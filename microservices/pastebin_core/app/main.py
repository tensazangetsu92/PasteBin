from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from .crud import get_text_by_short_key
from .database import create_tables, delete_tables, new_session
from .scheduler import start_scheduler
from .schemas import TextCreate
from .services import upload_file_and_save_to_db
from .storage import get_file_from_bucket, get_file_size_from_bucket
from .utils import convert_to_kilobytes
from fastapi.responses import RedirectResponse

BUCKET_NAME = "texts"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    await create_tables()
    # Создаём сессию вручную
    async with new_session() as session:
        # Запускаем планировщик
        start_scheduler(session)
    yield

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
            file_obj=file_obj,
            bucket_name=BUCKET_NAME,
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
    text_record = await get_text_by_short_key(session, short_key)
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")

    try:
        text_content = await get_file_from_bucket(text_record.blob_url)
        text_size_in_bytes = await get_file_size_from_bucket(text_record.blob_url)
        text_size_in_kilobytes = convert_to_kilobytes(text_size_in_bytes)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving text: {e}")

    return {
        "name": text_record.name,
        "text": text_content,
        "text_size": text_size_in_kilobytes,
    }


