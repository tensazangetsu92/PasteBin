from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from microservices.pastebin_backend.app.config import settings
from microservices.pastebin_backend.app.postgresql.crud import get_expired_records_from_db, \
    delete_record_and_file, batch_update_views
from microservices.pastebin_backend.app.redis.redis import get_all_keys_sorted_set, delete_key_sorted_set, \
                                                            update_score_sorted_set, delete_post_cache


scheduler = AsyncIOScheduler()

def start_scheduler(async_session: AsyncSession, redis: Redis):
    """Настраивает и запускает планировщик."""
    # scheduler.add_job(delete_expired_records, 'interval', seconds=settings.CLEANUP_EXP_POSTS_INTERVAL, args=[async_session])
    # scheduler.add_job(sync_views, 'interval', seconds=settings.SYNC_VIEWS_INTERVAL, args=[redis, async_session])
    # scheduler.add_job(decrement_scores, 'interval', seconds=settings.DECREMENT_RECENT_VIEWS_INTERVAL, args=[redis])
    scheduler.start()
    # print("Планировщик запущен")

def terminate_scheduler():
    scheduler.shutdown()


async def delete_expired_records(session: AsyncSession):
    """Функция для удаления просроченных записей."""
    try:
        expired_records = await get_expired_records_from_db(session)
        for record in expired_records:
            await delete_post_cache()
            await delete_record_and_file(session, record)
        print("Устаревшие записи удалены")
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")

async def sync_views(redis, session: AsyncSession):
    """Синхронизирует просмотры из Redis в БД одним batch-запросом."""
    views = await get_all_keys_sorted_set(redis, settings.SORTED_SET_VIEWS)
    if not views: return
    await batch_update_views(session, views)
    await clear_views_from_cache(redis, views.keys())


# async def decrement_scores(redis: Redis):
#     """Уменьшает баллы всех элементов в sorted_set на 1 и удаляет элементы с нулевым баллом."""
#     keys = await get_all_keys_sorted_set(redis, settings.SORTED_SET_VIEWS)
#     for key, score in keys:
#         new_score = score - 1
#         if new_score <= 0:
#             await delete_key_sorted_set(redis, settings.SORTED_SET_VIEWS, key)
#         else:
#             await update_score_sorted_set(redis, settings.SORTED_SET_VIEWS, key, new_score)