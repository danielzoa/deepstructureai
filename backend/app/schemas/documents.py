from pydantic import BaseModel, Field


class DocumentImportRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    contentBase64: str = Field(..., min_length=1)


class DocumentImportResponse(BaseModel):
    name: str
    path: str
    size: int
    imported: bool


class DocumentReadResponse(BaseModel):
    name: str
    path: str
    size: int
    suffix: str
    content: str
    truncated: bool
    readable: bool
    warning: str = ""
