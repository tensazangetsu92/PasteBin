import json
import random
from datetime import datetime
from typing import Dict
import redis.asyncio as redis
from redis.asyncio import Redis
from microservices.pastebin_backend.app.config import settings


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


async def cache_post(redis: Redis, short_key: str, post_data: dict, ttl: int = 10):
    post_data["created_at"] = post_data["created_at"].isoformat()
    post_data["expires_at"] = post_data["expires_at"].isoformat()
    await redis.set(f"popular_post:{short_key}", json.dumps(post_data), ex=ttl)

async def get_post_from_cache(redis: Redis, short_key: str):
    cached_data = await redis.get(f"popular_post:{short_key}")
    if cached_data:
        post_data = json.loads(cached_data)
        post_data["created_at"] = datetime.fromisoformat(post_data["created_at"])
        post_data["expires_at"] = datetime.fromisoformat(post_data["expires_at"])
        return post_data
    return None


async def delete_post_from_cache(redis: Redis, short_key: str, sorted_set: str):
    """Удаляет пост по short_key из кэша Redis с использованием pipeline."""
    async with redis.pipeline() as pipe:
        pipe.delete(f"popular_post:{short_key}")
        pipe.delete(f"views:{short_key}")
        pipe.zrem(sorted_set, short_key)
        await pipe.execute()


async def increment_views_in_cache(redis: Redis, short_key: str):
    return await redis.incr(f"views:{short_key}")

async def get_popular_posts_keys(redis: Redis, sorted_set: str, top_n: int = 20, limit: int = 5):
    """Получить случайные limit постов из top_n самых популярных."""
    popular_posts = await redis.zrevrange(sorted_set, 0, top_n - 1, withscores=False)
    # Выбираем 5 случайных из 20
    selected_posts = random.sample(popular_posts, min(limit, len(popular_posts)))
    return selected_posts

async def get_post_and_incr_recent_views_in_cache(redis: Redis, short_key: str, sorted_set: str):
    """Получить пост из кэша, увеличить счетчик просмотров и вернуть количество просмотров."""
    async with redis.pipeline() as pipe:
        pipe.zincrby(sorted_set, 1, short_key)
        pipe.expire(sorted_set, settings.TTL_VIEWS)
        pipe.zscore(sorted_set, short_key)
        pipe.get(f"popular_post:{short_key}")  # Получаем кэшированное представление поста
        results = await pipe.execute()
        views = results[0]  # Количество просмотров (балл)
        cached_post = results[3]  # Кэшированные данные поста
    return cached_post, views

async def get_all_views_from_cache(redis) -> Dict[str, int]:
    """Получает все просмотры из кеша."""
    keys = await redis.keys("views:*")
    views = {}
    for key in keys:
        post_id = key.split(":")[1]
        count = await redis.get(key)
        if count:
            views[post_id] = int(count)
    return views

async def clear_views_from_cache(redis, post_ids):
    keys = [f"views:{post_id}" for post_id in post_ids]
    if keys:
        await redis.delete(*keys)


async def get_all_keys_sorted_set(redis: Redis, sorted_set: str):
    keys = await redis.zrange(sorted_set, 0, -1, withscores=True)
    return keys

async def delete_key_sorted_set(redis: Redis, sorted_set: str, short_key: str):
    await redis.zrem(sorted_set, short_key)

async def update_score_sorted_set(redis: Redis, sorted_set: str, short_key: str, score: int):
    await redis.zadd(sorted_set, {short_key: score})

