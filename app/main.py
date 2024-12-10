from fastapi import FastAPI

from .schemas import TextAdd


app = FastAPI()

app.include_router(router)

texts = []

@app.post("/add-text/")
async def add_text(content: str, session: AsyncSession = Depends(get_session)):
    # Загрузить текст в S3
    short_key = generate_short_key()
    s3_url = upload_to_s3(content, f"{short_key}.txt")

    # Сохранить данные в базу
    new_entry = TextUrlOrm(blob_url=s3_url, short_key=short_key)
    session.add(new_entry)
    await session.commit()

    return {"short_key": short_key, "blob_url": s3_url}