from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from .postgresql.crud import get_user_by_email
from .postgresql.database import get_session
from .postgresql.models import UserOrm
from .schemas import UserCreate, UserResponse
from .services import create_user, register_user_service, login_user_service
from sqlalchemy.ext.asyncio import AsyncSession
from .password_utils import hash_password

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        response = register_user_service(user, session)
        return response
    except Exception as e:
        return e

@router.post("/login")
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