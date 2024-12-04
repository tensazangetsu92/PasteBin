from typing import Annotated

from fastapi import APIRouter, Depends
from .schemas import Text, TextAdd

router = APIRouter(
    prefix="/texts",
    tags=["таск"],
)

texts = []

@router.post("/add")
async def add_text(
        text: TextAdd
):
    texts.append(text.content)
    return {"ok": True}