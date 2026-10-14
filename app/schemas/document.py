from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)