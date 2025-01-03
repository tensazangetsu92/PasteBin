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
        print(redis_client.keys('*'))
        return redis_client
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        return None

# Отключение от Redis
async def disconnect_from_redis(redis_client: redis.Redis):
    """Отключение от Redis."""
    if redis_client:
        await redis_client.close()