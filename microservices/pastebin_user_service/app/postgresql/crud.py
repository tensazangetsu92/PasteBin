from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservices.pastebin_user_service.app.postgresql.models import UserOrm


async def get_user_by_username(session: AsyncSession, username: str):
    db_user = await session.execute(select(UserOrm).where(UserOrm.username == username))
    return db_user.scalar_one_or_none()

async def add_user_record(session: AsyncSession):
    pass