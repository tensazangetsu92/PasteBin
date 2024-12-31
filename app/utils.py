

def parse_blob_url(blob_url: str) -> tuple[str, str]:
    """Разбор URL, чтобы получить имя бакета и объект."""
    url_parts = blob_url.replace("https://storage.yandexcloud.net/", "").split("/", 1)
    return url_parts[0], url_parts[1]