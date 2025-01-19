import secrets
from datetime import datetime
from io import BytesIO
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .redis.redis import get_and_increment_views, cache_post, get_popular_posts_keys
from .postgresql.crud import get_text_by_short_key
from .yandex_bucket.storage import get_file_from_bucket
from .utils import convert_to_kilobytes
from .config import settings
from .postgresql.crud import create_text_record
from .yandex_bucket.storage import upload_file_to_bucket
from .schemas import TextCreate


async def generate_short_key(length: int = 8) -> str:
    """Генерация уникального короткого ключа."""
    return secrets.token_urlsafe(length)[:length]

async def add_post_service(
    text_data: TextCreate,
    db: AsyncSession,
    current_user_id: int,
):
    """Добавление нового поста."""
    file_obj = BytesIO(text_data.text.encode("utf-8"))
    short_key = await generate_short_key()
    while await get_text_by_short_key(db, short_key) is not None:
        short_key = await generate_short_key()
    blob_url = await upload_file_to_bucket(
        settings.BUCKET_NAME, current_user_id, short_key, file_obj
    )
    # # Преобразуем expires_at в datetime, если оно в строке ISO
    # if isinstance(text_data.expires_at, str):
    #     text_data.expires_at = datetime.fromisoformat(text_data.expires_at)

    new_text = await create_text_record(
        session=db,
        object_name=text_data.name,
        blob_url=blob_url,
        short_key=short_key,
        author_id=current_user_id,
        expires_at=text_data.expires_at.replace(tzinfo=None),
    )
    await db.commit()
    return new_text

async def get_text_service(
    request, short_key: str, session: AsyncSession
):
    """Получение текста по short_key."""
    redis = request.app.state.redis
    cached_post, views = await get_and_increment_views(redis, short_key)
    if cached_post:
        return json.loads(cached_post)
    text_record = await get_text_by_short_key(session, short_key)
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")
    try:
        file_data = await get_file_from_bucket(text_record.blob_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")
    response = {
        "name": text_record.name,
        "text": file_data["content"],
        "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
        "short_key": short_key,
        "created_at": text_record.created_at,
        "expires_at": text_record.expires_at,
    }
    if views >= settings.CACHE_VIEWS_THRESHOLD:
        await cache_post(redis, short_key, response, settings.TTL_POSTS)
    return response

async def get_popular_posts_service(request, session: AsyncSession):
    """Получение популярных постов."""
    redis = request.app.state.redis
    keys = await get_popular_posts_keys(redis)
    response = []
    for short_key in keys:
        text_record = await get_text_by_short_key(session, short_key)
        file_data = await get_file_from_bucket(text_record.blob_url)

        # Вычисляем разницу во времени
        time_difference = datetime.utcnow() - text_record.created_at
        if time_difference.days > 0:
            creation_time = f"{time_difference.days} дней назад"
        elif time_difference.seconds >= 3600:
            creation_time = f"{time_difference.seconds // 3600} часов назад"
        elif time_difference.seconds >= 60:
            creation_time = f"{time_difference.seconds // 60} минут назад"
        else:
            creation_time = f"{time_difference.seconds} секунд назад"

        response.append({
            "name": text_record.name,
            "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
            "short_key": short_key,
            "creation_date": creation_time,
            "expires_at": text_record.expires_at,
        })

    return response
