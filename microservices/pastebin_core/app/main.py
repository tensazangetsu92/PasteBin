import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from microservices.pastebin_core.app.postgresql.crud import get_text_by_short_key
from microservices.pastebin_core.app.postgresql.database import create_tables, new_session, delete_tables
from .redis.redis import connect_to_redis, disconnect_from_redis, get_and_increment_views, cache_post
from .scheduler import start_scheduler, terminate_scheduler
from .schemas import TextCreate
from .services import upload_file_and_save_to_db
from microservices.pastebin_core.app.yandex_bucket.storage import get_file_from_bucket
from .utils import convert_to_kilobytes
from fastapi.responses import RedirectResponse
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    app.state.redis = await connect_to_redis()
    async with new_session() as session:
        start_scheduler(session)
    yield
    terminate_scheduler()
    await disconnect_from_redis(app.state.redis)

app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session

async def get_current_user_id() -> int:
    return 3  # Здесь подключите JWT или другой метод авторизации



@app.post("/")
async def add_text(
    text_data: TextCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        file_obj = BytesIO(text_data.text.encode("utf-8"))
        new_text = await upload_file_and_save_to_db(
            session=db,
            # redis_client=app.state.redis,
            file_obj=file_obj,
            bucket_name=settings.BUCKET_NAME,
            object_name=text_data.name,
            author_id=current_user_id,
            expires_at=text_data.expires_at.replace(tzinfo=None),
        )
        return RedirectResponse(url=f"/{new_text.short_key}", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@app.get("/{short_key}")
async def get_text(
        short_key: str, session:
        AsyncSession = Depends(get_session)
):
    cached_post, views = await get_and_increment_views(app.state.redis, short_key)

    if cached_post:
        print("CACHE")
        return json.loads(cached_post)
    print("DB")
    text_record = await get_text_by_short_key(session, short_key)
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")

    try:
        file_data = await get_file_from_bucket(text_record.blob_url)
        response = {
            "name": text_record.name,
            "text": file_data["content"],
            "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
            "short_key" : short_key,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")

    if views >= settings.CACHE_VIEWS_THRESHOLD:
        await cache_post(app.state.redis, short_key, response, settings.TTL)

    return response