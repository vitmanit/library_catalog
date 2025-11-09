from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation"""

    # Database
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # External APIs
    jsonbin_api_key: str
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: int = 20

    # Redis
    redis_url: Optional[str] = None

    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Security
    secret_key: str
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    cors_origins: list[str] = ["http://localhost:3000"]

    # API
    api_v1_prefix: str = "/api/v1"
    api_title: str = "Library Catalog API"
    api_version: str = "1.0.0"
    api_description: str = "API for managing library book catalog"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Игнорировать неизвестные поля
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """Singleton для settings"""
    return Settings()