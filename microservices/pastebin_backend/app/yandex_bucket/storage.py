from io import BytesIO
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError
from ..config import settings
from ..retry_config import s3_retry
from ..utils import parse_blob_url

# Инициализация клиента для Yandex Object Storage
s3_client = boto3.client(
    service_name="s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=settings.BUCKET_ACCESS_KEY,
    aws_secret_access_key=settings.BUCKET_SECRET_KEY,
)

@s3_retry
async def upload_file_to_bucket(bucket_name: str, author_id: int, short_key: str, text: str):
    """Загрузка файла в Yandex Object Storage."""
    try:
        file_obj = BytesIO(text.encode("utf-8"))
        object_url_in_bucket = f"{author_id}/{short_key}.txt"
        s3_client.upload_fileobj(file_obj, bucket_name, object_url_in_bucket)
        return f"https://storage.yandexcloud.net/{bucket_name}/{object_url_in_bucket}"
    except Exception as e:
        raise Exception(f"Ошибка загрузки файла в бакет: {e}")

@s3_retry
async def get_file_from_bucket(blob_url: str) -> dict:
    """Получение содержимого файла и его размера из бакета за один запрос."""
    try:
        bucket_name, object_name = parse_blob_url(blob_url)
        response = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        text_content = response["Body"].read().decode("utf-8")
        file_size = response["ContentLength"]
        return {
            "content": text_content,
            "size": file_size,
        }
    except ClientError as e:
        raise Exception(f"Error retrieving file and metadata from bucket: {e}")

@s3_retry
async def delete_file_from_bucket(bucket_name: str, author_id: int, object_short_key: str):
    """Удаление файла из бакета по URL ."""
    object_url_in_bucket = f"{author_id}/{object_short_key}.txt"
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_url_in_bucket)
        print(f"Файл {object_url_in_bucket} успешно удален из бакета {bucket_name}.")
    except Exception as e:
        print(f"Ошибка при удалении файла {object_url_in_bucket} из бакета {bucket_name}: {e}")