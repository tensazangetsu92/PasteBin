import secrets
from typing import Optional
import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import TextUrlOrm


async def generate_short_key(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]


async def create_text(
        session: AsyncSession,
        blob_url: str,
        author_id: int,
        expires_at: Optional[datetime.datetime] = None
):
    short_key = await generate_short_key()

    # Проверка уникальности (опционально)
    while True:
        existing = await session.execute(
            select(TextUrlOrm).where(TextUrlOrm.short_key == short_key)
        )
        if existing.scalar() is None:
            break
        short_key = await generate_short_key()

    # Создание новой записи
    new_text = TextUrlOrm(
        blob_url=blob_url,
        short_key=short_key,
        author_id=author_id,
        expires_at=expires_at,
    )
    session.add(new_text)
    await session.commit()
    await session.refresh(new_text)
    return new_text
