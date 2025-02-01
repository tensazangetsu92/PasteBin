from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import status
from microservices.pastebin_backend.app.config import settings


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

def get_current_user_id(request: Request):
    token = request.cookies.get("access_token")  # Берем токен из куки
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
    try:
        # Декодируем токен
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")  # Извлекаем идентификатор пользователя из payload
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка при проверке токена")
