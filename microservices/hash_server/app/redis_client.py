import redis.asyncio as redis

REDIS_URL = "redis-10298.c83.us-east-1-2.ec2.redns.redis-cloud.com:10298"
redis_client = None

async def connect_to_redis():
    """Подключение к Redis."""
    global redis_client

    try:
        redis_client = redis.Redis(
            host='redis-10298.c83.us-east-1-2.ec2.redns.redis-cloud.com',
            port=10298,
            decode_responses=True,
            username="default",
            password="dXG2FwFeuzy4UpRJr0g395czf8oaoIge",
        )

        await redis_client.ping()
        print("Redis подключен успешно")

    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        redis_client = None


async def disconnect_from_redis():
    """Отключение от Redis."""
    global redis_client
    if redis_client:
        await redis_client.close()
