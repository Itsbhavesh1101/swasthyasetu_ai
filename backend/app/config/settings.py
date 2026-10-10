"""Environment-backed settings and typed platform configuration sections."""

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.sections import (
    AbdmSettings,
    AppSettings,
    DatabaseSettings,
    FeaturesSettings,
    FhirSettings,
    LlmSettings,
    ObjectStorageSettings,
    ObservabilitySettings,
    OcrSettings,
    SecuritySettings,
    SpeechSettings,
)


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
    """Frozen platform settings with the P1 flat access contract preserved."""

    model_config = SettingsConfigDict(
        env_prefix="SWASTHYASETU_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    app_name: str = "SwasthyaSetu AI"
    environment: Environment = Environment.LOCAL
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: LogLevel = LogLevel.INFO

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    object_storage: ObjectStorageSettings = Field(default_factory=ObjectStorageSettings)
    llm: LlmSettings = Field(default_factory=LlmSettings)
    ocr: OcrSettings = Field(default_factory=OcrSettings)
    speech: SpeechSettings = Field(default_factory=SpeechSettings)
    fhir: FhirSettings = Field(default_factory=FhirSettings)
    abdm: AbdmSettings = Field(default_factory=AbdmSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    features: FeaturesSettings = Field(default_factory=FeaturesSettings)

    @property
    def app(self) -> AppSettings:
        """Expose the application namespace without breaking P1 flat access."""
        return AppSettings(
            name=self.app_name,
            environment=self.environment.value,
            debug=self.debug,
            api_v1_prefix=self.api_v1_prefix,
            log_level=self.log_level.value,
        )

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_v1_prefix(cls, value: str) -> str:
        """Keep the configurable prefix absolute and free of a trailing slash."""
        if not value.startswith("/"):
            raise ValueError("API v1 prefix must start with '/'")
        if value == "/" or value.endswith("/"):
            raise ValueError("API v1 prefix must not be '/' or end with '/'")
        return value
