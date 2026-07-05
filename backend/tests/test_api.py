from pathlib import Path
import sys

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app


client = TestClient(app)


def test_health_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_summary_ok():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "relations" in data


def test_chat_without_key_does_not_break(monkeypatch):
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    response = client.post(
        "/api/chat",
        json={"message": "Teste", "mode": "chat", "model": "glm"},
    )
    assert response.status_code == 200
    assert response.json()["answer"]


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
