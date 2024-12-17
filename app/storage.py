import boto3
from .config import settings

# Инициализация клиента для Yandex Object Storage с использованием переменных окружения
s3_client = boto3.client(
    service_name="s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=settings.ACCESS_KEY,
    aws_secret_access_key=settings.SECRET_KEY,
)

s3_client.upload_file("local_file.txt", "texts", "remote_file.txt")
print("Файл успешно загружен!")

