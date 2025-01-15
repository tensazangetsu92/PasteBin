from fastapi import FastAPI
from contextlib import asynccontextmanager
from .postgresql.database import create_tables, delete_tables, new_session
from .redis.redis import connect_to_redis, disconnect_from_redis
from .scheduler import start_scheduler, terminate_scheduler
from .middlewares import setup_cors
from .config import settings
from .routes import router  # Импорт маршрутов

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
setup_cors(app)

# Подключение маршрутов
app.include_router(router, prefix="/api", tags=["PasteBin"])
