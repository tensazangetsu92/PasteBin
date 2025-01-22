# services.py
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from .password_utils import hash_password, verify_password
from .postgresql.crud import get_user_by_email, create_user, get_user_by_username
from .postgresql.models import UserOrm
from .schemas import UserCreate, UserResponse
from .token_utils import create_access_token


#
# async def authenticate_user(username: str, password: str, session: AsyncSession):
#     stmt = select(UserOrm).filter(UserOrm.username == username)
#     result = await session.execute(stmt)
#     user = result.scalars().first()
#     if user and pwd_context.verify(password, user.hashed_password):
#         return user
#     raise HTTPException(status_code=400, detail="Invalid credentials")


async def register_user_service(user: UserCreate, session: AsyncSession) -> UserResponse:
    """Сервис для регистрации нового пользователя."""
    # Проверка существующего пользователя
    existing_user = await get_user_by_email(session, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Хеширование пароля и создание пользователя
    hashed_password = hash_password(user.password)
    new_user = await create_user(session, user.username, user.email, hashed_password)
    return UserResponse.from_orm(new_user)


async def login_user_service(user: UserCreate, session: AsyncSession):
    db_user = await get_user_by_username(user.username, session)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    access_token = create_access_token({"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}