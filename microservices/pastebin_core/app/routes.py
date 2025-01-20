from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from .postgresql.database import new_session
from .services import (
    add_post_service,
    get_text_service,
    get_popular_posts_service,
)
from .schemas import TextCreate, PopularPostsResponse

router = APIRouter()

async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session

async def get_current_user_id() -> int:
    return 3  # Здесь подключите JWT или другой метод авторизации

@router.post("/add_post")
async def add_post(
    text_data: TextCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        new_text = await add_post_service(
            text_data=text_data,
            db=db,
            current_user_id=current_user_id,
        )
        return RedirectResponse(url=f"/api/{new_text.short_key}", status_code=303)
    except Exception as e:
        raise e


@router.post("/get_popular_posts")
async def get_popular_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        response = await get_popular_posts_service(request, session)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@router.get("/{short_key}")
async def get_text(
    request: Request,
    short_key: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        response = await get_text_service(request, short_key, session)
        return response
    except HTTPException as e:
        raise e