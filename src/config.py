"""
Конфигурация бэкенда. Все ENV-переменные собираются в один объект Config.
Доступ — через get_config() (lru_cache, чтобы парсить .env один раз).

Паттерн взят из appss-back/src/config.py.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


class GeneralParams(EnvSettings):
    environment: str = Field("development", alias="ENVIRONMENT")
    debug: bool = Field(False, alias="DEBUG")
    cors_allow_origins: str = Field("*", alias="CORS_ALLOW_ORIGINS")


class DBParams(EnvSettings):
    url: str = Field(..., alias="DATABASE_URL")


class TgParams(EnvSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    bot_push_url: str = Field("http://localhost:8080", alias="BOT_PUSH_URL")
    push_internal_token: str = Field("change-me", alias="PUSH_INTERNAL_TOKEN")
    init_data_ttl_hours: int = Field(24, alias="INIT_DATA_TTL_HOURS")


class Config(EnvSettings):
    general: GeneralParams = GeneralParams()
    db: DBParams = DBParams()
    tg: TgParams = TgParams()


@lru_cache
def get_config() -> Config:
    return Config()
