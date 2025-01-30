from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse
from .postgresql.database import create_tables, delete_tables, async_session
from .redis.redis import connect_to_redis, disconnect_from_redis
from .scheduler import start_scheduler, terminate_scheduler
from .middlewares import setup_cors
from .routes import PostsRouter
from .user_management.auth_routes import AuthRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    await create_tables()
    app.state.redis = await connect_to_redis()
    async with async_session() as session:
        start_scheduler(session, app.state.redis)
    yield
    terminate_scheduler()
    await disconnect_from_redis(app.state.redis)

app = FastAPI(lifespan=lifespan)
setup_cors(app)
app.include_router(PostsRouter, prefix="/api", tags=["PasteBin"])
app.include_router(AuthRouter, prefix="/api", tags=["registration and login"])

@app.exception_handler(HTTPException)
async def validation_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )
