from pydantic import BaseModel


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    output: str
    blocked: bool = False
    warnings: list[str] = []
