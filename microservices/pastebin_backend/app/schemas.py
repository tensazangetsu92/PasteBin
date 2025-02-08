from pydantic import BaseModel, HttpUrl, validator, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

class PostCreate(BaseModel):
    name: str = "Untitled"
    text: str = "Some text"
    expires_at: datetime

    @field_validator('expires_at', mode='before')
    @staticmethod
    def parse_expires_at(cls, v):
        # Если expires_at None, установить значение по умолчанию
        if v is None:
            return datetime(2040, 12, 30, 14, 1, 49, 746000)
        # Если значение в формате ISO, преобразовать в datetime
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        return v  # В случае уже валидного datetime

class PostResponse(BaseModel):
    name: str
    text_size_kilobytes: float
    short_key: str
    created_at: str
    expires_at: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(timespec='milliseconds')
        }
class PopularPostsResponse(BaseModel):
    posts: List[PostResponse]


class PostUpdate(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    expires_at: Optional[datetime] = None

    @field_validator('expires_at', mode='before')
    @staticmethod
    def parse_expires_at(cls, v):
        # Если expires_at None, установить значение по умолчанию
        if v is None:
            return None
        # Если значение в формате ISO, преобразовать в datetime
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        return v  # В случае уже валидного datetime

