"""Application construction tests."""

from app.config import Settings
from app.main import APP_VERSION, create_app


def test_create_app_uses_explicit_settings(test_settings: Settings) -> None:
    application = create_app(test_settings)

    assert application.title == "SwasthyaSetu AI"
    assert application.version == APP_VERSION
    assert application.debug is False


def test_default_application_factory_succeeds() -> None:
    application = create_app()

    assert application.title == "SwasthyaSetu AI"
