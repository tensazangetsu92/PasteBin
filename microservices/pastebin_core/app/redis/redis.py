import json
import time
from datetime import datetime

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
    """Получить пост из кэша, увеличить счетчик просмотров и вернуть количество просмотров."""
    async with redis.pipeline() as pipe:
        await pipe.zincrby("post_views", 1, short_key)
        await pipe.expire("post_views", settings.TTL_VIEWS)
        await pipe.zscore("post_views", short_key)
        await pipe.get(f"popular_post:{short_key}")  # Получаем кэшированное представление поста
        results = await pipe.execute()
        cached_post = results[3]  # Кэшированные данные поста

    return cached_post

async def get_post_from_cache(redis: Redis, short_key: str):
    cached_data = await redis.get(f"popular_post:{short_key}")
    if cached_data:
        post_data = json.loads(cached_data)
        post_data["created_at"] = datetime.fromisoformat(post_data["created_at"])
        post_data["expires_at"] = datetime.fromisoformat(post_data["expires_at"])
        return post_data
    return None

async def cache_post(redis: Redis, short_key: str, post_data: dict, ttl: int = 10):
    post_data["created_at"] = post_data["created_at"].isoformat()
    post_data["expires_at"] = post_data["expires_at"].isoformat()
    await redis.set(f"popular_post:{short_key}", json.dumps(post_data), ex=ttl)

async def get_popular_posts_keys(redis: Redis, limit: int = 3):
    """Получить ключи популярных постов, отсортированных по количеству просмотров."""
    popular_posts = await redis.zrevrange("post_views", 0, limit - 1, withscores=True)
    post_keys = [key for key, _ in popular_posts]  # Извлекаем ключи постов
    return post_keys

