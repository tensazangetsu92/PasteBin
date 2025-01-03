import secrets
import redis.asyncio as redis

# Подключение к Redis
async def connect_to_redis() -> redis.Redis:
    """Подключение к Redis."""
    try:
        redis_client = redis.Redis(
            host='redis-10298.c83.us-east-1-2.ec2.redns.redis-cloud.com',
            port=10298,
            db=0,
            decode_responses=True,
            username="default",
            password="dXG2FwFeuzy4UpRJr0g395czf8oaoIge",
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
