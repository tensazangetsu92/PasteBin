# from apscheduler.schedulers.asyncio import AsyncIOScheduler
#
# from microservices.hash_server.app.main import check_and_generate_hashes
#
# scheduler = AsyncIOScheduler()
#
# def start_scheduler():
#     """Настраивает и запускает планировщик."""
#     scheduler.add_job(check_and_generate_hashes, 'interval', seconds=1)
#     scheduler.start()
#     # print("Планировщик запущен")
