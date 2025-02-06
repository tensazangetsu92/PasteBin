from datetime import datetime

import httpx
from fastapi import HTTPException

from microservices.pastebin_backend.app.config import settings


async def get_hash() -> str:
    """Получение хэша от хэш-сервера через HTTP-запрос."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.HASH_SERVER_URL)
            if response.status_code == 200:
                data = response.json()
                if "hash" in data:
                    return data["hash"]
            raise ValueError("Failed to fetch hash from hash server")
    except httpx.RequestError as req_err:
        raise HTTPException(503, f"Failed to fetch hash from hash server: {req_err}")

def parse_blob_url(blob_url: str) -> tuple[str, str]:
    """Разбор URL, чтобы получить имя бакета и объект."""
    url_parts = blob_url.replace("https://storage.yandexcloud.net/", "").split("/", 1)
    return url_parts[0], url_parts[1]

def convert_to_kilobytes(byte_count: int):
    return round(byte_count / 1024, 2)

def get_post_age(created_at: datetime):
    """Получить сколько секунд/минут/часов/дней назад был создан пост"""
    time_difference = datetime.now() - created_at
    if time_difference.days > 0:
        creation_time = f"{time_difference.days} дней назад"
    elif time_difference.seconds >= 3600:
        creation_time = f"{time_difference.seconds // 3600} часов назад"
    elif time_difference.seconds >= 60:
        creation_time = f"{time_difference.seconds // 60} минут назад"
    else:
        creation_time = f"{time_difference.seconds} секунд назад"
    return creation_time

