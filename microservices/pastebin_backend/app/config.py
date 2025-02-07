import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Переменные для базы данных PostgreSql
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Переменные для Yandex Object Storage
    BUCKET_ACCESS_KEY: str
    BUCKET_SECRET_KEY: str
    BUCKET_NAME: str

    # Переменные для базы данных Redis
    DB_REDIS_HOST: str
    DB_REDIS_PORT: int
    DB_REDIS_INDEX: int
    DB_REDIS_USERNAME: str
    DB_REDIS_PASSWORD: str
    CACHE_VIEWS_THRESHOLD: int # Минимальное количество просмотров для добавления в кэш
    TTL_POSTS: int
    TTL_VIEWS: int
    SORTED_SET_VIEWS: str

    HASH_SERVER_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLEANUP_EXP_POSTS_INTERVAL: int
    SYNC_VIEWS_INTERVAL: int
    DECREMENT_RECENT_VIEWS_INTERVAL: int

    @property
    def database_url_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '..', '.env'))


settings = Settings()