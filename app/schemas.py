from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class TextCreate(BaseModel):
    blob_url: HttpUrl
    expires_at: Optional[datetime]

class TextResponse(BaseModel):
    id: int
    blob_url: HttpUrl
    short_key: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
