"""Frozen, provider-neutral configuration sections for the platform."""

from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

from app.shared.feature_flags import FeatureFlag


class ConfigurationSection(BaseModel):
    """Common immutable base for nested settings sections."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class AppSettings(ConfigurationSection):
    """Core application behavior shared with the P1 flat interface."""

    name: str
    environment: str
    debug: bool
    api_v1_prefix: str
    log_level: str


class DatabaseSettings(ConfigurationSection):
    """PostgreSQL persistence settings with safe disabled defaults."""

    enabled: bool = False
    url: SecretStr | None = None
    connect_timeout_seconds: int = Field(default=3, ge=1, le=30)
    pool_timeout_seconds: int = Field(default=5, ge=1, le=60)

    @model_validator(mode="after")
    def validate_database_configuration(self) -> "DatabaseSettings":
        """Require an explicit PostgreSQL Psycopg URL whenever configured."""
        if self.enabled and self.url is None:
            raise ValueError("database URL is required when database is enabled")
        if self.url is not None:
            scheme = urlsplit(self.url.get_secret_value()).scheme.lower()
            if scheme != "postgresql+psycopg":
                raise ValueError("database URL must use the postgresql+psycopg driver")
        return self


class SecuritySettings(ConfigurationSection):
    """Unconfigured security-secret boundary for later identity work."""

    secret_key: SecretStr | None = None


class RateLimitSettings(ConfigurationSection):
    """Validated application-layer abuse-control budgets."""

    window_seconds: int = Field(default=60, ge=1, le=3_600)
    process_requests: int = Field(default=6_000, ge=1, le=1_000_000)
    peer_requests: int = Field(default=600, ge=1, le=1_000_000)
    credential_requests: int = Field(default=120, ge=1, le=1_000_000)
    mutation_peer_requests: int = Field(default=300, ge=1, le=1_000_000)
    mutation_credential_requests: int = Field(default=60, ge=1, le=1_000_000)
    session_creation_peer_requests: int = Field(default=120, ge=1, le=1_000_000)
    max_tracked_keys: int = Field(default=10_000, ge=16, le=1_000_000)

    @model_validator(mode="after")
    def validate_layer_order(self) -> "RateLimitSettings":
        if not (
            self.session_creation_peer_requests
            <= self.mutation_peer_requests
            <= self.peer_requests
            <= self.process_requests
            and self.mutation_credential_requests
            <= self.credential_requests
            <= self.process_requests
        ):
            raise ValueError("rate-limit budgets must become stricter at narrower layers")
        return self


class SessionsSettings(ConfigurationSection):
    """Foundation TTLs; production values require later security/privacy review."""

    pseudonymous_ttl_minutes: int = Field(default=60, ge=1, le=10_080)
    kiosk_ttl_minutes: int = Field(default=30, ge=1, le=10_080)


class ObjectStorageSettings(ConfigurationSection):
    """Inactive provider-neutral object-storage boundary."""

    enabled: bool = False
    endpoint: str | None = None
    access_key: SecretStr | None = None
    secret_key: SecretStr | None = None


class LlmSettings(ConfigurationSection):
    """Inactive provider-neutral language-model boundary."""

    enabled: bool = False
    endpoint: str | None = None
    api_key: SecretStr | None = None


class OcrSettings(ConfigurationSection):
    """Inactive provider-neutral OCR boundary."""

    enabled: bool = False
    endpoint: str | None = None


class SpeechSettings(ConfigurationSection):
    """Inactive provider-neutral speech boundary."""

    enabled: bool = False
    endpoint: str | None = None


class FhirSettings(ConfigurationSection):
    """Inactive FHIR interoperability boundary."""

    enabled: bool = False
    endpoint: str | None = None


class AbdmSettings(ConfigurationSection):
    """Inactive ABDM integration boundary."""

    enabled: bool = False
    endpoint: str | None = None


class ObservabilitySettings(ConfigurationSection):
    """In-process observability settings with no P2-C exporter support."""

    tracing_enabled: bool = True
    metrics_enabled: bool = True
    external_export_enabled: bool = False
    service_name: str = "swasthyasetu-backend"

    @field_validator("external_export_enabled")
    @classmethod
    def reject_unsupported_external_export(cls, value: bool) -> bool:
        """Fail fast instead of pretending an unavailable exporter is active."""
        if value:
            raise ValueError("external telemetry export is not supported in P2-C")
        return value

    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, value: str) -> str:
        """Require a stable, non-empty service identity."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("observability service name must not be empty")
        return normalized


class FeaturesSettings(ConfigurationSection):
    """Immutable names of explicitly enabled optional features."""

    enabled: tuple[str, ...] = ()

    @field_validator("enabled")
    @classmethod
    def validate_enabled_flags(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Validate names and reject duplicates for unambiguous configuration."""
        validated = tuple(str(FeatureFlag(name)) for name in value)
        if len(validated) != len(set(validated)):
            raise ValueError("enabled feature flags must not contain duplicates")
        return validated
