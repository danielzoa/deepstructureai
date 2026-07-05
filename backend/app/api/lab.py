from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["lab"])


@router.get("/lab/status")
def lab_status():
    return service.lab_status()
