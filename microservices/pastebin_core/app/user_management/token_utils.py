from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import status
from microservices.pastebin_core.app.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_token(token: str = Depends(oauth2_scheme)):
    return token

def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    """
    Получить данные пользователя из токена.
    :param token: JWT-токен.
    :return: Данные пользователя (user_id, username).
    :raises HTTPException: Если токен недействителен.
    """
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
        )
    return {"user_id": user_id}

def create_access_token(data: dict):
    """
    Создает JWT-токен.

    :param data: Данные, которые нужно закодировать в токен.
    :return: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """
    Декодирует JWT-токен и проверяет его валидность.

    :param token: JWT-токен.
    :return: Декодированные данные из токена.
    :raises HTTPException: Если токен недействителен или истёк.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
