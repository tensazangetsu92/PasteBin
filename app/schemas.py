from pydantic import BaseModel

class Paste(BaseModel):
    title: str
    content: str
    expiration: int
