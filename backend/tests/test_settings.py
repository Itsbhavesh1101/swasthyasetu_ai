"""Typed settings behavior tests."""

import pytest
from pydantic import ValidationError

from app.config import Environment, LogLevel, Settings


def test_settings_have_production_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "SwasthyaSetu AI"
    assert settings.environment is Environment.LOCAL
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.log_level is LogLevel.INFO


def test_settings_accept_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_ENVIRONMENT", "staging")
    monkeypatch.setenv("SWASTHYASETU_LOG_LEVEL", "WARNING")

    settings = Settings(_env_file=None)

    assert settings.environment is Environment.STAGING
    assert settings.log_level is LogLevel.WARNING


def test_settings_reject_invalid_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWASTHYASETU_DEBUG", "not-a-boolean")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("prefix", ["api/v1", "/", "/api/v1/"])
def test_settings_reject_invalid_api_prefix(prefix: str) -> None:
    with pytest.raises(ValidationError):
        Settings(api_v1_prefix=prefix, _env_file=None)
