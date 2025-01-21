from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from starlette.responses import JSONResponse

from .postgresql.database import create_tables, delete_tables, new_session
from .routes import router  # Импорт маршрутов

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/users", tags=["users"])

@app.exception_handler(HTTPException)
async def validation_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )
