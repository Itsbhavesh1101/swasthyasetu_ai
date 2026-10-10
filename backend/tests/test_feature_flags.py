"""Provider-neutral feature-flag behavior tests."""

from dataclasses import FrozenInstanceError

import pytest

from app.config import FeaturesSettings, Settings
from app.main import create_app
from app.shared.feature_flags import (
    ConfigurationFeatureFlagProvider,
    FeatureFlag,
    FeatureFlagService,
)

SYNTHETIC_FLAG = FeatureFlag("synthetic_optional_feature")


@pytest.mark.parametrize(
    "invalid_name",
    ["", "ExampleFeature", "example-feature", "example.feature", "_example", "example_"],
)
def test_feature_flag_rejects_invalid_identifiers(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        FeatureFlag(invalid_name)


def test_absent_and_unknown_valid_flags_default_off() -> None:
    service = FeatureFlagService(ConfigurationFeatureFlagProvider.from_names(()))

    assert service.is_enabled(SYNTHETIC_FLAG) is False
    assert service.is_enabled(FeatureFlag("another_synthetic_feature")) is False


def test_explicitly_configured_flag_is_enabled() -> None:
    service = FeatureFlagService(
        ConfigurationFeatureFlagProvider.from_names((str(SYNTHETIC_FLAG),))
    )

    assert service.is_enabled(SYNTHETIC_FLAG) is True
    assert service.is_enabled(FeatureFlag("unconfigured_feature")) is False


def test_default_settings_enable_no_product_flags() -> None:
    settings = Settings(_env_file=None)

    assert settings.features.enabled == ()
    assert create_app(settings).state.feature_flags.is_enabled(SYNTHETIC_FLAG) is False


def test_feature_settings_reject_duplicate_or_invalid_names() -> None:
    with pytest.raises(ValueError):
        FeaturesSettings(enabled=("example_feature", "example_feature"))
    with pytest.raises(ValueError):
        FeaturesSettings(enabled=("invalid-feature",))


def test_feature_configuration_and_provider_are_immutable() -> None:
    settings = FeaturesSettings(enabled=("example_feature",))
    provider = ConfigurationFeatureFlagProvider.from_names(settings.enabled)

    with pytest.raises(ValueError):
        settings.enabled = ()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        provider.enabled = frozenset()  # type: ignore[misc]


def test_feature_settings_load_from_nested_environment_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SWASTHYASETU_FEATURES", '{"enabled":["example_feature"]}')

    settings = Settings(_env_file=None)

    assert settings.features.enabled == ("example_feature",)
    assert create_app(settings).state.feature_flags.is_enabled(FeatureFlag("example_feature"))
