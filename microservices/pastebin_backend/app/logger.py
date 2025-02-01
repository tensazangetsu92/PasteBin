import logging
import os
from pathlib import Path

# Определяем уровень логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Создаем логгер
logger = logging.getLogger("pastebin")
logger.setLevel(LOG_LEVEL)

# Формат сообщений
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

log_file_path = Path(__file__).parent.parent / "app.log"  # Файл будет в той же папке, что и logger.py

# Запись логов в файл
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
