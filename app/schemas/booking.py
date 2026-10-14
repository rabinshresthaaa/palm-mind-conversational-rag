
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    interview_at: datetime


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    interview_at: datetime
    status: str
    created_at: datetime
