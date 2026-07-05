import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.api import activity, agents, chat, documents, graph, health, lab, memory, models, router


def _cors_origins() -> list[str]:
    raw = os.getenv("FRONTEND_ORIGINS") or os.getenv("FRONTEND_URL") or ""
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    local_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    merged = [*local_origins, *origins]
    return list(dict.fromkeys(merged))


app = FastAPI(title="DeepStructureAI API", version="0.1.0-mvp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(lab.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(router.router, prefix="/api")
