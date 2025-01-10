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
    """Получить пост из кэша и увеличить счетчик просмотров с помощью Lua."""
    lua_script = """
    local post = redis.call("GET", KEYS[1])
    local views = redis.call("INCR", KEYS[2])
    return {post, views}
    """
    keys = [f"popular_post:{short_key}", f"post_views:{short_key}"]
    result = await redis.eval(lua_script, len(keys), *keys)
    cached_post, views = result[0], int(result[1])
    return cached_post, views


async def cache_post(redis: Redis, short_key: str, post_data: dict, ttl: int = 3600):
    """Сохранить пост в кэш с помощью Lua."""
    lua_script = """
    redis.call("SET", KEYS[1], ARGV[1], "EX", ARGV[2])
    """
    key = f"popular_post:{short_key}"
    value = json.dumps(post_data)
    await redis.eval(lua_script, 1, key, value, ttl)
