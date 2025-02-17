import socket

from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
import sqlalchemy.exc
import redis.exceptions

db_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(min=2, max=10),
    retry=retry_if_exception_type((
        sqlalchemy.exc.OperationalError,
        sqlalchemy.exc.TimeoutError,
        sqlalchemy.exc.DisconnectionError,
    )),
)

cache_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(min=1, max=5),
    retry=retry_if_exception_type(
        (redis.exceptions.ConnectionError,
         redis.exceptions.TimeoutError,
         redis.exceptions.BusyLoadingError)
    ),
)

s3_retry = retry(
    stop=stop_after_attempt(3),  # Максимум 3 попытки
    wait=wait_random_exponential(min=1, max=10),  # Экспоненциальное ожидание с джиттером
    retry=retry_if_exception_type((
        ClientError,  # Ошибки от boto3
        socket.timeout,  # Тайм-ауты
        socket.gaierror,  # Ошибки подключения
    )),
)