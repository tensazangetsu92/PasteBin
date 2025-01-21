# services.py
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from postgresql.models import UserOrm
from .schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate, session: AsyncSession):
    hashed_password = pwd_context.hash(user.password)
    new_user = UserOrm(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def authenticate_user(username: str, password: str, session: AsyncSession):
    stmt = select(UserOrm).filter(UserOrm.username == username)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    raise HTTPException(status_code=400, detail="Invalid credentials")
