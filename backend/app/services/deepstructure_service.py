import json
import os
import sqlite3
import base64
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: Path, fallback: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def _file_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    if path.is_file():
        return round(path.stat().st_size / (1024 * 1024), 1)
    total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return round(total / (1024 * 1024), 1)


class DeepStructureService:
    allowed_document_suffixes = {".pdf", ".tex", ".md", ".json", ".txt"}
    max_import_bytes = 10 * 1024 * 1024

    dangerous_tokens = {
        "rm ",
        "del ",
        "remove-item",
        "format",
        "shutdown",
        "reset --hard",
        "drop table",
    }

    def project_root(self):
        return PROJECT_ROOT

    def about(self):
        return {
            "name": "DeepStructureAI",
            "description": "NTG Research Assistant com backend FastAPI e frontend web MVP.",
            "version": "0.1.0-mvp",
        }

    def health(self):
        return {
            "status": "ok",
            "project": "DeepStructureAI",
            "glmConfigured": bool(os.getenv("ZAI_API_KEY")),
            "ollamaAvailable": self._ollama_available(),
        }

    def _ollama_available(self):
        url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        base_url = url.split("/api/")[0]
        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=0.8)
            return response.status_code == 200
        except Exception:
            return False

    def models(self):
        env_map = {
            "glm": bool(os.getenv("ZAI_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "claude": bool(os.getenv("ANTHROPIC_API_KEY")),
            "ollama": self._ollama_available(),
            "deepseek": self._ollama_available(),
            "qwen": self._ollama_available(),
            "hermes": self._ollama_available(),
        }
        labels = {
            "glm": "GLM / Z.AI",
            "ollama": "Ollama Local",
            "openai": "OpenAI",
            "claude": "Claude",
            "deepseek": "DeepSeek",
            "qwen": "Qwen",
            "hermes": "Hermes",
        }
        return [
            {"id": key, "name": labels[key], "available": env_map[key]}
            for key in labels
        ]

    def agents(self):
        return [
            {"name": "Planner", "role": "Planejamento", "status": "online"},
            {"name": "Researcher", "role": "Pesquisa", "status": "online"},
            {"name": "Critic", "role": "Crítica", "status": "standby"},
            {"name": "Writer", "role": "Escrita", "status": "online"},
            {"name": "Reviewer", "role": "Revisão", "status": "standby"},
        ]

    def summary(self):
        graph = self.graph()
        documents = self.documents()
        return {
            "nodes": len(graph["nodes"]),
            "relations": len(graph["edges"]),
            "clusters": max(3, min(17, len(graph["nodes"]) // 2)),
            "concepts": max(8, len(graph["nodes"]) + len(documents)),
            "semanticMemorySize": _file_size_mb(PROJECT_ROOT / "data" / "semantic_memory.db"),
            "scientificMemorySize": _file_size_mb(PROJECT_ROOT / "data" / "scientific_memory.json"),
            "laboratorySize": _file_size_mb(PROJECT_ROOT / "data" / "laboratory.db"),
            "documentsCount": len(documents),
        }

    def graph(self):
        for path in (
            PROJECT_ROOT / "data" / "knowledge_graph.json",
            PROJECT_ROOT / "output" / "graph" / "knowledge_graph.json",
        ):
            data = _read_json(path, None)
            normalized = self._normalize_graph(data)
            if normalized:
                return normalized
        return self._mock_graph()

    def _normalize_graph(self, data):
        if not isinstance(data, dict):
            return None
        raw_nodes = data.get("nodes") or []
        raw_edges = data.get("edges") or data.get("links") or []
        nodes = []
        for idx, node in enumerate(raw_nodes):
            if isinstance(node, dict):
                node_id = str(node.get("id") or node.get("name") or node.get("label") or idx)
                nodes.append({"id": node_id, "label": str(node.get("label") or node.get("name") or node_id)})
            else:
                nodes.append({"id": str(node), "label": str(node)})
        edges = []
        for edge in raw_edges:
            if isinstance(edge, dict):
                source = edge.get("source") or edge.get("from")
                target = edge.get("target") or edge.get("to")
                if source and target:
                    edges.append({"source": str(source), "target": str(target), "label": str(edge.get("label", ""))})
        if nodes:
            return {"nodes": nodes[:80], "edges": edges[:160]}
        return None

    def _mock_graph(self):
        labels = [
            "NTG",
            "Navier-Stokes 3D",
            "Vorticidade",
            "Pressão Anisotrópica",
            "Não Comutatividade",
            "Matéria Escura",
            "Rigidez Espectral",
            "Energia",
            "Transporte",
        ]
        nodes = [{"id": label.lower().replace(" ", "-"), "label": label} for label in labels]
        edges = [{"source": "ntg", "target": node["id"], "label": "relaciona"} for node in nodes[1:]]
        return {"nodes": nodes, "edges": edges}

    def graph_stats(self):
        graph = self.graph()
        return {
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "density": round(len(graph["edges"]) / max(1, len(graph["nodes"])), 2),
        }

    def memory(self):
        return [
            {"name": "Memória Semântica", "size": _file_size_mb(PROJECT_ROOT / "data" / "semantic_memory.db")},
            {"name": "Memória Científica", "size": _file_size_mb(PROJECT_ROOT / "data" / "scientific_memory.json")},
            {"name": "Knowledge Graph", "size": _file_size_mb(PROJECT_ROOT / "data" / "knowledge_graph.db")},
            {"name": "Laboratório", "size": _file_size_mb(PROJECT_ROOT / "data" / "laboratory.db")},
        ]

    def lab_status(self):
        lab_db = PROJECT_ROOT / "data" / "laboratory.db"
        evidence_count = 3
        tests_count = 2
        try:
            if lab_db.exists():
                with sqlite3.connect(lab_db) as conn:
                    tables = conn.execute("select name from sqlite_master where type='table'").fetchall()
                    tests_count = max(tests_count, len(tables))
        except Exception:
            pass
        return {
            "project": "Controle de Enstrofia em NS 3D",
            "hypothesis": "Ativa",
            "evidenceCount": evidence_count,
            "testsCount": tests_count,
            "progress": 68,
        }

    def documents(self):
        roots = [
            PROJECT_ROOT / "knowledge" / "NTG",
            PROJECT_ROOT / "knowledge" / "NTG" / "imports",
            PROJECT_ROOT / "output" / "pdf" / "articles",
            PROJECT_ROOT / "data",
        ]
        docs = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".pdf", ".tex", ".md", ".json", ".db"}:
                    docs.append(
                        {
                            "name": path.name,
                            "path": str(path.relative_to(PROJECT_ROOT)),
                            "size": path.stat().st_size,
                            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                        }
                    )
        return sorted(docs, key=lambda item: item["modified"], reverse=True)[:40]

    def import_document(self, name: str, content_base64: str):
        safe_name = Path(name).name.strip()
        suffix = Path(safe_name).suffix.lower()
        if not safe_name or suffix not in self.allowed_document_suffixes:
            raise ValueError("Tipo de documento não permitido.")

        try:
            content = base64.b64decode(content_base64, validate=True)
        except Exception as exc:
            raise ValueError("Conteúdo base64 inválido.") from exc

        if len(content) > self.max_import_bytes:
            raise ValueError("Documento excede o limite de 10 MB.")

        target_dir = PROJECT_ROOT / "knowledge" / "NTG" / "imports" / "web_uploads"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = self._unique_path(target_dir / safe_name)
        target.write_bytes(content)

        return {
            "name": target.name,
            "path": str(target.relative_to(PROJECT_ROOT)),
            "size": target.stat().st_size,
            "imported": True,
        }

    def _unique_path(self, path: Path):
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 2
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def activity(self):
        log_path = PROJECT_ROOT / "logs" / "agent.log"
        if log_path.exists():
            try:
                lines = [line.strip() for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
                return [{"time": "", "event": line[:120]} for line in lines[-8:]][::-1]
            except Exception:
                pass
        return [
            {"time": "10:45", "event": "Grafo atualizado"},
            {"time": "10:44", "event": "Evidência adicionada"},
            {"time": "10:43", "event": "Pesquisa concluída"},
            {"time": "10:42", "event": "PDF importado"},
        ]

    def run_command(self, command: str):
        normalized = command.strip().lower()
        if any(token in normalized for token in self.dangerous_tokens):
            return {"output": "Comando bloqueado por segurança.", "blocked": True, "warnings": ["dangerous_command"]}
        if normalized in {"/help", "help"}:
            payload = {
                "commands": [
                    "/about",
                    "/health",
                    "/team",
                    "/models",
                    "/documents",
                    "/activity",
                    "/graph stats",
                    "/graph build",
                    "/semantic search",
                    "/validate idea",
                    "/search termo",
                ],
                "hint": "Use o chat para perguntas abertas e as ferramentas para estado do projeto.",
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/about", "about"}:
            return {"output": json.dumps(self.about(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/health", "health"}:
            return {"output": json.dumps(self.health(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/models", "models"}:
            return {"output": json.dumps(self.models(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/team", "team"}:
            return {"output": json.dumps(self.agents(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/documents", "documents"}:
            return {"output": json.dumps(self.documents()[:10], ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/activity", "activity"}:
            return {"output": json.dumps(self.activity(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/lab status", "/lab start", "lab status", "lab start"}:
            return {"output": json.dumps(self.lab_status(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/graph stats", "graph stats"}:
            return {"output": json.dumps(self.graph_stats(), ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/benchmark", "benchmark"}:
            payload = {
                "status": "ready",
                "scope": "MVP",
                "checks": ["health", "router", "summary", "graph", "chat fallback"],
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/import_ntg", "import_ntg"}:
            payload = {
                "status": "available",
                "target": "knowledge/NTG/imports/web_uploads",
                "allowed": sorted(self.allowed_document_suffixes),
                "documentsCount": len(self.documents()),
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/graph build", "graph build"}:
            payload = {
                "status": "ready",
                "message": "Resumo do grafo recalculado a partir dos dados disponíveis.",
                **self.graph_stats(),
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": ["graph_build_summary"]}
        if normalized.startswith("/search ") or normalized.startswith("search "):
            term = normalized.split(" ", 1)[1].strip()
            docs = [doc for doc in self.documents() if term in doc["name"].lower() or term in doc.get("path", "").lower()]
            nodes = [node for node in self.graph()["nodes"] if term in node["label"].lower() or term in node["id"].lower()]
            payload = {
                "term": term,
                "documents": docs[:10],
                "nodes": nodes[:10],
                "total": len(docs) + len(nodes),
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": []}
        if normalized in {"/semantic search", "semantic search"}:
            payload = {
                "status": "ready",
                "memorySizeMb": _file_size_mb(PROJECT_ROOT / "data" / "semantic_memory.db"),
                "message": "Busca semântica conectada em modo resumo no MVP.",
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": ["semantic_search_mock"]}
        if normalized in {"/validate idea", "validate idea"}:
            payload = {
                "status": "ready",
                "validator": "DeepSeek > GLM > Gemini > Ollama/mock",
                "message": "Use o modo Crítico ou Laboratório para validar uma hipótese.",
            }
            return {"output": json.dumps(payload, ensure_ascii=False, indent=2), "blocked": False, "warnings": ["validator_hint"]}
        return {
            "output": "Comando reconhecido no MVP. A execução profunda será conectada ao CLI em uma próxima etapa.",
            "blocked": False,
            "warnings": ["demo_command"],
        }


service = DeepStructureService()
