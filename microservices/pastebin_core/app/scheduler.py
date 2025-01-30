from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_core.app.postgresql.crud import delete_expired_records_from_db, \
    delete_record_and_file

scheduler = AsyncIOScheduler()

def start_scheduler(session: AsyncSession):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=60*60, args=[session])
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