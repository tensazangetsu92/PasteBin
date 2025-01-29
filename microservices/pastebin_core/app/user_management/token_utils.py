import json

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import status
from microservices.pastebin_core.app.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def create_access_token(to_encode: dict):
    """
    Создает JWT-токен.

    :param data: Данные, которые нужно закодировать в токен.
    :return: Закодированный JWT-токен.
    """
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except JWTError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_from_token(token: str):
    """
    Получить данные пользователя из токена.
    :param token: JWT-токен.
    :return: Данные пользователя (user_id, username).
    :raises HTTPException: Если токен недействителен.
    """
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )
        return user_id
    except Exception as e:
        print(e)

