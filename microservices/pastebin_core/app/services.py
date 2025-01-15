import secrets
from datetime import datetime
from http.client import HTTPException
from typing import Optional, BinaryIO
import httpx
from microservices.pastebin_core.app.config import settings
from microservices.pastebin_core.app.yandex_bucket.storage import upload_file_to_bucket
from microservices.pastebin_core.app.postgresql.crud import create_text_record, get_text_by_short_key
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_short_key(length: int = 8) -> str:
    """Генерация уникального короткого ключа."""
    return secrets.token_urlsafe(length)[:length]

async def get_hash() -> str:
    """Получение хэша от хэш-сервера через HTTP-запрос."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.HASH_SERVER_URL)
            if response.status_code == 200:
                data = response.json()
                if "hash" in data:
                    return data["hash"]
            raise ValueError("Failed to fetch hash from hash server")
    except httpx.RequestError as req_err:
        raise HTTPException(503, f"Failed to fetch hash from hash server: {req_err}")

async def upload_file_and_save_to_db(
    session: AsyncSession,
    # redis_client: redis.Redis,
    file_obj: BinaryIO,
    bucket_name: str,
    object_name: str,
    author_id: int,
    expires_at: Optional[datetime] = None,
):
    """Загрузка файла и сохранение данных в БД."""
    short_key = await get_hash()
    while await get_text_by_short_key(session, short_key) is not None:
        short_key = await get_hash()
    blob_url = await upload_file_to_bucket(bucket_name, author_id ,short_key, file_obj)
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

