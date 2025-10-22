from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Database settings
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_user: str = Field(default="mihailmamaev", description="Database user")
    db_password: str = Field(default="", description="Database password")
    db_name: str = Field(default="sensor", description="Database name")
    
    # Application settings
    debug: bool = Field(default=False, description="Debug mode")
    api_prefix: str = Field(default="/api", description="API prefix")
    
    # Additional settings can be added here
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Any:
    """Возвращает объект настроек приложения."""
    return Settings()
