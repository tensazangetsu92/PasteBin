from jose import jwt
from datetime import datetime, timedelta
from microservices.pastebin_user_service.app.config import settings


def create_access_token(data: dict):
    """
    Создает JWT-токен.

    :param data: Данные, которые нужно закодировать в токен.
    :return: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)



