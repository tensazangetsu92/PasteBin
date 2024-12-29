from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import delete
from .models import TextUrlOrm

async def delete_expired_records(session: AsyncSession):
    """Удаляет записи с истёкшим сроком действия."""
    try:
        now = datetime.utcnow()
        async with session.begin():
            await session.execute(
                delete(TextUrlOrm).where(TextUrlOrm.expires_at < now)
            )
        print("Устаревшие записи удалены")
    except Exception as e:
        print(f"Ошибка при удалении устаревших записей: {e}")

scheduler = AsyncIOScheduler()

def start_scheduler(session: AsyncSession):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=5, args=[session])
    scheduler.start()
    print("Планировщик запущен")
