from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import TextUrlOrm


async def get_text_by_short_key(session: AsyncSession, short_key: str):
    """Получить запись по короткому ключу."""
    result = await session.execute(
        select(TextUrlOrm).where(TextUrlOrm.short_key == short_key)
    )
    return result.scalar()


async def create_text_record(
    session: AsyncSession,
    blob_url: str,
    short_key: str,
    author_id: int,
    expires_at: Optional[datetime] = None,
):
    """Создать новую запись в базе данных."""
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
