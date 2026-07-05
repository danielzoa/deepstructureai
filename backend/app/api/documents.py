from fastapi import APIRouter, HTTPException

from app.schemas.documents import DocumentImportRequest, DocumentImportResponse, DocumentReadResponse
from app.services.deepstructure_service import service

router = APIRouter(tags=["documents"])


@router.get("/documents")
def documents():
    return service.documents()


@router.post("/documents/import", response_model=DocumentImportResponse)
def import_document(request: DocumentImportRequest):
    try:
        return service.import_document(request.name, request.contentBase64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/documents/read", response_model=DocumentReadResponse)
def read_document(path: str):
    try:
        return service.read_document(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
