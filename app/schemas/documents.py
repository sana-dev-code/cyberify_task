from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    filename: str
    chunk_index: int
    page_number: int | None
    chunk_text: str
    score: float | None = None
    created_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    enabled: bool
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentRead]


class DocumentToggleResponse(BaseModel):
    id: UUID
    filename: str
    enabled: bool
    message: str


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    filename: str
    chunk_count: int
    enabled: bool
    message: str


class SourceChunk(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    filename: str
    chunk_index: int
    page_number: int | None
    chunk_text: str
    score: float | None = None
    created_at: datetime


class UploadResponse(BaseModel):
    filename: str
    chunk_count: int


from datetime import datetime
from uuid import UUID

class DocumentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    filename: str
    enabled: bool
    created_at: datetime

class DocumentListResponse(BaseModel):
    documents: list[DocumentItem]