from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from .postgresql.database import new_session, get_session
from .services import (
    add_post_service,
    get_text_service,
    get_popular_posts_service,
)
from .schemas import PostCreate, PopularPostsResponse
from .user_management.auth_services import get_current_user

PostsRouter = APIRouter()



async def get_current_user_id() -> int:
    return 1  # Здесь подключите JWT или другой метод авторизации

@PostsRouter.post("/add-post")
async def add_post(
    text_data: PostCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        new_text = await add_post_service(
            text_data=text_data,
            db=db,
            current_user_id=current_user_id,
        )
        return RedirectResponse(url=f"/api/get-post:{new_text.short_key}", status_code=303)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@PostsRouter.post("/get-popular-posts", response_model=PopularPostsResponse)
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

@PostsRouter.get("/get-post/{short_key}")
async def get_text(
    request: Request,
    short_key: str,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    try:
        print(user)
        response = await get_text_service(request, short_key, session)
        return response
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

