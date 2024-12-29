from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from .database import create_tables, delete_tables, new_session
from .scheduler import start_scheduler
from .schemas import TextCreate
from .services import upload_file_and_save_to_db

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

        # Парсим дату истечения срока, если указана
        # expires_at_parsed = (
        #     text_data.expires_at
        #     if isinstance(text_data.expires_at, datetime)  # Если уже datetime, оставляем как есть
        #     else datetime.strptime(text_data.expires_at, "%Y-%m-%d")  # Иначе парсим из строки
        # )

        # Генерация имени файла в бакете
        object_name = f"{current_user_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"

        # Преобразуем текст в файл-like объект
        file_obj = BytesIO(text_data.text.encode("utf-8"))

        # Вызов функции для загрузки файла и записи в БД
        new_text = await upload_file_and_save_to_db(
            session=db,
            file_obj=file_obj,
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            author_id=current_user_id,
            expires_at=text_data.expires_at.replace(tzinfo=None),
        )
        return {"short_key": new_text.short_key, "url": new_text.blob_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
