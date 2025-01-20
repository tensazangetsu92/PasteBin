from datetime import datetime
from io import BytesIO
import json
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .redis.redis import get_and_increment_views, cache_post, get_popular_posts_keys
from .postgresql.crud import get_text_by_short_key
from .yandex_bucket.storage import get_file_from_bucket
from .utils import convert_to_kilobytes, get_post_age
from .config import settings
from .postgresql.crud import create_text_record
from .yandex_bucket.storage import upload_file_to_bucket
from .schemas import TextCreate


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

async def add_post_service(
    text_data: TextCreate,
    db: AsyncSession,
    current_user_id: int,
):
    """Добавление нового поста."""
    file_obj = BytesIO(text_data.text.encode("utf-8"))
    short_key = await get_hash()
    while await get_text_by_short_key(db, short_key) is not None:
        short_key = await get_hash()
    blob_url = await upload_file_to_bucket(
        settings.BUCKET_NAME, current_user_id, short_key, file_obj
    )
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
        "views" : views,
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
        creation_time = get_post_age(text_record.created_at)
        response.append({
            "name": text_record.name,
            "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
            "short_key": short_key,
            "creation_date": creation_time,
            "expires_at": text_record.expires_at,
        })
    print(response)
    return response
