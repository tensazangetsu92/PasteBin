from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from io import BytesIO
import json
from .postgresql.crud import get_text_by_short_key
from .postgresql.database import new_session
from .redis.redis import get_and_increment_views, cache_post
from .schemas import TextCreate
from .services import upload_file_and_save_to_db
from .yandex_bucket.storage import get_file_from_bucket
from .utils import convert_to_kilobytes
from .config import settings

router = APIRouter()

# Зависимости
async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session

async def get_current_user_id() -> int:
    return 3  # Здесь подключите JWT или другой метод авторизации


@router.post("/")
async def add_text(
    request: Request,  # Параметры без значений по умолчанию идут первыми
    text_data: TextCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        file_obj = BytesIO(text_data.text.encode("utf-8"))
        new_text = await upload_file_and_save_to_db(
            session=db,
            file_obj=file_obj,
            bucket_name=settings.BUCKET_NAME,
            object_name=text_data.name,
            author_id=current_user_id,
            expires_at=text_data.expires_at.replace(tzinfo=None),
        )
        return RedirectResponse(url=f"/api/{new_text.short_key}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.get("/{short_key}")
async def get_text(
    request: Request,  # Параметры без значений по умолчанию идут первыми
    short_key: str,
    session: AsyncSession = Depends(get_session),
):
    print('0')

    redis = request.app.state.redis  # Получение Redis из состояния приложения
    cached_post, views = await get_and_increment_views(redis, short_key)

    if cached_post:
        return json.loads(cached_post)
    print('1')
    text_record = await get_text_by_short_key(session, short_key)
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")
    print('2')
    try:
        file_data = await get_file_from_bucket(text_record.blob_url)
        response = {
            "name": text_record.name,
            "text": file_data["content"],
            "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
            "short_key": short_key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")

    if views >= settings.CACHE_VIEWS_THRESHOLD:
        await cache_post(redis, short_key, response, settings.TTL)

    return response
