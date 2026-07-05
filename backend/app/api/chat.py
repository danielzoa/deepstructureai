from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import CommandRequest, CommandResponse
from app.services.deepstructure_service import service
from app.services.router_service import multi_ai

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = multi_ai.generate(request.message, request.mode, request.model)
    return ChatResponse(
        answer=result.answer,
        model=result.model,
        mode=request.mode,
        sources=[],
        warnings=result.warnings,
    )


@router.post("/command", response_model=CommandResponse)
def command(request: CommandRequest):
    return service.run_command(request.command)
