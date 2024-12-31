from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError
from .config import settings
from .utils import parse_blob_url

# Инициализация клиента для Yandex Object Storage
s3_client = boto3.client(
    service_name="s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=settings.ACCESS_KEY,
    aws_secret_access_key=settings.SECRET_KEY,
)

async def upload_file_to_bucket(bucket_name: str, author_id: int, short_key: str, file_obj: BinaryIO):
    """Загрузка файла в Yandex Object Storage."""
    try:
        object_url_in_bucket = f"{author_id}/{short_key}.txt"
        s3_client.upload_fileobj(file_obj, bucket_name, object_url_in_bucket)
        return f"https://storage.yandexcloud.net/{bucket_name}/{object_url_in_bucket}"
    except Exception as e:
        raise Exception(f"Ошибка загрузки файла в бакет: {e}")


async def get_file_from_bucket(blob_url: str) -> str:
    """Скачивание текста из бакета."""
    try:
        bucket_name, object_name = parse_blob_url(blob_url)
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        text_content = response["Body"].read().decode("utf-8")
        return text_content
    except ClientError as e:
        raise Exception(f"Error downloading file from bucket: {e}")

async def get_file_size_from_bucket(blob_url: str) -> int:
    """Получение размера файла из бакета."""
    try:
        # Получаем метаданные объекта
        bucket_name, object_name = parse_blob_url(blob_url)
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)
        # Размер файла в байтах
        file_size = response['ContentLength']
        return file_size
    except ClientError as e:
        print(f"Ошибка при получении размера файла: {e}")
        return None


async def delete_file_from_bucket(bucket_name: str, author_id: int, object_short_key: str):
    """Удаление файла из бакета по URL ."""
    object_url_in_bucket = f"{author_id}/{object_short_key}.txt"
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_url_in_bucket)
        print(f"Файл {object_url_in_bucket} успешно удален из бакета {bucket_name}.")
    except Exception as e:
        print(f"Ошибка при удалении файла {object_url_in_bucket} из бакета {bucket_name}: {e}")