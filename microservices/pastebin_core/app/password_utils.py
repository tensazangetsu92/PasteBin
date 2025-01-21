from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хэширует пароль."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(password, hashed_password)
