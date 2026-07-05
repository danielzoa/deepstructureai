from fastapi import APIRouter

from app.services.deepstructure_service import service

router = APIRouter(tags=["graph"])


@router.get("/summary")
def summary():
    return service.summary()


@router.get("/graph")
def graph():
    return service.graph()


@router.get("/graph/stats")
def graph_stats():
    return service.graph_stats()
