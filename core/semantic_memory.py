import hashlib
import json
import math
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

from core.config import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    SEMANTIC_MEMORY_FILE,
)
from core.moltbook_gateway import PublicContentPolicy, SecurityViolation


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        client=None,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    ):
        self.client = client or OpenAI()
        self.model = model
        self.dimensions = dimensions

    def embed(self, text):
        response = self.client.embeddings.create(
            model=self.model,
            input=text.replace("\n", " "),
            dimensions=self.dimensions,
            encoding_format="float",
        )
        return response.data[0].embedding


class SemanticMemory:
    CATEGORIES = {"fact", "preference", "insight", "decision", "hypothesis"}
    MAX_CONTENT_LENGTH = 4000

    def __init__(
        self,
        database=SEMANTIC_MEMORY_FILE,
        embedding_provider=None,
    ):
        self.database = Path(database)
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_provider = embedding_provider
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    project TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    importance INTEGER NOT NULL DEFAULT 3,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    last_accessed TEXT,
                    UNIQUE(project, fingerprint)
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(semantic_memories)"
                ).fetchall()
            }
            migrations = {
                "status": "TEXT NOT NULL DEFAULT 'active'",
                "importance": "INTEGER NOT NULL DEFAULT 3",
                "access_count": "INTEGER NOT NULL DEFAULT 0",
                "last_accessed": "TEXT",
            }
            for name, definition in migrations.items():
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE semantic_memories "
                        f"ADD COLUMN {name} {definition}"
                    )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_semantic_project "
                "ON semantic_memories(project)"
            )

    @staticmethod
    def _fingerprint(content):
        normalized = " ".join(content.casefold().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _check_sensitive(content):
        for pattern in (
            *PublicContentPolicy.SECRET_PATTERNS,
            *PublicContentPolicy.PRIVATE_PATTERNS,
        ):
            if pattern.search(content):
                raise SecurityViolation(
                    "Memória bloqueada: possível segredo ou dado pessoal."
                )

    def _provider(self):
        if self.embedding_provider is None:
            raise RuntimeError("Provedor de embeddings não configurado.")
        return self.embedding_provider

    def remember(
        self,
        content,
        project="Geral",
        category="insight",
        source="user",
        metadata=None,
    ):
        content = content.strip()
        if not content:
            raise ValueError("A memória não pode estar vazia.")
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise ValueError("A memória excede 4.000 caracteres.")
        if category not in self.CATEGORIES:
            raise ValueError(f"Categoria inválida: {category}")
        self._check_sensitive(content)

        fingerprint = self._fingerprint(content)
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id, status FROM semantic_memories "
                "WHERE project = ? AND fingerprint = ?",
                (project, fingerprint),
            ).fetchone()
            if existing:
                if existing["status"] == "archived":
                    connection.execute(
                        "UPDATE semantic_memories SET status = 'active' "
                        "WHERE id = ?",
                        (existing["id"],),
                    )
                return {
                    "id": existing["id"],
                    "created": False,
                    "restored": existing["status"] == "archived",
                }

        vector = self._provider().embed(content)
        if not vector:
            raise RuntimeError("O provedor retornou um embedding vazio.")
        model = getattr(self.embedding_provider, "model", "custom")
        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO semantic_memories (
                    content, project, category, source, embedding,
                    embedding_model, fingerprint, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    content,
                    project,
                    category,
                    source,
                    json.dumps(vector),
                    model,
                    fingerprint,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    created_at,
                ),
            )
            return {"id": cursor.lastrowid, "created": True}

    @staticmethod
    def _cosine(left, right):
        if len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def _tokens(text):
        return {
            token
            for token in re.findall(r"\w+", text.casefold())
            if len(token) > 2
        }

    def search(self, query, project="Geral", limit=5, min_score=0.2):
        query = query.strip()
        if not query or self.count(project=project, include_general=True) == 0:
            return []

        query_vector = self._provider().embed(query[: self.MAX_CONTENT_LENGTH])
        query_tokens = self._tokens(query)
        projects = ("Geral",) if project == "Geral" else ("Geral", project)
        placeholders = ",".join("?" for _ in projects)

        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM semantic_memories "
                f"WHERE project IN ({placeholders}) AND status = 'active'",
                projects,
            ).fetchall()

        results = []
        accessed_ids = []
        for row in rows:
            vector = json.loads(row["embedding"])
            semantic_score = self._cosine(query_vector, vector)
            memory_tokens = self._tokens(row["content"])
            lexical_score = (
                len(query_tokens & memory_tokens) / len(query_tokens)
                if query_tokens
                else 0.0
            )
            score = 0.85 * semantic_score + 0.15 * lexical_score
            if score >= min_score:
                results.append(
                    {
                        "id": row["id"],
                        "content": row["content"],
                        "project": row["project"],
                        "category": row["category"],
                        "source": row["source"],
                        "score": round(score, 4),
                        "created_at": row["created_at"],
                        "importance": row["importance"],
                        "metadata": json.loads(row["metadata"]),
                    }
                )
        selected = sorted(
            results,
            key=lambda item: (
                item["score"],
                item["importance"],
            ),
            reverse=True,
        )[:limit]
        accessed_ids = [item["id"] for item in selected]
        if accessed_ids:
            placeholders = ",".join("?" for _ in accessed_ids)
            with self._connect() as connection:
                connection.execute(
                    f"UPDATE semantic_memories "
                    f"SET access_count = access_count + 1, last_accessed = ? "
                    f"WHERE id IN ({placeholders})",
                    (datetime.now(timezone.utc).isoformat(), *accessed_ids),
                )
        return selected

    def list(self, project=None, limit=50, status="active"):
        query = (
            "SELECT id, content, project, category, source, created_at, "
            "status, importance, access_count, last_accessed "
            "FROM semantic_memories"
        )
        parameters = []
        conditions = []
        if project:
            conditions.append("project = ?")
            parameters.append(project)
        if status:
            conditions.append("status = ?")
            parameters.append(status)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id DESC LIMIT ?"
        parameters.append(limit)
        with self._connect() as connection:
            return [dict(row) for row in connection.execute(query, parameters)]

    def forget(self, memory_id):
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM semantic_memories WHERE id = ?",
                (int(memory_id),),
            )
            return cursor.rowcount == 1

    def archive(self, memory_ids):
        ids = [int(memory_id) for memory_id in memory_ids]
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        with self._connect() as connection:
            cursor = connection.execute(
                f"UPDATE semantic_memories SET status = 'archived' "
                f"WHERE id IN ({placeholders}) AND status = 'active'",
                ids,
            )
            return cursor.rowcount

    def restore(self, memory_id):
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE semantic_memories SET status = 'active' WHERE id = ?",
                (int(memory_id),),
            )
            return cursor.rowcount == 1

    def set_importance(self, memory_id, importance):
        importance = int(importance)
        if importance not in range(1, 6):
            raise ValueError("A importância deve estar entre 1 e 5.")
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE semantic_memories SET importance = ? WHERE id = ?",
                (importance, int(memory_id)),
            )
            return cursor.rowcount == 1

    def get(self, memory_id):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM semantic_memories WHERE id = ?",
                (int(memory_id),),
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["embedding"] = json.loads(result["embedding"])
        result["metadata"] = json.loads(result["metadata"])
        return result

    def active_with_vectors(self, project=None):
        query = "SELECT * FROM semantic_memories WHERE status = 'active'"
        parameters = []
        if project:
            query += " AND project = ?"
            parameters.append(project)
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["embedding"] = json.loads(item["embedding"])
            item["metadata"] = json.loads(item["metadata"])
            results.append(item)
        return results

    def count(self, project=None, include_general=False, status="active"):
        with self._connect() as connection:
            if project and include_general and project != "Geral":
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM semantic_memories "
                    "WHERE project IN ('Geral', ?) AND status = ?",
                    (project, status),
                ).fetchone()
            elif project:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM semantic_memories "
                    "WHERE project = ? AND status = ?",
                    (project, status),
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT COUNT(*) AS total FROM semantic_memories "
                    "WHERE status = ?",
                    (status,),
                ).fetchone()
        return row["total"]

    def stats(self):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT project, category, status, COUNT(*) AS total "
                "FROM semantic_memories GROUP BY project, category, status"
            ).fetchall()
        return {
            "total": self.count(),
            "archived": self.count(status="archived"),
            "groups": [dict(row) for row in rows],
        }
