from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List
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
    name: str
    text_size_kilobytes: int
    short_key: str
    created_at: str
    expires_at: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(timespec='milliseconds')
        }
class PopularPostsResponse(BaseModel):
    posts: List[TextResponse]
