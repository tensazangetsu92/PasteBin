import secrets
import time
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from microservices.hash_server.app.redis_client import connect_to_redis, disconnect_from_redis, redis_client
# from microservices.hash_server.app.scheduler import start_scheduler

# Количество хешей для генерации
HASH_POOL_SIZE = 100
MIN_HASH_COUNT = 100  # Минимальное количество хешей в очереди

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_redis()
    scheduler.add_job(check_and_generate_hashes, 'interval', seconds=1)
    scheduler.start()
    yield
    await disconnect_from_redis()

app = FastAPI(lifespan=lifespan)

def generate_hash(length: int = 8) -> str:
    """Генерация уникального короткого ключа."""
    return secrets.token_urlsafe(length)[:length]

async def generate_hashes(count: int) -> None:
    """Генерация хешей и сохранение их в Redis."""
    hashes = [generate_hash() for _ in range(count)]
    # Сохраняем хеши в Redis
    await redis_client.lpush("hash_pool", *hashes)  # Добавляем все хеши в очередь Redis

async def check_and_generate_hashes() -> None:
    """Проверка количества хешей в Redis и добавление новых, если их меньше минимального порога."""
    hash_count = await redis_client.llen("hash_pool")
    if hash_count < MIN_HASH_COUNT:
        await generate_hashes(HASH_POOL_SIZE)


# @app.get("/health")
# async def health_check():
#     """Проверка состояния сервиса и Redis."""
#     try:
#         if await redis.ping():
#             return {"status": "ok", "redis": "connected"}
#     except Exception as e:
#         return {"status": "error", "error": str(e)}

@app.get("/generate_hashes")
async def generate_more_hashes(count: int = 10):
    """Принудительная генерация хешей."""
    await generate_hashes(count)
    return {"status": "success", "generated_count": count}

# @app.get("/get_hash")
# async def get_hash():
#     """Получение хешей из Redis."""
#     await check_and_generate_hashes()  # Проверяем, если нужно, генерируем хеши
#     hash = await redis.rpop("hash_pool")
#     if hash:
#         return {"hash": hash}
#     return {"error": "No hash available"}
