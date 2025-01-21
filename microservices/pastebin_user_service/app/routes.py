# routes.py
from fastapi import APIRouter, Depends
from .schemas import UserCreate, UserResponse
from .services import create_user, authenticate_user
from sqlalchemy.ext.asyncio import AsyncSession
from postgresql.database import new_session

router = APIRouter()

async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    return await create_user(user, session)

@router.post("/login")
async def login(user: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(user.username, user.password, session)
    return {"access_token": "fake_jwt_token", "token_type": "bearer"}
