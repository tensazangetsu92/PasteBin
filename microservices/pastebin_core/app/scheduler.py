from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from microservices.pastebin_core.app.postgresql.crud import delete_expired_records

scheduler = AsyncIOScheduler()

def start_scheduler(session: AsyncSession):
    """Настраивает и запускает планировщик."""
    scheduler.add_job(delete_expired_records, 'interval', seconds=60*60, args=[session])
    scheduler.start()
    # print("Планировщик запущен")

def terminate_scheduler():
    scheduler.shutdown()
