from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from redis.commands.search.reducers import random_sample
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from .postgresql.database import async_session, get_session
from .services import (
    add_post_service,
    get_text_service,
    get_popular_posts_service, get_user_posts_service,
)
from .schemas import PostCreate, PopularPostsResponse
from .user_management.token_utils import get_current_user_id

PostsRouter = APIRouter()



@PostsRouter.post("/add-post")
async def add_post(
    text_data: PostCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        return await add_post_service(text_data, db, current_user_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@PostsRouter.post("/get-popular-posts", response_model=PopularPostsResponse)
async def get_popular_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_popular_posts_service(request, session)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@PostsRouter.get("/get-post/{short_key}")
async def get_text(
    request: Request,
    short_key: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_id = Depends(get_current_user_id),
):
    try:
        return await get_text_service(request, short_key, session, background_tasks)
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@PostsRouter.post("/get-user-posts")
async def get_user_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user_id = Depends(get_current_user_id),
):
    try:
        return await get_user_posts_service(request, session, user_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")