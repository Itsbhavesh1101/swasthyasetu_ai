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
    assert settings.observability.external_export_enabled is False


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
    settings = Settings(
        database=DatabaseSettings(url=SecretStr(secret)),
        llm=LlmSettings(api_key=SecretStr(secret)),
        _env_file=None,
    )

    assert secret not in repr(settings)
    assert secret not in repr(settings.database)
    assert secret not in repr(settings.llm)
