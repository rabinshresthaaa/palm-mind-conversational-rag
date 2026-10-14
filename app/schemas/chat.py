from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=100,
        description="Identifies a conversation across multiple requests.",
    )
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="The user's question or message.",
    )


class SourceChunk(BaseModel):
    document_id: int | None = None
    filename: str | None = None
    chunk_index: int | None = None
    text: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceChunk]
    booking_created: bool = False
    booking_id: int | None = None