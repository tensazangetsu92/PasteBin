import hashlib
import secrets
from fastapi import FastAPI
from typing import List
from concurrent.futures import ThreadPoolExecutor
import asyncio
from collections import deque

# Количество хешей для генерации
HASH_POOL_SIZE = 100

# Кеш для хешей
hash_cache = deque(maxlen=HASH_POOL_SIZE)

# Настройка многозадачности
executor = ThreadPoolExecutor(max_workers=10)

app = FastAPI()

def generate_hash() -> str:
    """Генерация хеша."""
    return hashlib.sha256(secrets.token_bytes(32)).hexdigest()

def generate_hashes(count: int) -> List[str]:
    """Генерация нескольких хешей и сохранение их в кеш."""
    hashes = [generate_hash() for _ in range(count)]
    hash_cache.extend(hashes)
    return hashes

@app.on_event("startup")
async def startup():
    """Запуск генерации хешей при старте сервера."""
    await asyncio.to_thread(generate_hashes, HASH_POOL_SIZE)

@app.get("/get_hash")
async def get_hash():
    """Получение хеша из кеша."""
    if not hash_cache:
        await asyncio.to_thread(generate_hashes, HASH_POOL_SIZE)
    return {"hash": hash_cache.popleft()}
