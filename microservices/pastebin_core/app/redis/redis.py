import json
import time

import redis.asyncio as redis
from redis.asyncio import Redis

from microservices.pastebin_core.app.config import settings


async def connect_to_redis() -> redis.Redis:
    """Подключение к Redis."""
    try:
        redis_client = redis.Redis(
            host=settings.DB_REDIS_HOST,
            port=settings.DB_REDIS_PORT,
            db=settings.DB_REDIS_INDEX,
            decode_responses=True,
            username=settings.DB_REDIS_USERNAME,
            password=settings.DB_REDIS_PASSWORD,
        )
        return redis_client
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        return None

async def disconnect_from_redis(redis_client: redis.Redis):
    """Отключение от Redis."""
    if redis_client:
        await redis_client.close()

async def get_and_increment_views(redis: Redis, short_key: str):
    """Получить пост из кэша и увеличить счетчик просмотров."""
    async with redis.pipeline() as pipe:
        pipe.get(f"popular_post:{short_key}")
        pipe.incr(f"post_views:{short_key}")
        pipe.expire(f"post_views:{short_key}", settings.TTL_VIEWS)
        cached_post, views, ttl_set_result  = await pipe.execute()
    return cached_post, views

async def cache_post(redis: Redis, short_key: str, post_data: dict, ttl: int = 10):
    """Сохранить пост в кэш."""
    await redis.set(f"popular_post:{short_key}", json.dumps(post_data), ex=ttl)

async def get_popular_posts_keys(redis: Redis, limit: int = 10):
    keys = await redis.keys("post_views:*")
    post_views = []
    for key in keys:
        views = await redis.get(key)
        if views:
            post_views.append((key, int(views)))  # Убираем decode()
    post_views.sort(key=lambda x: x[1], reverse=True)
    return [key.split(':')[1] for key, _ in post_views[:limit]]

