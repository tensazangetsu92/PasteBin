from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request
from fastapi import Response
from ..postgresql_db.crud import get_user_by_email, create_user, get_user_by_username, \
    get_user_by_id
from ..user_management.password_utils import hash_password, verify_password
from ..user_management.token_utils import create_access_token, get_current_user_id
from ..schemas.auth_schemas import UserCreate, UserResponse, UserLogin


async def register_user_service(user: UserCreate, session: AsyncSession) -> UserResponse:
    existing_user = await get_user_by_email(session, str(user.email))
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_password = hash_password(user.password)
    new_user = await create_user(session, user.username, str(user.email), hashed_password)
    return UserResponse.model_validate(new_user)

async def login_user_service(user: UserLogin, session: AsyncSession, response: Response):
    db_user = await get_user_by_username(session, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    access_token = create_access_token({"sub": str(db_user.id), "username" : db_user.username})
    response.set_cookie(
        key="access_token",  # Название куки
        value=access_token,  # Значение куки — сам токен
        httponly=True,  # Запрещаем доступ к куке через JavaScript
        secure=False,  # Используйте True, если работаете через HTTPS
        samesite="strict",  # Для кросс-доменных запросов
        max_age=3600,  # Устанавливает время жизни куки (1 час)
    )
    return {"access_token" : access_token, "token_type": "bearer"}

async def get_current_user_service(request: Request, session: AsyncSession):
    user_id = get_current_user_id(request)
    user_data = await get_user_by_id(session, user_id)
    response = {
        "username": user_data.username,
        "email": user_data.email,
    }
    return response

