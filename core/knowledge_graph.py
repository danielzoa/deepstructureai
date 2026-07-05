import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from core.config import ROOT_DIR
from core.moltbook_gateway import PublicContentPolicy


class KnowledgeGraph:
    """Persistent scientific graph with provenance and legacy commands."""

    def __init__(self, llm=None, database=None, legacy_file=None):
        self.llm = llm
        self.database = Path(database or ROOT_DIR / "data" / "knowledge_graph.db")
        self.legacy_file = Path(
            legacy_file or ROOT_DIR / "data" / "knowledge_graph.json"
        )
        self.policy = PublicContentPolicy()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        if database is None:
            self._migrate_legacy_json()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self):
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS graph_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content_hash TEXT NOT NULL UNIQUE,
                    ingested_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canonical_name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS graph_aliases (
                    alias TEXT PRIMARY KEY,
                    node_id INTEGER NOT NULL REFERENCES graph_nodes(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS graph_node_sources (
                    node_id INTEGER NOT NULL REFERENCES graph_nodes(id)
                        ON DELETE CASCADE,
                    provenance_id INTEGER NOT NULL REFERENCES graph_sources(id)
                        ON DELETE CASCADE,
                    confidence REAL NOT NULL,
                    description TEXT NOT NULL,
                    PRIMARY KEY (node_id, provenance_id)
                );

                CREATE TABLE IF NOT EXISTS graph_edges (
                    id INTEGER PRIMARY KEY,
                    source_node_id INTEGER NOT NULL REFERENCES graph_nodes(id)
                        ON DELETE CASCADE,
                    relation TEXT NOT NULL,
                    target_node_id INTEGER NOT NULL REFERENCES graph_nodes(id)
                        ON DELETE CASCADE,
                    description TEXT NOT NULL DEFAULT '',
                    evidence TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL,
                    provenance_id INTEGER NOT NULL REFERENCES graph_sources(id)
                        ON DELETE CASCADE,
                    created_at TEXT NOT NULL,
                    UNIQUE (
                        source_node_id, relation, target_node_id, provenance_id
                    )
                );
                """
            )

    @staticmethod
    def _normalize(value):
        value = unicodedata.normalize("NFKD", str(value))
        value = "".join(
            character
            for character in value
            if not unicodedata.combining(character)
        )
        value = re.sub(r"[^\w\s]", " ", value)
        return " ".join(value.casefold().split())

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def _upsert_node(
        self,
        connection,
        name,
        node_type="concept",
        description="",
        confidence=None,
        aliases=None,
    ):
        canonical = self._normalize(name)
        row = connection.execute(
            "SELECT id FROM graph_nodes WHERE canonical_name = ?",
            (canonical,),
        ).fetchone()
        if row:
            node_id = row["id"]
            connection.execute(
                """
                UPDATE graph_nodes
                SET node_type = CASE
                        WHEN node_type = 'concept' THEN ?
                        ELSE node_type
                    END,
                    description = CASE
                        WHEN description = '' THEN ?
                        ELSE description
                    END,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    node_type or "concept",
                    description or "",
                    self._now(),
                    node_id,
                ),
            )
        else:
            timestamp = self._now()
            cursor = connection.execute(
                """
                INSERT INTO graph_nodes (
                    canonical_name, display_name, node_type, description,
                    confidence, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    canonical,
                    str(name).strip(),
                    node_type or "concept",
                    description or "",
                    confidence if confidence is not None else 0.5,
                    timestamp,
                    timestamp,
                ),
            )
            node_id = cursor.lastrowid

        all_aliases = {str(name).strip(), *(aliases or [])}
        for alias in all_aliases:
            normalized_alias = self._normalize(alias)
            if normalized_alias:
                connection.execute(
                    """
                    INSERT INTO graph_aliases (alias, node_id)
                    VALUES (?, ?)
                    ON CONFLICT(alias) DO UPDATE SET node_id = excluded.node_id
                    """,
                    (normalized_alias, node_id),
                )
        return node_id

    def _node_by_name(self, connection, name):
        normalized = self._normalize(name)
        return connection.execute(
            """
            SELECT n.*
            FROM graph_nodes n
            LEFT JOIN graph_aliases a ON a.node_id = n.id
            WHERE n.canonical_name = ? OR a.alias = ?
            ORDER BY CASE WHEN n.canonical_name = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (normalized, normalized, normalized),
        ).fetchone()

    def _migrate_legacy_json(self):
        if not self.legacy_file.exists():
            return
        with self._connect() as connection:
            already_migrated = connection.execute(
                """
                SELECT id FROM graph_sources
                WHERE source_type = 'legacy'
                  AND source_id = 'knowledge_graph.json'
                """
            ).fetchone()

        try:
            data = json.loads(self.legacy_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not data.get("nodes"):
            return

        content_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        with self._connect() as connection:
            if already_migrated:
                provenance_id = already_migrated["id"]
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO graph_sources (
                        source_type, source_id, title, content_hash, ingested_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "legacy",
                        "knowledge_graph.json",
                        "Grafo manual legado",
                        content_hash,
                        self._now(),
                    ),
                )
                provenance_id = cursor.lastrowid
            node_ids = {}
            for node_id, node in data.get("nodes", {}).items():
                database_id = self._upsert_node(
                    connection,
                    node.get("label") or node_id,
                    node.get("type", "concept"),
                    node.get("description", ""),
                    aliases=[node_id],
                )
                node_ids[node_id] = database_id
                connection.execute(
                    """
                    INSERT OR IGNORE INTO graph_node_sources
                    (node_id, provenance_id, confidence, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        database_id,
                        provenance_id,
                        0.8,
                        node.get("description", ""),
                    ),
                )
            for edge in data.get("edges", []):
                source = node_ids.get(edge.get("source"))
                target = node_ids.get(edge.get("target"))
                if source and target:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO graph_edges (
                            source_node_id, relation, target_node_id,
                            description, evidence, confidence,
                            provenance_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            source,
                            edge.get("relation", "related_to"),
                            target,
                            "",
                            "",
                            0.8,
                            provenance_id,
                            self._now(),
                        ),
                    )

    def ingest(
        self,
        content,
        title="Documento",
        source_type="document",
        source_id=None,
    ):
        content = self.policy.validate_outbound(content)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        source_id = str(source_id or content_hash)

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM graph_sources WHERE content_hash = ?",
                (content_hash,),
            ).fetchone()
            if existing:
                return {
                    "created": False,
                    "source_id": existing["id"],
                    **self.stats(),
                }

        if self.llm is None:
            raise RuntimeError(
                "Extração automática do grafo requer um modelo de linguagem."
            )
        system_prompt = """
Extraia um grafo científico do texto. Responda somente JSON com:
entities: name, type, description, aliases, confidence;
relations: source, relation, target, description, evidence, confidence.
Preserve o estatuto epistêmico: hipótese não é fato ou prova.
"""
        raw = self.llm.ask(system_prompt, f"Título: {title}\n\n{content}")
        extracted = json.loads(raw)
        entities = extracted.get("entities", [])
        relations = extracted.get("relations", [])

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO graph_sources (
                    source_type, source_id, title, content_hash, ingested_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    source_type,
                    source_id,
                    title,
                    content_hash,
                    self._now(),
                ),
            )
            provenance_id = cursor.lastrowid
            node_ids = {}
            for entity in entities:
                name = entity["name"].strip()
                node_id = self._upsert_node(
                    connection,
                    name,
                    entity.get("type", "concept"),
                    entity.get("description", ""),
                    entity.get("confidence"),
                    entity.get("aliases", []),
                )
                node_ids[self._normalize(name)] = node_id
                connection.execute(
                    """
                    INSERT OR IGNORE INTO graph_node_sources
                    (node_id, provenance_id, confidence, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        node_id,
                        provenance_id,
                        entity.get("confidence", 0.5),
                        entity.get("description", ""),
                    ),
                )

            for relation in relations:
                source_name = relation["source"].strip()
                target_name = relation["target"].strip()
                source_node = node_ids.get(self._normalize(source_name))
                target_node = node_ids.get(self._normalize(target_name))
                if source_node is None:
                    source_node = self._upsert_node(connection, source_name)
                if target_node is None:
                    target_node = self._upsert_node(connection, target_name)
                for node_id in (source_node, target_node):
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO graph_node_sources
                        (node_id, provenance_id, confidence, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (node_id, provenance_id, 0.5, ""),
                    )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO graph_edges (
                        source_node_id, relation, target_node_id,
                        description, evidence, confidence, provenance_id,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        source_node,
                        relation.get("relation", "related_to"),
                        target_node,
                        relation.get("description", ""),
                        relation.get("evidence", ""),
                        relation.get("confidence", 0.5),
                        provenance_id,
                        self._now(),
                    ),
                )

        return {"created": True, "source_id": provenance_id, **self.stats()}

    @staticmethod
    def _node_dict(row):
        return {
            "id": row["id"],
            "display_name": row["display_name"],
            "node_type": row["node_type"],
            "description": row["description"],
            "confidence": row["confidence"],
        }

    def search(self, query, limit=10):
        terms = {
            term
            for term in re.findall(r"[\w-]+", self._normalize(query))
            if len(term) > 2 or re.fullmatch(r"[a-z]\d+", term)
        }
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT n.*, GROUP_CONCAT(a.alias, ' ') AS aliases
                FROM graph_nodes n
                LEFT JOIN graph_aliases a ON a.node_id = n.id
                GROUP BY n.id
                """
            ).fetchall()

        ranked = []
        normalized_query = self._normalize(query)
        for row in rows:
            searchable = self._normalize(
                " ".join(
                    [
                        row["display_name"],
                        row["node_type"],
                        row["description"],
                        row["aliases"] or "",
                    ]
                )
            )
            searchable_terms = set(re.findall(r"[\w-]+", searchable))
            score = sum(
                3 if term in searchable_terms else 1
                for term in terms
                if term in searchable
            )
            if normalized_query and normalized_query in searchable:
                score += 3
            if score:
                ranked.append((score, row))
        ranked.sort(key=lambda item: (-item[0], item[1]["display_name"].casefold()))
        return [self._node_dict(row) for _, row in ranked[:limit]]

    def neighbors(self, name):
        with self._connect() as connection:
            node = self._node_by_name(connection, name)
            if node is None:
                return None
            edges = connection.execute(
                """
                SELECT e.*, s.display_name AS source_name,
                       t.display_name AS target_name,
                       p.title AS provenance_title
                FROM graph_edges e
                JOIN graph_nodes s ON s.id = e.source_node_id
                JOIN graph_nodes t ON t.id = e.target_node_id
                JOIN graph_sources p ON p.id = e.provenance_id
                WHERE e.source_node_id = ? OR e.target_node_id = ?
                ORDER BY e.id
                """,
                (node["id"], node["id"]),
            ).fetchall()
        return {
            "node": self._node_dict(node),
            "edges": [
                {
                    "source": edge["source_name"],
                    "relation": edge["relation"],
                    "target": edge["target_name"],
                    "description": edge["description"],
                    "evidence": edge["evidence"],
                    "confidence": edge["confidence"],
                    "provenance_title": edge["provenance_title"],
                }
                for edge in edges
            ],
        }

    def shortest_path(self, source, target):
        with self._connect() as connection:
            source_node = self._node_by_name(connection, source)
            target_node = self._node_by_name(connection, target)
            if source_node is None or target_node is None:
                return None
            rows = connection.execute(
                "SELECT source_node_id, target_node_id FROM graph_edges"
            ).fetchall()
            nodes = {
                row["id"]: row
                for row in connection.execute("SELECT * FROM graph_nodes").fetchall()
            }

        adjacency = {}
        for row in rows:
            adjacency.setdefault(row["source_node_id"], set()).add(
                row["target_node_id"]
            )
            adjacency.setdefault(row["target_node_id"], set()).add(
                row["source_node_id"]
            )
        queue = deque([(source_node["id"], [source_node["id"]])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == target_node["id"]:
                return [self._node_dict(nodes[node_id]) for node_id in path]
            if current in visited:
                continue
            visited.add(current)
            for neighbor in adjacency.get(current, set()):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        return []

    def context(self, query, limit=8):
        matches = self.search(query, limit=limit)
        if not matches:
            return "Nenhuma relação relevante foi encontrada no grafo."

        identifiers = set(
            re.findall(r"\b[a-z]\d+\b", self._normalize(query))
        )
        exact_identifier_matches = [
            node
            for node in matches
            if self._normalize(node["display_name"]) in identifiers
        ]
        if exact_identifier_matches:
            matches = exact_identifier_matches

        selected = {node["display_name"] for node in matches}
        relations = []
        frontier = set(selected)
        visited = set()
        depth = 2 if exact_identifier_matches else 1
        for _ in range(depth):
            next_frontier = set()
            for name in frontier - visited:
                neighborhood = self.neighbors(name)
                if neighborhood is None:
                    continue
                visited.add(name)
                for edge in neighborhood["edges"]:
                    selected.add(edge["source"])
                    selected.add(edge["target"])
                    next_frontier.add(edge["source"])
                    next_frontier.add(edge["target"])
                    signature = (
                        edge["source"],
                        edge["relation"],
                        edge["target"],
                        edge["provenance_title"],
                    )
                    if signature not in relations:
                        relations.append(signature)
            frontier = next_frontier

        with self._connect() as connection:
            node_rows = [
                self._node_by_name(connection, name)
                for name in sorted(selected, key=str.casefold)
            ]
        lines = ["Nós relevantes:"]
        for node in node_rows:
            description = node["description"].strip()
            lines.append(
                f"- {node['display_name']} [{node['node_type']}]"
                + (f": {description}" if description else "")
            )
        if relations:
            lines.append("\nRelações:")
            for source, relation, target, provenance in relations:
                lines.append(
                    f"- {source} --{relation}--> {target} (fonte: {provenance})"
                )
        return "\n".join(lines)

    def stats(self):
        with self._connect() as connection:
            return {
                "nodes": connection.execute(
                    "SELECT COUNT(*) FROM graph_nodes"
                ).fetchone()[0],
                "edges": connection.execute(
                    "SELECT COUNT(*) FROM graph_edges"
                ).fetchone()[0],
                "sources": connection.execute(
                    "SELECT COUNT(*) FROM graph_sources"
                ).fetchone()[0],
            }

    def verify_integrity(self):
        with self._connect() as connection:
            violations = connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()
        return {"valid": not violations, "violations": len(violations)}

    def export_data(self):
        with self._connect() as connection:
            nodes = [
                self._node_dict(row)
                for row in connection.execute(
                    "SELECT * FROM graph_nodes ORDER BY id"
                ).fetchall()
            ]
            edges = [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT s.display_name AS source, e.relation,
                           t.display_name AS target, e.description,
                           e.evidence, e.confidence,
                           p.title AS provenance_title
                    FROM graph_edges e
                    JOIN graph_nodes s ON s.id = e.source_node_id
                    JOIN graph_nodes t ON t.id = e.target_node_id
                    JOIN graph_sources p ON p.id = e.provenance_id
                    ORDER BY e.id
                    """
                ).fetchall()
            ]
        return {"nodes": nodes, "edges": edges}

    def export_json(self, filename="knowledge_graph.json"):
        path = ROOT_DIR / "output" / "graph" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.export_data(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def export_graphml(self, filename="knowledge_graph.graphml"):
        data = self.export_data()
        namespace = "http://graphml.graphdrawing.org/xmlns"
        ET.register_namespace("", namespace)
        root = ET.Element(f"{{{namespace}}}graphml")
        graph = ET.SubElement(
            root,
            f"{{{namespace}}}graph",
            edgedefault="directed",
        )
        ids = {}
        for node in data["nodes"]:
            graph_id = f"n{node['id']}"
            ids[node["display_name"]] = graph_id
            ET.SubElement(graph, f"{{{namespace}}}node", id=graph_id)
        for index, edge in enumerate(data["edges"]):
            ET.SubElement(
                graph,
                f"{{{namespace}}}edge",
                id=f"e{index}",
                source=ids[edge["source"]],
                target=ids[edge["target"]],
            )
        path = ROOT_DIR / "output" / "graph" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
        return path

    # Compatibility with the original interactive graph commands.
    def add_node(self, node_id, label=None, node_type="concept", description=""):
        with self._connect() as connection:
            if self._node_by_name(connection, node_id):
                return f"Nó já existe: {node_id}"
            self._upsert_node(
                connection,
                label or node_id,
                node_type,
                description,
                aliases=[node_id],
            )
        return f"Nó criado: {node_id}"

    def add_edge(self, source, relation, target):
        source = source.strip()
        target = target.strip()
        relation = relation.strip()
        with self._connect() as connection:
            source_node = self._node_by_name(connection, source)
            target_node = self._node_by_name(connection, target)
            if source_node is None:
                source_id = self._upsert_node(connection, source)
            else:
                source_id = source_node["id"]
            if target_node is None:
                target_id = self._upsert_node(connection, target)
            else:
                target_id = target_node["id"]
            provenance = connection.execute(
                """
                SELECT id FROM graph_sources
                WHERE source_type = 'manual' AND source_id = 'interactive'
                """,
            ).fetchone()
            if provenance is None:
                cursor = connection.execute(
                    """
                    INSERT INTO graph_sources (
                        source_type, source_id, title, content_hash, ingested_at
                    ) VALUES (
                        'manual', 'interactive', 'Entrada manual',
                        'manual-interactive', ?
                    )
                    """,
                    (self._now(),),
                )
                provenance_id = cursor.lastrowid
            else:
                provenance_id = provenance["id"]
            connection.execute(
                """
                INSERT OR IGNORE INTO graph_edges (
                    source_node_id, relation, target_node_id,
                    description, evidence, confidence,
                    provenance_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    relation,
                    target_id,
                    "",
                    "",
                    0.8,
                    provenance_id,
                    self._now(),
                ),
            )
        return f"Relação criada: {source} --{relation}--> {target}"

    def show_node(self, node_id):
        neighborhood = self.neighbors(node_id)
        if neighborhood is None:
            return f"Nó não encontrado: {node_id}"
        node = neighborhood["node"]
        lines = [
            f"Nó: {node['display_name']}",
            f"Tipo: {node['node_type']}",
            f"Descrição: {node['description']}",
            "",
            "Relações:",
        ]
        lines.extend(
            f"- {edge['source']} --{edge['relation']}--> {edge['target']}"
            for edge in neighborhood["edges"]
        )
        if not neighborhood["edges"]:
            lines.append("- nenhuma")
        return "\n".join(lines)

    def related(self, node_id):
        neighborhood = self.neighbors(node_id)
        if neighborhood is None:
            return f"Nó não encontrado: {node_id}"
        if not neighborhood["edges"]:
            return f"Relacionados a {node_id}:\n\nNenhuma relação encontrada."
        return "\n".join(
            [f"Relacionados a {node_id}:", ""]
            + [
                f"{edge['source']} --{edge['relation']}--> {edge['target']}"
                for edge in neighborhood["edges"]
            ]
        )

    def path(self, source, target):
        nodes = self.shortest_path(source, target)
        if nodes is None:
            return "Origem ou destino inexistente."
        if not nodes:
            return "Nenhum caminho encontrado."
        return " -> ".join(node["display_name"] for node in nodes)

    def summary(self):
        statistics = self.stats()
        return (
            "\nKnowledge Graph\n\n"
            f"Nós: {statistics['nodes']}\n"
            f"Relações: {statistics['edges']}\n"
            f"Fontes: {statistics['sources']}\n"
        )
