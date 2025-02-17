import asyncio
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from microservices.pastebin_backend.app.config import settings
from microservices.pastebin_backend.app.postgresql_db.crud import get_expired_records_from_db, \
    batch_update_views, delete_record_by_short_key, get_record_by_id, get_record_by_short_key
from microservices.pastebin_backend.app.postgresql_db.database import async_session
from microservices.pastebin_backend.app.redis_cache.cache import get_all_keys_sorted_set, delete_key_sorted_set, \
    update_score_sorted_set, delete_post_cache, delete_all_keys_from_sorted_set, get_popular_posts_keys
from microservices.pastebin_backend.app.utils import get_post_age, convert_to_kilobytes
from microservices.pastebin_backend.app.yandex_bucket.storage import delete_file_from_bucket, get_file_from_bucket

scheduler = AsyncIOScheduler()

def start_scheduler(async_session: AsyncSession, redis: Redis):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=settings.CLEANUP_EXP_POSTS_INTERVAL, args=[redis,async_session])
    scheduler.add_job(sync_views, 'interval', seconds=settings.SYNC_VIEWS_INTERVAL, args=[redis, async_session])
    scheduler.add_job(collect_most_popular_posts, 'interval', seconds=settings.COLLECT_MOST_POPULAR_POSTS_INTERVAL, args=[redis])
    scheduler.start()
    # print("Планировщик запущен")

def terminate_scheduler():
    scheduler.shutdown()

async def delete_expired_records(redis_client: Redis, session: AsyncSession):
    """Функция для удаления просроченных записей."""
    try:
        expired_records = await get_expired_records_from_db(session)
        for record in expired_records:
            await delete_post_cache(redis_client, record.short_key, record.id, settings.SORTED_SET_VIEWS)
            await delete_file_from_bucket("texts", record.author_id, record.short_key)
            await delete_record_by_short_key(session, record.short_key)
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")

async def sync_views(redis_client: Redis, session: AsyncSession):
    """Синхронизирует просмотры из Redis в БД одним batch-запросом."""
    views = await get_all_keys_sorted_set(redis_client, settings.SORTED_SET_VIEWS)
    if not views: return
    views_dict = {k: int(v) for k, v in views}  # Преобразуем в dict
    await batch_update_views(session, views_dict)
    await delete_all_keys_from_sorted_set(redis_client, settings.SORTED_SET_VIEWS)

async def collect_most_popular_posts(redis_client: Redis):
    post_ids = await get_popular_posts_keys(redis_client, settings.SORTED_SET_VIEWS)
    async def fetch_post(post_key):
        short_key = post_key.split(":")[1]
        async with async_session() as new_session:
            text_record = await get_record_by_short_key(new_session, short_key)
            if not text_record:
                return None
            file_data = await get_file_from_bucket(text_record.blob_url)
            return {
                "name": text_record.name,
                "text_size_kilobytes": convert_to_kilobytes(file_data["size"]),
                "short_key": text_record.short_key,
                "created_at": text_record.created_at.isoformat(),
                "expires_at": text_record.expires_at.isoformat(),
            }

    posts = await asyncio.gather(*(fetch_post(post_id) for post_id in post_ids))
    posts = [post for post in posts if post]  # Фильтруем None значения
    await redis_client.set(f"most_popular_posts", json.dumps(posts))
