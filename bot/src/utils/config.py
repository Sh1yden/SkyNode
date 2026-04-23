from pathlib import Path
from typing import Literal

import os
from dotenv import load_dotenv

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsSchema(BaseSettings):
    """Схема настроек приложения с автоопределением окружения"""

    # PROJECT SETTINGS
    PROJECT_STATUS: Literal["development", "product"] = Field(
        default="development", description="Статус проекта: development или product"
    )

    # TELEGRAM
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API токен")
    TELEGRAM_WEBHOOK_SECRET: str = Field(..., description="Секретный ключ для webhook")

    # TUNA TUNNELS
    TUNA_TOKEN: str = Field(default="", description="Tuna tunnel токен")
    TUNA_API_TOKEN: str = Field(default="", description="Tuna API токен")

    # RUNTIME
    WEB_SERVER_HOST: str = Field(
        default="0.0.0.0", description="Webhook server bind host"
    )
    WEB_SERVER_PORT: str = Field(default="8080", description="Webhook server port")
    BASE_WEBHOOK_URL: str = Field(
        default="",
        description="Public base URL for Telegram webhook. If empty, Tuna is used.",
    )

    # SQLITE (Development only)
    SQLITE_DB_URL: str = Field(
        default="sqlite+aiosqlite:///common/database/database files/sqlite/dev.db",
        description="SQLite database URL для development",
    )

    # POSTGRESQL (Production)
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_ASYNCPG: str = Field(
        default="asyncpg", description="PostgreSQL async драйвер"
    )
    POSTGRES_DB: str = Field(default="postgres", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="postgres", description="PostgreSQL user")
    POSTGRES_PASSWORD: str = Field(
        default="postgres", description="PostgreSQL password"
    )
    POSTGRES_PORT: str = Field(default="5432", description="PostgreSQL port")

    # REDIS
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: str = Field(default="6379", description="Redis port")

    # SERVICES
    VISUAL_CROSSING_KEY: str = Field(..., description="Visual Crossing API key")
    WEATHER_API_KEY: str = Field(..., description="Weather API key")
    OPEN_WEATHER_MAP_API_KEY: str = Field(..., description="OpenWeatherMap API key")
    GOOGLE_KEY: str = Field(..., description="OpenWeatherMap API key")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )

    @property
    def is_production(self) -> bool:
        """Проверка на production окружение"""
        return self.PROJECT_STATUS == "product"

    @property
    def is_development(self) -> bool:
        """Проверка на development окружение"""
        return self.PROJECT_STATUS == "development"

    @property
    def db_url(self) -> str:
        """Получить URL базы данных в зависимости от окружения"""
        if self.is_production:
            return (
                f"postgresql+{self.POSTGRES_ASYNCPG}://"
                f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
        return self.SQLITE_DB_URL


def get_settings() -> SettingsSchema:
    """
    Фабрика настроек с автоопределением окружения

    Логика работы:
    1. Проверяет переменную окружения PROJECT_STATUS
    2. Загружает соответствующий .env файл
    3. Если PROJECT_STATUS не задан, использует .env.dev

    Returns:
        Настроенный экземпляр SettingsSchema

    Raises:
        FileNotFoundError: Если требуемый .env файл не найден
    """
    # Читаем PROJECT_STATUS из окружения .env
    load_dotenv()
    project_status = os.getenv("PROJECT_STATUS", "development")

    env_file = ".env.prod" if project_status == "product" else ".env.dev"
    env_path = Path(env_file)

    # Временно меняем env_file в model_config
    original_config = SettingsSchema.model_config.copy()
    SettingsSchema.model_config["env_file"] = (
        str(env_path) if env_path.exists() else None
    )

    try:
        settings_instance = SettingsSchema()  # type: ignore
        return settings_instance
    finally:
        # Восстанавливаем оригинальную конфигурацию
        SettingsSchema.model_config = original_config


# Глобальный экземпляр настроек
settings = get_settings()
