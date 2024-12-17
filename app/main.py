from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TextCreate, TextResponse
from .services import create_text
from .database import async_sessionmaker

app = FastAPI()

async def get_db() -> AsyncSession:
    async with async_sessionmaker() as session:
        yield session

@app.post("/", response_model=TextResponse)
async def add_text(
    text_data: TextCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        new_text = await create_text(
            session=db,
            blob_url=text_data.blob_url,
            author_id=text_data.current_user_id,
            expires_at=text_data.expires_at,
        )
        return new_text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
