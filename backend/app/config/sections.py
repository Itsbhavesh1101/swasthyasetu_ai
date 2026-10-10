"""Frozen, provider-neutral configuration sections for the platform."""

from pydantic import BaseModel, ConfigDict, SecretStr


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
    """P1 logging-preserving boundary; exporters remain disabled until P2-C."""

    external_export_enabled: bool = False


class FeaturesSettings(ConfigurationSection):
    """Empty namespace reserved for P2-C feature-flag configuration."""
