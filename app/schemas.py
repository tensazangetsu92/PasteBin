from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class TextCreate(BaseModel):
    text: str  # Текст, который вводит пользователь
    expires_at: Optional[datetime]  # Опциональная дата истечения срока

class TextResponse(BaseModel):
    id: int
    blob_url: HttpUrl
    short_key: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
