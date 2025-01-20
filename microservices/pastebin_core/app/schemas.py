from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime

class TextCreate(BaseModel):
    name: str = "Untitled"
    text: str = "Some text"
    expires_at: datetime

    @validator('expires_at', pre=True)
    def parse_expires_at(cls, v):
        # Если expires_at None, установить значение по умолчанию
        if v is None:
            return datetime(2040, 12, 30, 14, 1, 49, 746000)
        # Если значение в формате ISO, преобразовать в datetime
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        return v  # В случае уже валидного datetime


class TextResponse(BaseModel):
    id: int
    blob_url: HttpUrl
    short_key: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
