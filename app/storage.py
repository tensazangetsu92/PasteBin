from typing import BinaryIO

import boto3
from .config import settings

# Инициализация клиента для Yandex Object Storage
s3_client = boto3.client(
    service_name="s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=settings.ACCESS_KEY,
    aws_secret_access_key=settings.SECRET_KEY,
)

async def upload_file_to_bucket(bucket_name: str, object_name: str, file_obj: BinaryIO):
    """Загрузка файла в Yandex Object Storage."""
    try:
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
        return f"https://storage.yandexcloud.net/{bucket_name}/{object_name}"
    except Exception as e:
        raise Exception(f"Ошибка загрузки файла в бакет: {e}")


async def delete_file_from_bucket(bucket_name: str, object_name: str):
    """Удаляет файл из бакета по URL ."""
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"Файл {object_name} успешно удален из бакета {bucket_name}.")
    except Exception as e:
        print(f"Ошибка при удалении файла {object_name} из бакета {bucket_name}: {e}")