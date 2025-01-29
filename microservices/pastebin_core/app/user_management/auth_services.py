from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, status, Request

from microservices.pastebin_core.app.postgresql.crud import get_user_by_email, create_user, get_user_by_username, \
    get_user_by_id
from microservices.pastebin_core.app.user_management.password_utils import hash_password, verify_password
from microservices.pastebin_core.app.user_management.token_utils import create_access_token, oauth2_scheme, \
    get_current_user_from_token
from microservices.pastebin_core.app.user_management.auth_schemas import UserCreate, UserResponse, UserLogin


async def register_user_service(user: UserCreate, session: AsyncSession) -> UserResponse:
    """Сервис для регистрации нового пользователя."""
    existing_user = await get_user_by_email(session, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    hashed_password = hash_password(user.password)
    new_user = await create_user(session, user.username, user.email, hashed_password)
    return UserResponse.from_orm(new_user)

async def login_user_service(user: UserLogin, session: AsyncSession):
    db_user = await get_user_by_username(session, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    access_token = create_access_token({"sub": str(db_user.id), "username" : db_user.username})
    return access_token

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")  # Берем токен из куки
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    try:
        user_id = get_current_user_from_token(token)
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")

# async def get_current_user(session: AsyncSession, token: str = Depends(oauth2_scheme)) -> UserResponse:
#     try:
#         user_data = await get_current_user_from_token(token)
#         user = await get_user_by_id(session, user_data["user_id"])
#         if not user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#         return user  # возвращаем данные пользователя
#
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Не удалось проверить токен",
#         )
