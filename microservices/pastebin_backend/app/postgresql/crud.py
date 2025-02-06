from datetime import datetime
from typing import Optional
from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_backend.app.postgresql.models import PostOrm, UserOrm
from microservices.pastebin_backend.app.schemas import PostUpdate
from microservices.pastebin_backend.app.yandex_bucket.storage import delete_file_from_bucket, upload_file_to_bucket


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

async def get_record_by_short_key(session: AsyncSession, short_key: str):
    result = await session.execute(
        select(PostOrm).where(PostOrm.short_key == short_key)
    )
    post = result.scalar()
    if post:
        post.views_count += 1
        await session.commit()
    return post

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

async def get_expired_records_from_db(session: AsyncSession):
    """Удаляет записи с истекшим сроком действия из базы данных."""
    now = datetime.now()
    async with session.begin():
        expired_records = await session.execute(
            select(PostOrm).where(PostOrm.expires_at < now)
        )
        expired_records = expired_records.scalars().all()
    return expired_records

async def delete_record_and_file(session: AsyncSession, record: PostOrm):
    """Удаляет запись и файл из бакета."""
    await delete_file_from_bucket("texts", record.author_id, record.short_key)  # Удаление файла
    async with session.begin():
        await session.execute(delete(PostOrm).where(PostOrm.id == record.id))  # Удаление записи из базы данных

async def update_record_views_in_db(session: AsyncSession, post_id: str, views_count: int):
    """Прибавляет количество просмотров к существующему значению в базе данных."""
    async with session.begin():
        await session.execute(
            update(PostOrm)
            .where(PostOrm.short_key == post_id)
            .values(views_count=PostOrm.views_count + views_count)
        )


async def get_user_by_id(session: AsyncSession, user_id: int):
    result = await session.execute(select(UserOrm).where(UserOrm.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str):
    db_user = await session.execute(select(UserOrm).where(UserOrm.username == username))
    return db_user.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str):
    existing_user = await session.execute(select(UserOrm).where(UserOrm.email == email))
    return existing_user.scalar_one_or_none()

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

