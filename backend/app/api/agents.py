from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["agents"])


@router.get("/agents")
def agents():
    return service.agents()
