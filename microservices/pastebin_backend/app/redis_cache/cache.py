import json
import random
from datetime import datetime
import redis.asyncio as redis
from redis.asyncio import Redis
from microservices.pastebin_backend.app.config import settings
from microservices.pastebin_backend.app.retry_config import cache_retry


@cache_retry
async def connect_to_redis():
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

@cache_retry
async def disconnect_from_redis(redis_client: redis.Redis):
    """Отключение от Redis."""
    if redis_client:
        await redis_client.close()

@cache_retry
async def create_post_cache(redis_client: Redis, short_key: str, post_data: dict, ttl: int = 10):
    post_data["created_at"] = post_data["created_at"].isoformat()
    post_data["expires_at"] = post_data["expires_at"].isoformat()
    await redis_client.set(f"popular_post:{short_key}", json.dumps(post_data), ex=ttl)

@cache_retry
async def get_post_cache(redis_client: Redis, short_key: str):
    cached_data = await redis_client.get(f"popular_post:{short_key}")
    if cached_data:
        post_data = json.loads(cached_data)
        post_data["created_at"] = datetime.fromisoformat(post_data["created_at"])
        post_data["expires_at"] = datetime.fromisoformat(post_data["expires_at"])
        return post_data
    return None

@cache_retry
async def update_post_cache(redis_client: Redis, short_key: str, updated_data: dict, ttl: int = 10):
    """Обновляет пост в кэше Redis."""
    existing_post = await get_post_cache(redis_client, short_key)
    if existing_post:
        existing_post.update(updated_data)  # Обновляем данные
        existing_post["created_at"] = existing_post["created_at"].isoformat()
        existing_post["expires_at"] = existing_post["expires_at"].isoformat()
        await redis_client.set(f"popular_post:{short_key}", json.dumps(existing_post), ex=ttl)

@cache_retry
async def delete_post_cache(redis_client: Redis, short_key: str, post_id: str, sorted_set: str):
    """Удаляет пост по short_key из кэша Redis с использованием pipeline."""
    async with redis_client.pipeline() as pipe:
        pipe.delete(f"popular_post:{short_key}")
        pipe.zrem(sorted_set, post_id)
        await pipe.execute()

@cache_retry
async def get_popular_posts_keys(redis_client: Redis, sorted_set: str, top_n: int = 20, limit: int = 5):
    """Получить случайные limit постов из top_n самых популярных."""
    keys = await redis_client.keys(f"popular_post:*")
    selected_keys = random.sample(keys, min(limit, len(keys)))
    return selected_keys

@cache_retry
async def increment_views_in_cache(redis_client: Redis, post_id: str, sorted_set: str):
    async with redis_client.pipeline() as pipe:
        pipe.zincrby(sorted_set, 1, post_id)
        pipe.zscore(sorted_set, post_id)
        results = await pipe.execute()
        views = results[1]
    return views



@cache_retry
async def get_all_keys_sorted_set(redis_client: Redis, sorted_set: str):
    keys = await redis_client.zrange(sorted_set, 0, -1, withscores=True)
    return keys

@cache_retry
async def delete_all_keys_from_sorted_set(redis_client: Redis, sorted_set: str):
    await redis_client.zremrangebyrank(sorted_set, 0, -1)

@cache_retry
async def delete_key_sorted_set(redis_client: Redis, sorted_set: str, short_key: str):
    await redis_client.zrem(sorted_set, short_key)

@cache_retry
async def update_score_sorted_set(redis_client: Redis, sorted_set: str, short_key: str, score: int):
    await redis_client.zadd(sorted_set, {short_key: score})

