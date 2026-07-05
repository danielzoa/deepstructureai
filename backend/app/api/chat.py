from fastapi import APIRouter

from app.schemas.chat import ChatHistoryResponse, ChatRequest, ChatResponse, ClearChatResponse
from app.schemas.common import CommandRequest, CommandResponse
from app.services.deepstructure_service import service
from app.services.router_service import multi_ai

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = multi_ai.generate(request.message, request.mode, request.model)
    service.record_chat_exchange(request.message, result.answer, result.model, request.mode)
    return ChatResponse(
        answer=result.answer,
        model=result.model,
        mode=request.mode,
        sources=[],
        warnings=result.warnings,
    )


@router.get("/chat/history", response_model=ChatHistoryResponse)
def chat_history():
    return ChatHistoryResponse(messages=service.chat_history())


@router.delete("/chat/history", response_model=ClearChatResponse)
def clear_chat_history():
    return ClearChatResponse(**service.clear_chat_history())


@router.post("/command", response_model=CommandResponse)
def command(request: CommandRequest):
    response = service.run_command(request.command)
    service.record_activity(f"Comando executado: {request.command[:80]}")
    return response
