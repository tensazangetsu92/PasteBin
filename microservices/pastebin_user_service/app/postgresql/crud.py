from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_user_service.app.postgresql.models import UserOrm


async def get_user_by_username(session: AsyncSession, username: str):
    db_user = await session.execute(select(UserOrm).where(UserOrm.username == username))
    return db_user.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str):
    existing_user = await session.execute(select(UserOrm).where(UserOrm.email == email))
    return existing_user.scalar_one_or_none()

async def create_user(session: AsyncSession, username: str, email: str, hashed_password: str) -> UserOrm:
    """Создать нового пользователя."""
    new_user = UserOrm(username=username, email=email, hashed_password=hashed_password)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        await session.rollback()
        raise
