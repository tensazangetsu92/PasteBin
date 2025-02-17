import json
from datetime import datetime

from fastapi import HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_backend.app.redis_cache.cache import create_post_cache, get_post_cache, increment_views_in_cache, delete_post_cache, update_post_cache
from microservices.pastebin_backend.app.postgresql_db.crud import get_record_by_short_key, get_records_by_user_id, delete_record_by_short_key, update_record
from microservices.pastebin_backend.app.yandex_bucket.storage import get_file_from_bucket, delete_file_from_bucket
from microservices.pastebin_backend.app.utils import convert_to_kilobytes, get_post_age
from microservices.pastebin_backend.app.config import settings
from microservices.pastebin_backend.app.postgresql_db.crud import create_record
from microservices.pastebin_backend.app.yandex_bucket.storage import upload_file_to_bucket
from microservices.pastebin_backend.app.schemas.posts_schemas import PostCreate, PostUpdate
from microservices.pastebin_backend.app.utils import get_hash


async def add_post_service(
    text_data: PostCreate,
    db: AsyncSession,
    current_user_id: int,
):
    """Добавление нового поста."""
    short_key = await get_hash()
    while await get_record_by_short_key(db, short_key) is not None:
        short_key = await get_hash()
    blob_url = await upload_file_to_bucket(settings.BUCKET_NAME, current_user_id, short_key, text_data.text)
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

async def get_post_service(
    request: Request,
    short_key: str,
    session: AsyncSession,
    background_tasks: BackgroundTasks,
):
    """Получение текста по short_key."""
    try:
        redis = request.app.state.redis
        cached_post = await get_post_cache(redis, short_key)
        if cached_post:
            await increment_views_in_cache(redis, cached_post['id'], settings.SORTED_SET_VIEWS)
            cached_post["views"] += 1
            background_tasks.add_task(create_post_cache,redis, cached_post["short_key"], cached_post, settings.TTL_POSTS)
            return cached_post
        else:
            text_record = await get_record_by_short_key(session, short_key)
            if not text_record: raise HTTPException(status_code=404, detail="Text not found")
            file_data = await get_file_from_bucket(text_record.blob_url)
            views = await increment_views_in_cache(redis, text_record.id, settings.SORTED_SET_VIEWS)
            response = {
                "id": text_record.id,
                "name": text_record.name,
                "text": file_data["content"],
                "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
                "short_key": short_key,
                "created_at": text_record.created_at,
                "expires_at": text_record.expires_at,
                "views" : text_record.views_count,
            }

            if views >= settings.CACHE_VIEWS_THRESHOLD:
                background_tasks.add_task(create_post_cache, redis, short_key, response, settings.TTL_POSTS)
            return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")

async def get_popular_posts_service(request: Request):
    """Получение популярных постов."""
    try:
        redis = request.app.state.redis
        cached_popular_posts = await redis.get("most_popular_posts")
        if cached_popular_posts:
            response = []
            popular_posts = json.loads(cached_popular_posts)
            for post in popular_posts:
                if post:
                    post["created_at"] = get_post_age(datetime.fromisoformat(post["created_at"]))
                    response.append(post)
            return {"posts": response}
        else:
            raise HTTPException(status_code=404, detail="Популярные посты не найдены в кеше")
    except Exception as e:
        print(f"Ошибка при получении популярных постов: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения популярных постов")

async def get_user_posts_service( session: AsyncSession, user_id: int):
    """Получить список постов текущего пользователя."""
    posts = await get_records_by_user_id(session, user_id)
    response = [
        {
            "id": post.id,
            "name": post.name,
            "short_key": post.short_key,
            "created_at": get_post_age(post.created_at),
            "expires_at": post.expires_at.isoformat(),
            "views": post.views_count,
        }
        for post in posts[:5]
    ]
    return {"posts": response}

async def delete_post_service(
        short_key: str,
        request: Request,
        session: AsyncSession,
        background_tasks: BackgroundTasks
):
    """Удаляет пост с указанным short_key."""

    post = await delete_record_by_short_key(session, short_key)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    background_tasks.add_task(delete_post_cache, request.app.state.redis, short_key, post.id, settings.SORTED_SET_VIEWS)
    background_tasks.add_task(delete_file_from_bucket,settings.BUCKET_NAME, post.author_id, short_key)
    return post

async def update_post_service(
    short_key: str,
    post_data: PostUpdate,
    request: Request,
    session: AsyncSession,
    user_id: int
):
    post = await get_record_by_short_key(session, short_key)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this post")
    if post_data.text is not None:
        await upload_file_to_bucket(settings.BUCKET_NAME, user_id, short_key, post_data.text)
    if post_data.name is not None:
        post.name = post_data.name
    if post_data.expires_at is not None:
        post.expires_at = post_data.expires_at
    updated_post = await update_record(session, short_key, post)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found after update")
    if await get_post_cache(request.app.state.redis, short_key):
        await update_post_cache(request.app.state.redis, short_key, {
            "name": post_data.name,
            "text": post_data.text,
            "expires_at": post_data.expires_at
        }, settings.TTL_POSTS)
    return updated_post



