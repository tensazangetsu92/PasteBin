from fastapi import APIRouter, Depends, HTTPException, Response, Request
from starlette import status
from ..schemas.auth_schemas import UserResponse, UserCreate, UserLogin
from ..services.auth_services import register_user_service, login_user_service, get_current_user_service
from sqlalchemy.ext.asyncio import AsyncSession
from ..postgresql_db.database import get_async_session
from ..logger import logger

auth_router = APIRouter()

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Attempt to register user: {user.email}")
    try:
        result = await register_user_service(user, session)
        logger.info(f"User {user.email} registered successfully")
        return result
    except Exception as e:
        logger.error(f"Registration error for {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/login")
async def login(response: Response, user: UserLogin, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"User {user.username} attempting to log in")
    try:
        result = await login_user_service(user, session, response)
        logger.info(f"User {user.username} logged in successfully")
        return result
    except Exception as e:
        logger.error(f"Login error for {user.username}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.get("/get-current-user")
async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Fetching current user for request {request.client.host}")
    try:
        result = await get_current_user_service(request, session)
        logger.info(f"Current user retrieved: {result}")
        return result
    except Exception as e:
        logger.error(f"Error fetching current user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/logout")
async def logout(response: Response):
    logger.info(f"Logging out user")
    try:
        response.delete_cookie("access_token")  # Удаляем куки с токеном
        logger.info(f"User logged out successfully")
        return {"detail": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

