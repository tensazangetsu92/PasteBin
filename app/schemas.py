from pydantic import BaseModel

class Text(BaseModel):
    id: int

class TextAdd(Text):
    title: str
    content: str | None
    expiration: int