from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from microservices.pastebin_core.app.config import settings
from microservices.pastebin_core.app.postgresql.crud import delete_expired_records_from_db, \
    delete_record_and_file, update_post_views_in_db
from microservices.pastebin_core.app.redis.redis import get_all_views_from_cache, clear_views_from_cache, \
    get_all_keys_sorted_set, delete_key_sorted_set, update_score_sorted_set

scheduler = AsyncIOScheduler()

def start_scheduler(session: AsyncSession, redis: Redis):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=settings.CLEANUP_EXP_POSTS_INTERVAL, args=[session])
    scheduler.add_job(sync_views, 'interval', seconds=settings.SYNC_VIEWS_INTERVAL, args=[session, redis])
    scheduler.add_job(decrement_scores, 'interval', seconds=settings.DECREMENT_RECENT_VIEWS_INTERVAL, args=[redis])
    scheduler.start()
    # print("Планировщик запущен")

def terminate_scheduler():
    scheduler.shutdown()


async def delete_expired_records(session: AsyncSession):
    """Функция для удаления просроченных записей."""
    try:
        expired_records = await delete_expired_records_from_db(session)
        for record in expired_records:
            await delete_record_and_file(session, record)
        print("Устаревшие записи удалены")
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")

async def sync_views(session: AsyncSession, redis):
    """Синхронизирует просмотры из Redis в базу данных."""
    views = await get_all_views_from_cache(redis)  # Получаем просмотры
    for post_id, count in views.items():
        await update_post_views_in_db(session, post_id, count)  # Обновляем в БД
    await clear_views_from_cache(redis, views.keys())  # Очищаем кеш

async def decrement_scores(redis: Redis):
    """Уменьшает баллы всех элементов в sorted_set на 1 и удаляет элементы с нулевым баллом."""
    keys = await get_all_keys_sorted_set(redis, settings.SORTED_SET_RECENT_VIEWS)
    for key, score in keys:
        new_score = score - 1
        if new_score <= 0:
            await delete_key_sorted_set(redis, settings.SORTED_SET_RECENT_VIEWS, key)
        else:
            await update_score_sorted_set(redis, settings.SORTED_SET_RECENT_VIEWS, key, new_score)