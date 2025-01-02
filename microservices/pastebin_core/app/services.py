import secrets
from datetime import datetime
from typing import Optional, BinaryIO
import httpx

from microservices.pastebin_core.app.redis.redis_client import redis
from microservices.pastebin_core.app.yandex_bucket.storage import upload_file_to_bucket
from microservices.pastebin_core.app.postgresql.crud import create_text_record, get_text_by_short_key
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_short_key(length: int = 8) -> str:
    """Генерация уникального короткого ключа."""
    return secrets.token_urlsafe(length)[:length]

HASH_SERVER_URL = "http://127.0.0.1:8001/get_hash"

async def get_hash():
    """Получение хешей из Redis."""
    hash = await redis.rpop("hash_pool")
    if hash:
        return {"hash": hash}
    return {"error": "No hash available"}

async def upload_file_and_save_to_db(
    session: AsyncSession,
    file_obj: BinaryIO,
    bucket_name: str,
    object_name: str,
    author_id: int,
    expires_at: Optional[datetime] = None,
):
    """Загрузка файла и сохранение данных в БД."""
    # Генерация уникального короткого ключа
    # short_key = await generate_short_key()
    short_key = await get_hash()
    # Проверка уникальности короткого ключа
    while await get_text_by_short_key(session, short_key) is not None:
        short_key = await generate_short_key()
    # Загрузка файла в бакет
    blob_url = await upload_file_to_bucket(bucket_name, author_id ,short_key, file_obj)
    # Сохранение записи в БД
    new_text = await create_text_record(
        session=session,
        object_name=object_name,
        blob_url=blob_url,
        short_key=short_key,
        author_id=author_id,
        expires_at=expires_at,
    )
    await session.commit()
    return new_text

