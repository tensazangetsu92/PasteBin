import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    HASH_POOL_SIZE: int  # Количество хэшей для генерации
    MIN_HASH_COUNT: int # Минимальное количество хэшей в пуле
    HASH_CHECK_INTERVAL: int  # Интервал проверки в секундах

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))

settings = Settings()