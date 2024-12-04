from fastapi import FastAPI

from .router import router
from .schemas import TextAdd

app = FastAPI()

app.include_router(router)

texts = []

# @app.post("")
# async def add_text(
#         # text: Annotated[TextAdd, Depends()]
#         text: TextAdd
# ):
#     texts.append(text.content)
#     return {"content": text.content}