import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Переменные для базы данных Redis
    DB_REDIS_HOST: str
    DB_REDIS_PORT: int
    DB_REDIS_INDEX: int
    DB_REDIS_USERNAME: str
    DB_REDIS_PASSWORD: str


    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '..', '.env'))

settings = Settings()
