import aioredis

REDIS_URL = "redis-10298.c83.us-east-1-2.ec2.redns.redis-cloud.com:10298"
redis = None

async def connect_to_redis():
    """Подключение к Redis."""
    global redis
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

async def disconnect_from_redis():
    """Отключение от Redis."""
    if redis:
        await redis.close()
