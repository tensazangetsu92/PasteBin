from database import new_session
from models import TextUrlOrm

class TaskRepository:
    @classmethod
    async def add_one(cls, textUrl: TextUrlOrm):
        async with new_session() as session:
            pass