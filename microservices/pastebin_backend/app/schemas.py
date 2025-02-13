from pydantic import BaseModel, HttpUrl, validator, EmailStr, field_validator, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime

class PostCreate(BaseModel):
    name: str = "Untitled"
    text: str = "Some text"
    expires_at: Optional[datetime]

    @field_validator('expires_at')
    @classmethod
    def parse_expires_at(cls, v):
        if v is None:
            return datetime(2040, 12, 30, 14, 1, 49, 746000)
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        return v


class GetPostResponse(BaseModel):
    id: int
    name: str
    text: str
    text_size_kilobytes: float
    short_key: str
    created_at: datetime
    expires_at: datetime
    views: int


class UserPostResponse(BaseModel):
    id: int
    name: str
    short_key: str
    created_at: str
    expires_at: str
    views: int

    model_config = ConfigDict(
            json_encoders={
            datetime: lambda v: v.isoformat(timespec='milliseconds')
        })
class UserPostsResponse(BaseModel):
    posts: List[UserPostResponse]


class PostResponse(BaseModel):
    name: str
    text_size_kilobytes: float
    short_key: str
    created_at: str
    expires_at: str

    model_config = ConfigDict(
            json_encoders={
            datetime: lambda v: v.isoformat(timespec='milliseconds')
        })
class PopularPostsResponse(BaseModel):
    posts: List[PostResponse]

class PostUpdate(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    expires_at: Optional[datetime] = None

    @field_validator('expires_at', mode='before')
    @staticmethod
    def parse_expires_at(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.replace("Z", "+00:00")
            return datetime.fromisoformat(v)
        return v

