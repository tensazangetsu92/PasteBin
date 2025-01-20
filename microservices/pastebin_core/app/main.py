from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from starlette.responses import JSONResponse

from .postgresql.database import create_tables, delete_tables, new_session
from .redis.redis import connect_to_redis, disconnect_from_redis
from .scheduler import start_scheduler, terminate_scheduler
from .middlewares import setup_cors
from .routes import router  # Импорт маршрутов

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    await create_tables()
    app.state.redis = await connect_to_redis()
    async with new_session() as session:
        start_scheduler(session)
    yield
    terminate_scheduler()
    await disconnect_from_redis(app.state.redis)

app = FastAPI(lifespan=lifespan)
setup_cors(app)
app.include_router(router, prefix="/api", tags=["PasteBin"])

@app.exception_handler(HTTPException)
async def validation_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )
