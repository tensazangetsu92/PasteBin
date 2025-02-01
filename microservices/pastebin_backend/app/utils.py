from datetime import datetime


def parse_blob_url(blob_url: str) -> tuple[str, str]:
    """Разбор URL, чтобы получить имя бакета и объект."""
    url_parts = blob_url.replace("https://storage.yandexcloud.net/", "").split("/", 1)
    return url_parts[0], url_parts[1]

def convert_to_kilobytes(bytes: int):
    return round(bytes / 1024, 2)

def get_post_age(created_at: datetime):
    """Получить сколько секунд/минут/часов/дней назад был создан пост"""
    time_difference = datetime.utcnow() - created_at
    if time_difference.days > 0:
        creation_time = f"{time_difference.days} дней назад"
    elif time_difference.seconds >= 3600:
        creation_time = f"{time_difference.seconds // 3600} часов назад"
    elif time_difference.seconds >= 60:
        creation_time = f"{time_difference.seconds // 60} минут назад"
    else:
        creation_time = f"{time_difference.seconds} секунд назад"
    return creation_time