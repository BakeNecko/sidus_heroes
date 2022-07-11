from typing import Optional

from pydantic import BaseModel, BaseSettings


class AppConfig(BaseModel):
    TITLE: str = "SIDUS HEROES ТЗ"
    VERSION: str = "0.0.1"


class GlobalSettings(BaseSettings):
    APP_CONFIG: AppConfig = AppConfig()

    DB_URL: str

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None

    SECRET_KEY: str

    @property
    def ASYNC_DB_URL(self) -> str:
        return self.DB_URL.replace('postgresql://', 'postgresql+asyncpg://')
