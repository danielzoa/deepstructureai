from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["memory"])


@router.get("/memory")
def memory():
    return service.memory()
