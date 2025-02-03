from io import BytesIO
import json
import asyncio
import httpx
from fastapi import HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .postgresql.database import async_session
from .redis.redis import get_post_and_incr_recent_views_in_cache, cache_post, get_popular_posts_keys, \
    get_post_from_cache, \
    increment_views_in_cache, delete_post_from_cache
from .postgresql.crud import get_record_by_short_key, get_records_by_user_id, delete_record_by_short_key
from .yandex_bucket.storage import get_file_from_bucket, delete_file_from_bucket
from .utils import convert_to_kilobytes, get_post_age
from .config import settings
from .postgresql.crud import create_record
from .yandex_bucket.storage import upload_file_to_bucket
from .schemas import PostCreate


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
    text_data: PostCreate,
    db: AsyncSession,
    current_user_id: int,
):
    """Добавление нового поста."""
    file_obj = BytesIO(text_data.text.encode("utf-8"))
    short_key = await get_hash()
    while await get_record_by_short_key(db, short_key) is not None:
        short_key = await get_hash()
    blob_url = await upload_file_to_bucket(
        settings.BUCKET_NAME, current_user_id, short_key, file_obj
    )
    new_post = await create_record(
        session=db,
        object_name=text_data.name,
        blob_url=blob_url,
        short_key=short_key,
        author_id=current_user_id,
        expires_at=text_data.expires_at.replace(tzinfo=None),
    )
    await db.commit()
    return new_post

async def get_text_service(
    request: Request,
    short_key: str,
    session: AsyncSession,
    background_tasks: BackgroundTasks,
):
    """Получение текста по short_key."""
    try:
        redis = request.app.state.redis
        background_tasks.add_task(increment_views_in_cache, redis, short_key)
        cached_post, recent_views = await get_post_and_incr_recent_views_in_cache(redis, short_key, settings.SORTED_SET_RECENT_VIEWS)
        if cached_post:
            return json.loads(cached_post)
        else:
            text_record = await get_record_by_short_key(session, short_key)
            if not text_record:
                raise HTTPException(status_code=404, detail="Text not found")
            file_data = await get_file_from_bucket(text_record.blob_url)
            response = {
                "name": text_record.name,
                "text": file_data["content"],
                "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
                "short_key": short_key,
                "created_at": text_record.created_at,
                "expires_at": text_record.expires_at,
                "views" : text_record.views_count,
            }
            if recent_views >= settings.CACHE_VIEWS_THRESHOLD:
                background_tasks.add_task(cache_post, redis, short_key, response, settings.TTL_POSTS)
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")

async def get_popular_posts_service(request, session: AsyncSession):
    """Получение популярных постов."""
    redis = request.app.state.redis
    keys = await get_popular_posts_keys(redis, settings.SORTED_SET_RECENT_VIEWS)

    async def fetch_post(short_key):
        text_record_cached = await get_post_from_cache(redis, short_key)
        if text_record_cached:
            creation_time = get_post_age(text_record_cached['created_at'])
            return {
                "name": text_record_cached['name'],
                "text_size_kilobytes": text_record_cached["text_size_kilobytes"],
                "short_key": short_key,
                "created_at": creation_time,
                "expires_at": text_record_cached['expires_at'],
            }
        else:
            async with async_session() as new_session:
                text_record = await get_record_by_short_key(new_session, short_key)
                if not text_record: return None
                file_data = await get_file_from_bucket(text_record.blob_url)
                creation_time = get_post_age(text_record.created_at)
                return {
                    "name": text_record.name,
                    "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
                    "short_key": short_key,
                    "created_at": creation_time,
                    "expires_at": text_record.expires_at,
                }
    posts = await asyncio.gather(*(fetch_post(short_key) for short_key in keys))
    posts = [post for post in posts if post]
    return {"posts": posts}

async def get_user_posts_service(request: Request, session: AsyncSession, user_id: int):
    """Получить список постов текущего пользователя."""
    posts = await get_records_by_user_id(session, user_id)
    response = [
        {
            "id": post.id,
            "name": post.name,
            "short_key": post.short_key,
            "created_at": post.created_at,
            "expires_at": post.expires_at,
            "views": post.views_count,
        }
        for post in posts
    ]
    return response

async def delete_post_service(
        short_key: str,
        request: Request,
        session: AsyncSession,
        background_tasks: BackgroundTasks
):
    """Удаляет пост с указанным short_key."""
    background_tasks.add_task(delete_post_from_cache,request.app.state.redis, short_key, settings.SORTED_SET_RECENT_VIEWS)
    post = await delete_record_by_short_key(session, short_key)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    background_tasks.add_task(delete_file_from_bucket,settings.BUCKET_NAME, post.author_id, short_key)
    return post


