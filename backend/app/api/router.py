from fastapi import APIRouter

from app.schemas.chat import RouterTestRequest
from app.services.router_service import multi_ai

router = APIRouter(tags=["router"])


@router.get("/router/status")
def router_status():
    return multi_ai.status()


@router.post("/router/test")
def router_test(request: RouterTestRequest):
    status = multi_ai.status()
    mode = multi_ai.router.normalize_task(request.mode)
    route = status["activeRoutes"].get(mode, status["activeRoutes"].get("chat", ["mock"]))
    if request.dryRun:
        return {
            "mode": mode,
            "model": route[0] if route else "mock",
            "chain": route,
            "dryRun": True,
        }
    result = multi_ai.generate(request.message, mode, request.model)
    return {
        "mode": mode,
        "model": result.model,
        "answer": result.answer,
        "warnings": result.warnings,
        "dryRun": False,
    }
