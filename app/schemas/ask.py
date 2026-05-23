from pydantic import BaseModel, Field

from app.schemas.documents import SourceChunk


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class AskResponse(BaseModel):
    answer: str
    prompt: str
    sources: list[SourceChunk]