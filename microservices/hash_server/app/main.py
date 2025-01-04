from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from .redis import connect_to_redis, disconnect_from_redis, check_and_generate_hashes

HASH_POOL_SIZE = 100
MIN_HASH_COUNT = 100
HASH_CHECK_INTERVAL = 100

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация Redis и сохранение его в app.state
    app.state.redis = await connect_to_redis()
    scheduler.add_job(check_and_generate_hashes, 'interval', seconds=HASH_CHECK_INTERVAL, args=[app.state.redis])
    scheduler.start()
    yield
    await disconnect_from_redis(app.state.redis)

app = FastAPI(lifespan=lifespan)

@app.get("/generate_hashes")
async def generate_more_hashes(count: int = 10):
    """Принудительная генерация хешей."""
    await check_and_generate_hashes(app.state.redis)
    return {"status": "success", "generated_count": count}
