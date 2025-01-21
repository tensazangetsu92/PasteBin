from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from microservices.pastebin_core.app.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

class Base(DeclarativeBase):
    pass
