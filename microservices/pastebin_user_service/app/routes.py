from fastapi import APIRouter, Depends, HTTPException
from .postgresql.crud import get_user_by_email
from .postgresql.database import get_session
from .postgresql.models import UserOrm
from .schemas import UserCreate, UserResponse
from .services import create_user, authenticate_user, register_user_service
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
    user = await authenticate_user(user.username, user.password, session)
    return {"access_token": "fake_jwt_token", "token_type": "bearer"}
