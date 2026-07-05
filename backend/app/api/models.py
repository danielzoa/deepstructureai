from fastapi import APIRouter

from app.services.router_service import multi_ai

router = APIRouter(tags=["models"])


@router.get("/models")
def models():
    return multi_ai.models()
