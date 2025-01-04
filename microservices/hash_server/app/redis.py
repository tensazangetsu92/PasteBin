import secrets
import redis.asyncio as redis
from .config import settings

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

async def generate_hashes(redis_client: redis.Redis, count: int) -> None:
    """Генерация хешей и сохранение их в Redis."""
    hashes = [secrets.token_urlsafe(8)[:8] for _ in range(count)]
    await redis_client.lpush("hash_pool", *hashes)

async def check_and_generate_hashes(redis_client: redis.Redis) -> None:
    """Проверка количества хешей в Redis и добавление новых, если их меньше минимального порога."""
    hash_count = await redis_client.llen("hash_pool")
    if hash_count < 100:  # Минимальное количество хешей
        await generate_hashes(redis_client, 100)
