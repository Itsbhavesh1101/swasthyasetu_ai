"""Frozen, provider-neutral configuration sections for the platform."""

from pydantic import BaseModel, ConfigDict, SecretStr, field_validator

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
    """Inactive persistence configuration boundary for P3."""

    enabled: bool = False
    url: SecretStr | None = None


class SecuritySettings(ConfigurationSection):
    """Unconfigured security-secret boundary for later identity work."""

    secret_key: SecretStr | None = None


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
