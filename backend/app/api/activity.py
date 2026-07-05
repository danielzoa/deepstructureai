from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["activity"])


@router.get("/activity")
def activity():
    return service.activity()
