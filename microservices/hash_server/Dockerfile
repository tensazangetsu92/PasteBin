FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

EXPOSE 8001

CMD ["fastapi", "run", "app/main.py", "--port", "8001", "--reload"]