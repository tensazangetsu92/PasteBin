from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from microservices.pastebin_backend.app.config import settings
from microservices.pastebin_backend.app.postgresql.crud import get_expired_records_from_db, \
     batch_update_views, delete_record_by_short_key
from microservices.pastebin_backend.app.redis.redis import get_all_keys_sorted_set, delete_key_sorted_set, \
    update_score_sorted_set, delete_post_cache, delete_all_keys_from_sorted_set
from microservices.pastebin_backend.app.yandex_bucket.storage import delete_file_from_bucket

scheduler = AsyncIOScheduler()

def start_scheduler(async_session: AsyncSession, redis: Redis):
    """Настраивает и запускает планировщик."""
    # scheduler.add_job(delete_expired_records, 'interval', seconds=settings.CLEANUP_EXP_POSTS_INTERVAL, args=[redis,async_session])
    scheduler.add_job(sync_views, 'interval', seconds=settings.SYNC_VIEWS_INTERVAL, args=[redis, async_session])
    # scheduler.add_job(decrement_scores, 'interval', seconds=settings.DECREMENT_RECENT_VIEWS_INTERVAL, args=[redis])
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
        print("Устаревшие записи удалены")
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")

async def sync_views(redis_client: Redis, session: AsyncSession):
    """Синхронизирует просмотры из Redis в БД одним batch-запросом."""
    views = await get_all_keys_sorted_set(redis_client, settings.SORTED_SET_VIEWS)
    if not views: return
    views_dict = {k: int(v) for k, v in views}  # Преобразуем в dict
    await batch_update_views(session, views_dict)
    await delete_all_keys_from_sorted_set(redis_client, settings.SORTED_SET_VIEWS)


# async def decrement_scores(redis: Redis):
#     """Уменьшает баллы всех элементов в sorted_set на 1 и удаляет элементы с нулевым баллом."""
#     keys = await get_all_keys_sorted_set(redis, settings.SORTED_SET_VIEWS)
#     for key, score in keys:
#         new_score = score - 1
#         if new_score <= 0:
#             await delete_key_sorted_set(redis, settings.SORTED_SET_VIEWS, key)
#         else:
#             await update_score_sorted_set(redis, settings.SORTED_SET_VIEWS, key, new_score)