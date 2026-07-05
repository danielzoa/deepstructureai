from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return service.health()


@router.get("/about")
def about():
    return service.about()
