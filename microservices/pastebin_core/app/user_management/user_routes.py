from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from .user_schemas import UserResponse, UserCreate
from .user_services import register_user_service, login_user_service
from sqlalchemy.ext.asyncio import AsyncSession
from ..postgresql.database import get_session

UsersRouter = APIRouter()


@UsersRouter.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        response = register_user_service(user, session)
        return response
    except Exception as e:
        return e

@UsersRouter.post("/login")
async def login(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        access_token = await login_user_service(user, session)
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Strict"
        )
        return response
    except Exception as e:
        return e