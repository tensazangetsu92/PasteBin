from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_core.app.postgresql.models import TextUrlOrm, UserOrm
from microservices.pastebin_core.app.yandex_bucket.storage import delete_file_from_bucket


async def create_text_record(
    session: AsyncSession,
    object_name: str,
    blob_url: str,
    short_key: str,
    author_id: int,
    expires_at: Optional[datetime] = None,
):
    """Создать новую запись в базе данных."""
    new_text = TextUrlOrm(
        name=object_name,
        blob_url=blob_url,
        short_key=short_key,
        author_id=author_id,
        expires_at=expires_at,
    )
    session.add(new_text)
    await session.flush()
    await session.refresh(new_text)
    return new_text

async def get_text_by_short_key(session: AsyncSession, short_key: str):
    """Получить запись по короткому ключу."""
    result = await session.execute(
        select(TextUrlOrm).where(TextUrlOrm.short_key == short_key)
    )
    return result.scalar()


async def delete_text_record(
        session: AsyncSession,
        text_id: int
):
    """Удалить запись по id"""
    text = await session.get(TextUrlOrm, text_id)
    if text:
        await session.delete(text)
        await session.commit()
    else:
        print("Текста с таким id нет")


async def delete_expired_records(session: AsyncSession):
    """Удаляет записи с истёкшим сроком действия."""
    try:
        now = datetime.utcnow()
        async with session.begin():
            expired_records = await session.execute(
                select(TextUrlOrm).where(TextUrlOrm.expires_at < now)
            )
            expired_records = expired_records.scalars().all()

        for record in expired_records:
            await delete_file_from_bucket("texts", record.author_id, record.short_key)  # Удаление файла из бакета
            async with session.begin():
                await session.execute(delete(TextUrlOrm).where(TextUrlOrm.id == record.id))  # Удаление записи из БД

        print("Устаревшие записи удалены")
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")


async def get_user_by_username(session: AsyncSession, username: str):
    db_user = await session.execute(select(UserOrm).where(UserOrm.username == username))
    return db_user.scalar_one_or_none()
