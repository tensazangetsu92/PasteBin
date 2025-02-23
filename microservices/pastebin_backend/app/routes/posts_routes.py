from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ..postgresql_db.database import get_async_session
from ..services.posts_services import (
    add_post_service,
    get_post_service,
    get_popular_posts_service,
    get_user_posts_service, delete_post_service, update_post_service,
)
from ..schemas.posts_schemas import PostCreate, PopularPostsResponse, PostUpdate, GetPostResponse, UserPostsResponse
from ..user_management.token_utils import get_current_user_id
from ..logger import logger

posts_router = APIRouter()

@posts_router.post("/add-post")
async def add_post(
    text_data: PostCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user_id),
):
    logger.info(f"User {user_id} is adding a post: {text_data}")
    try:
        result = await add_post_service(text_data, db, user_id)
        logger.info(f"Post added successfully: {result}")
    except Exception as e:
        logger.error(f"Error adding post: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@posts_router.get("/get-post/{short_key}", response_model=GetPostResponse)
async def get_post(
    request: Request,
    short_key: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user_id),
):
    logger.info(f"User {user_id} is fetching post: {short_key}")
    try:
        return await get_post_service(request, short_key, session, background_tasks)
    except HTTPException as e:
        logger.warning(f"Post {short_key} not found: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching post {short_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@posts_router.get("/get-popular-posts", response_model=PopularPostsResponse)
async def get_popular_posts(request: Request):
    logger.info(f"Fetching popular posts from {request.client.host}")
    try:
        return await get_popular_posts_service(request)
    except Exception as e:
        logger.error(f"Error fetching popular posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@posts_router.get("/get-user-posts", response_model=UserPostsResponse)
async def get_user_posts(session: AsyncSession = Depends(get_async_session), user_id: int = Depends(get_current_user_id)):
    logger.info(f"Fetching posts for user {user_id}")
    try:
        return await get_user_posts_service(session, user_id)
    except Exception as e:
        logger.error(f"Error fetching user posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@posts_router.delete("/delete-post/{short_key}")
async def delete_post(
        request: Request,
        short_key: str,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_async_session),
        user_id: int = Depends(get_current_user_id),
):
    try:
        post = await delete_post_service(short_key, request, session, background_tasks)
        logger.info(f"User {user_id} is deleting a post: {post}")
        return {"message": "Post deleted successfully"}
    except HTTPException as e:
        logger.error(f"Error deleting post: {e}", exc_info=True)
        raise e

@posts_router.patch("/update-post/{short_key}")
async def update_post(
        short_key: str,
        post_data: PostUpdate,
        request: Request,
        db: AsyncSession = Depends(get_async_session),
        user_id: int = Depends(get_current_user_id),
):
    logger.info(f"User {user_id} is updating a post: {short_key} with data: {post_data}")
    try:
        updated_post = await update_post_service(short_key, post_data, request, db, user_id)
        logger.info(f"Post updated successfully: {updated_post}")
        return {"message": "Post updated successfully", "post": updated_post}

    except Exception as e:
        logger.error(f"Error updating post {short_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")