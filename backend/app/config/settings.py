"""Environment-backed settings for the backend foundation."""

from enum import StrEnum

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported runtime environment labels."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PILOT = "pilot"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Logging levels accepted by the application configuration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Small, production-safe settings surface for P1-A."""

    model_config = SettingsConfigDict(
        env_prefix="SWASTHYASETU_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    app_name: str = "SwasthyaSetu AI"
    environment: Environment = Environment.LOCAL
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: LogLevel = LogLevel.INFO

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_v1_prefix(cls, value: str) -> str:
        """Keep the configurable prefix absolute and free of a trailing slash."""
        if not value.startswith("/"):
            raise ValueError("API v1 prefix must start with '/'")
        if value == "/" or value.endswith("/"):
            raise ValueError("API v1 prefix must not be '/' or end with '/'")
        return value
