from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collections import deque
import secrets
from .config import settings

hash_pool = deque()

scheduler = AsyncIOScheduler()

def generate_hashes(count: int) -> None:
    """Генерация хэшей и сохранение их в памяти."""
    global hash_pool
    hashes = [secrets.token_urlsafe(8)[:8] for _ in range(count)]
    hash_pool.extend(hashes)

def check_and_generate_hashes(min_count: int, generate_count: int) -> None:
    """Проверка количества хэшей в памяти и добавление новых, если их меньше минимального порога."""
    global hash_pool
    if len(hash_pool) < min_count:
        generate_hashes(generate_count)

def pop_hash() -> str | None:
    """Извлечение хэша из памяти."""
    global hash_pool
    return hash_pool.popleft() if hash_pool else None

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(check_and_generate_hashes, 'interval', seconds=settings.HASH_CHECK_INTERVAL, args=[settings.MIN_HASH_COUNT, settings.HASH_POOL_SIZE])
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/generate_hashes")
def generate_more_hashes(count: int = 10):
    """Принудительная генерация хэшей."""
    generate_hashes(count)
    return {"status": "success", "generated_count": count}

@app.get("/get_hash")
def get_hash():
    """Получение хэша из памяти."""
    hash_value = pop_hash()
    if hash_value:
        return {"hash": hash_value}
    return {"error": "No hash available"}
