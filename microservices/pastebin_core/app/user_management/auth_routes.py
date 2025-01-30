from fastapi import APIRouter, Depends, HTTPException, Response, Request
from starlette import status
from .auth_schemas import UserResponse, UserCreate, UserLogin
from .auth_services import register_user_service, login_user_service, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from ..postgresql.database import get_session


AuthRouter = APIRouter()

@AuthRouter.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        response = await register_user_service(user, session)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.post("/login")
async def login(response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)):
    try:
        access_token = await login_user_service(user, session)
        response.set_cookie(
            key="access_token",  # Название куки
            value=access_token,  # Значение куки — сам токен
            httponly=True,  # Запрещаем доступ к куке через JavaScript
            secure=False,  # Используйте True, если работаете через HTTPS
            samesite="strict",  # Для кросс-доменных запросов
            max_age=3600,  # Устанавливает время жизни куки (1 час)
        )
        return {"access_token" : access_token, "token_type": "bearer"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@AuthRouter.get("/get-current-user")
async def get_current_user_route(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        current_user = await get_current_user(request, session)  # Получаем текущего пользователя
        response = {
            "username" : current_user.username,
            "email" : current_user.email,
        }
        return response
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

