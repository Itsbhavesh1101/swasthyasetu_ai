"""Typed settings behavior tests."""

import pytest
from pydantic import SecretStr, ValidationError

from app.config import (
    AbdmSettings,
    AppSettings,
    DatabaseSettings,
    FeaturesSettings,
    FhirSettings,
    LlmSettings,
    LogLevel,
    ObjectStorageSettings,
    ObservabilitySettings,
    OcrSettings,
    SecuritySettings,
    Settings,
    SpeechSettings,
)
from app.config.settings import Environment


def test_settings_have_production_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "SwasthyaSetu AI"
    assert settings.environment is Environment.LOCAL
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.log_level is LogLevel.INFO


def test_settings_expose_typed_inactive_sections() -> None:
    settings = Settings(_env_file=None)

    assert isinstance(settings.app, AppSettings)
    assert isinstance(settings.database, DatabaseSettings)
    assert isinstance(settings.security, SecuritySettings)
    assert isinstance(settings.object_storage, ObjectStorageSettings)
    assert isinstance(settings.llm, LlmSettings)
    assert isinstance(settings.ocr, OcrSettings)
    assert isinstance(settings.speech, SpeechSettings)
    assert isinstance(settings.fhir, FhirSettings)
    assert isinstance(settings.abdm, AbdmSettings)
    assert isinstance(settings.observability, ObservabilitySettings)
    assert isinstance(settings.features, FeaturesSettings)
    assert settings.database.enabled is False
    assert settings.object_storage.enabled is False
    assert settings.llm.enabled is False
    assert settings.ocr.enabled is False
    assert settings.speech.enabled is False
    assert settings.fhir.enabled is False
    assert settings.abdm.enabled is False
    assert settings.observability.tracing_enabled is True
    assert settings.observability.metrics_enabled is True
    assert settings.observability.external_export_enabled is False
    assert settings.observability.service_name == "swasthyasetu-backend"
    assert settings.features.enabled == ()


def test_settings_accept_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_APP_NAME", "Test Setu")
    monkeypatch.setenv("SWASTHYASETU_ENVIRONMENT", "staging")
    monkeypatch.setenv("SWASTHYASETU_DEBUG", "true")
    monkeypatch.setenv("SWASTHYASETU_API_V1_PREFIX", "/platform/v1")
    monkeypatch.setenv("SWASTHYASETU_LOG_LEVEL", "WARNING")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Test Setu"
    assert settings.environment is Environment.STAGING
    assert settings.debug is True
    assert settings.api_v1_prefix == "/platform/v1"
    assert settings.log_level is LogLevel.WARNING
    assert settings.app.environment == "staging"
    assert settings.app.log_level == "WARNING"


def test_settings_reject_invalid_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_DEBUG", "not-a-boolean")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("prefix", ["api/v1", "/", "/api/v1/"])
def test_settings_reject_invalid_api_prefix(prefix: str) -> None:
    with pytest.raises(ValidationError):
        Settings(api_v1_prefix=prefix, _env_file=None)


def test_settings_reject_invalid_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_ENVIRONMENT", "unknown")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_unknown_environment_variable_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_UNKNOWN_SETTING", "ignored")

    assert Settings(_env_file=None).app_name == "SwasthyaSetu AI"


def test_settings_and_nested_sections_are_frozen() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(ValidationError):
        settings.debug = True  # type: ignore[misc]
    with pytest.raises(ValidationError):
        settings.database.enabled = True  # type: ignore[misc]


def test_secret_values_are_masked_in_representations() -> None:
    secret = "synthetic-secret-value"
    database_url = f"postgresql+psycopg://user:{secret}@localhost/synthetic"
    settings = Settings(
        database=DatabaseSettings(url=SecretStr(database_url)),
        llm=LlmSettings(api_key=SecretStr(secret)),
        _env_file=None,
    )

    assert secret not in repr(settings)
    assert secret not in repr(settings.database)
    assert secret not in repr(settings.llm)


def test_database_nested_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    url = "postgresql+psycopg://synthetic-user:synthetic-password@localhost/test_db"
    monkeypatch.setenv("SWASTHYASETU_DATABASE__ENABLED", "true")
    monkeypatch.setenv("SWASTHYASETU_DATABASE__URL", url)
    monkeypatch.setenv("SWASTHYASETU_DATABASE__CONNECT_TIMEOUT_SECONDS", "2")

    settings = Settings(_env_file=None)

    assert settings.database.enabled is True
    assert settings.database.url is not None
    assert settings.database.url.get_secret_value() == url
    assert settings.database.connect_timeout_seconds == 2
    assert url not in repr(settings)


def test_nested_environment_support_preserves_json_sections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SWASTHYASETU_FEATURES", '{"enabled":["example_feature"]}')
    monkeypatch.setenv(
        "SWASTHYASETU_OBSERVABILITY",
        '{"tracing_enabled":false,"metrics_enabled":true}',
    )

    settings = Settings(_env_file=None)

    assert settings.features.enabled == ("example_feature",)
    assert settings.observability.tracing_enabled is False
    assert settings.observability.metrics_enabled is True


def test_database_enabled_requires_url() -> None:
    with pytest.raises(ValidationError, match="database URL is required"):
        DatabaseSettings(enabled=True)


@pytest.mark.parametrize(
    "url",
    [
        "sqlite+aiosqlite:///synthetic.db",
        "mysql+asyncmy://localhost/synthetic",
        "postgresql://localhost/synthetic",
    ],
)
def test_database_rejects_non_explicit_psycopg_urls(url: str) -> None:
    with pytest.raises(ValidationError, match=r"postgresql\+psycopg"):
        DatabaseSettings(enabled=True, url=SecretStr(url))


def test_database_validation_error_masks_url_secret() -> None:
    secret = "validation-secret"
    with pytest.raises(ValidationError) as error:
        DatabaseSettings(enabled=True, url=SecretStr(f"postgresql://user:{secret}@localhost/db"))

    assert secret not in str(error.value)
