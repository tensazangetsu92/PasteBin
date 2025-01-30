from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from microservices.pastebin_core.app.config import settings
from microservices.pastebin_core.app.postgresql.crud import delete_expired_records_from_db, \
    delete_record_and_file, update_post_views_in_db
from microservices.pastebin_core.app.redis.redis import get_all_views_from_cache, clear_views_from_cache

scheduler = AsyncIOScheduler()

def start_scheduler(session: AsyncSession, redis: Redis):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=settings.CLEANUP_INTERVAL, args=[session])
    scheduler.add_job(sync_views, 'interval', seconds=10, args=[session, redis])
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