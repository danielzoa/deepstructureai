from pathlib import Path
import sys

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app
from app.services.deepstructure_service import service
from core.models.zai_model import ZAIModel


client = TestClient(app)


def test_health_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_zai_openrouter_key_uses_openrouter_defaults(monkeypatch):
    monkeypatch.setenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")
    monkeypatch.setenv("ZAI_MODEL", "GLM-5.2")
    model = ZAIModel(api_key="sk-or-v1-test")
    assert model.base_url == "https://openrouter.ai/api/v1"
    assert model.model_name == "z-ai/glm-5.2"


def test_readiness_ok():
    response = client.get("/api/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "configuredModels" in data
    assert "warnings" in data
    assert data["uploadDirectoryExists"] is True


def test_summary_ok():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "relations" in data


def test_chat_without_key_does_not_break(monkeypatch):
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.setattr(service, "record_chat_exchange", lambda *args, **kwargs: None)
    response = client.post(
        "/api/chat",
        json={"message": "Teste", "mode": "chat", "model": "glm"},
    )
    assert response.status_code == 200
    assert response.json()["answer"]


def test_chat_history_endpoint():
    history = client.get("/api/chat/history")
    assert history.status_code == 200
    assert "messages" in history.json()


def test_graph_returns_nodes_and_edges():
    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_router_status_and_dry_run():
    status = client.get("/api/router/status")
    assert status.status_code == 200
    assert "activeRoutes" in status.json()

    test = client.post(
        "/api/router/test",
        json={"message": "ok", "mode": "critic", "dryRun": True},
    )
    assert test.status_code == 200
    assert "chain" in test.json()


def test_import_document(tmp_path):
    response = client.post(
        "/api/documents/import",
        json={
            "name": "teste_import.md",
            "contentBase64": "IyBUZXN0ZQo=",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] is True
    assert data["name"].startswith("teste_import")
    imported_path = BACKEND_ROOT.parent / data["path"]
    if imported_path.exists():
        imported_path.unlink()


def test_read_document_endpoint(tmp_path):
    response = client.post(
        "/api/documents/import",
        json={
            "name": "teste_read.md",
            "contentBase64": "IyBUZXN0ZQoKQ29udGV1ZG8gZG8gZG9jdW1lbnRvLgo=",
        },
    )
    assert response.status_code == 200
    data = response.json()

    read = client.get("/api/documents/read", params={"path": data["path"]})
    assert read.status_code == 200
    payload = read.json()
    assert payload["name"].startswith("teste_read")
    assert "Conteudo do documento" in payload["content"] or "Conteúdo do documento" in payload["content"]

    imported_path = BACKEND_ROOT.parent / data["path"]
    if imported_path.exists():
        imported_path.unlink()


def test_quick_commands_work():
    for command in ["/team", "/benchmark", "/graph build", "/semantic search", "/validate idea"]:
        response = client.post("/api/command", json={"command": command})
        assert response.status_code == 200
        assert response.json()["output"]
