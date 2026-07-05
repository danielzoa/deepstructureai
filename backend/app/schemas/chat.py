from typing import Literal

from pydantic import BaseModel, Field


ChatMode = Literal[
    "auto",
    "chat",
    "fast",
    "document",
    "critic",
    "code",
    "lab",
    "offline",
    "research",
    "writer",
]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    mode: ChatMode = "chat"
    model: str | None = "auto"


class ChatResponse(BaseModel):
    answer: str
    model: str
    mode: ChatMode
    sources: list[str] = []
    warnings: list[str] = []


class RouterTestRequest(BaseModel):
    message: str = "Responda apenas: ok"
    mode: ChatMode = "chat"
    model: str | None = "auto"
    dryRun: bool = True
