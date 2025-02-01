from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from .postgresql.database import get_session
from .services import (
    add_post_service,
    get_text_service,
    get_popular_posts_service,
    get_user_posts_service,
)
from .schemas import PostCreate, PopularPostsResponse
from .user_management.token_utils import get_current_user_id
from .logger import logger

PostsRouter = APIRouter()

@PostsRouter.post("/add-post")
async def add_post(
    text_data: PostCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    logger.info(f"User {current_user_id} is adding a post: {text_data}")
    try:
        result = await add_post_service(text_data, db, current_user_id)
        logger.info(f"Post added successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error adding post: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@PostsRouter.get("/get-popular-posts", response_model=PopularPostsResponse)
async def get_popular_posts(request: Request, session: AsyncSession = Depends(get_session)):
    logger.info(f"Fetching popular posts from {request.client.host}")
    try:
        return await get_popular_posts_service(request, session)
    except Exception as e:
        logger.error(f"Error fetching popular posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@PostsRouter.get("/get-post/{short_key}")
async def get_text(
    request: Request,
    short_key: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    logger.info(f"User {user_id} is fetching post: {short_key}")
    try:
        return await get_text_service(request, short_key, session, background_tasks)
    except HTTPException as e:
        logger.warning(f"Post {short_key} not found: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching post {short_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@PostsRouter.get("/get-user-posts")
async def get_user_posts(request: Request, session: AsyncSession = Depends(get_session), user_id: int = Depends(get_current_user_id)):
    logger.info(f"Fetching posts for user {user_id}")
    try:
        return await get_user_posts_service(request, session, user_id)
    except Exception as e:
        logger.error(f"Error fetching user posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
