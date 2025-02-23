from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete, update, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .models import PostOrm, UserOrm
from ..retry_config import db_retry


@db_retry
async def create_record(
    session: AsyncSession,
    object_name: str,
    blob_url: str,
    short_key: str,
    author_id: int,
    expires_at: Optional[datetime] = None,
):
    """Создать новую запись в базе данных."""
    new_text = PostOrm(
        name=object_name,
        blob_url=blob_url,
        short_key=short_key,
        author_id=author_id,
        expires_at=expires_at,
    )
    session.add(new_text)
    await session.flush()
    await session.refresh(new_text)
    return new_text

@db_retry
async def get_record_by_short_key(session: AsyncSession, short_key: str):
    result = await session.execute(
        select(PostOrm).where(PostOrm.short_key == short_key)
    )
    post = result.scalar()
    if post:
        await session.commit()
    return post

@db_retry
async def get_record_by_id(session: AsyncSession, post_id: int):
    result = await session.execute(
        select(PostOrm).where(PostOrm.id == post_id)
    )
    post = result.scalar()
    if post:
        await session.commit()
    return post

@db_retry
async def update_record(
    session: AsyncSession,
    short_key: str,
    post: PostOrm
):
    await session.execute(
        update(PostOrm)
        .where(PostOrm.short_key == short_key)
        .values(
            name=post.name,
            expires_at=post.expires_at,
        )
    )
    await session.commit()
    await session.refresh(post)
    return post

@db_retry
async def delete_record_by_short_key(session: AsyncSession, short_key: str):
    post = await get_record_by_short_key(session, short_key)  # Получаем запись
    if not post:
        return None
    async with session.begin():
        await session.execute(delete(PostOrm).where(PostOrm.short_key == short_key))  # Удаляем запись по short_key
    return post  # Возвращаем удалённый пост для дальнейшей обработки

async def get_records_by_user_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(PostOrm).where(PostOrm.author_id == user_id))
    return result.scalars().all()

@db_retry
async def get_expired_records_from_db(session: AsyncSession):
    """Удаляет записи с истекшим сроком действия из базы данных."""
    now = datetime.now()
    async with session.begin():
        expired_records = await session.execute(
            select(PostOrm).where(PostOrm.expires_at < now)
        )
        expired_records = expired_records.scalars().all()
    return expired_records

@db_retry
async def batch_update_views(session: AsyncSession, views: dict[str, int]):
    """Обновляет просмотры с добавлением значений из кеша через SQL-запрос."""
    query = text("""
        UPDATE posts 
        SET views_count = views_count + :v
        WHERE id = :id
    """)
    for d, v in views.items():
        await session.execute(query, {"id": int(d), "v": v})
    await session.commit()

@db_retry
async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(UserOrm).where(UserOrm.id == user_id))
    return result.scalar_one_or_none()

@db_retry
async def get_user_by_username(session: AsyncSession, username: str):
    db_user = await session.execute(select(UserOrm).where(UserOrm.username == username))
    return db_user.scalar_one_or_none()

@db_retry
async def get_user_by_email(session: AsyncSession, email: str):
    existing_user = await session.execute(select(UserOrm).where(UserOrm.email == email))
    return existing_user.scalar_one_or_none()

@db_retry
async def create_user(session: AsyncSession, username: str, email: str, hashed_password: str) -> UserOrm:
    new_user = UserOrm(username=username, email=email, hashed_password=hashed_password)
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        await session.rollback()
        raise

