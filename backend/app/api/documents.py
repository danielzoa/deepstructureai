from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["documents"])


@router.get("/documents")
def documents():
    return service.documents()
