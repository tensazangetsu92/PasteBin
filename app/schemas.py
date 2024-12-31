from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class TextCreate(BaseModel):
    name: str = "Untitled"
    text: str = "text"
    expires_at: Optional[datetime] = "2025-12-30T14:01:49.746Z"


class TextResponse(BaseModel):
    id: int
    blob_url: HttpUrl
    short_key: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
