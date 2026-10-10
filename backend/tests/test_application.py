"""Application construction and module-composition tests."""

import pytest
from fastapi import APIRouter

from app.config import Settings
from app.main import APP_VERSION, create_app
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import (
    DuplicateModuleError,
    MissingRequiredCapabilityError,
    ModuleId,
    ModuleManifest,
    ModuleRegistration,
)


def test_create_app_uses_explicit_settings(test_settings: Settings) -> None:
    application = create_app(test_settings)

    assert application.title == "SwasthyaSetu AI"
    assert application.version == APP_VERSION
    assert application.debug is False


def test_default_application_factory_succeeds() -> None:
    application = create_app()

    assert application.title == "SwasthyaSetu AI"
    assert application.state.module_registry.is_sealed is True
    assert application.state.capability_registry.is_sealed is True


def test_synthetic_module_is_composed_and_capability_is_resolvable() -> None:
    router = APIRouter()
    identifier = CapabilityIdentifier("example.value")
    key = CapabilityKey[str](identifier)
    registration = ModuleRegistration(
        manifest=ModuleManifest(
            module_id=ModuleId("example"),
            version=1,
            provided_capabilities=frozenset({identifier}),
        ),
        routers=(router,),
        capability_bindings=(key.bind("synthetic-provider"),),
    )

    application = create_app(Settings(_env_file=None), module_registrations=(registration,))

    assert application.state.module_registry.module_ids == ("example",)
    assert (
        application.state.module_registry.get_manifest(ModuleId("example")) is registration.manifest
    )
    assert application.state.capability_registry.resolve(key) == "synthetic-provider"


def test_missing_required_capability_fails_application_construction() -> None:
    missing = CapabilityIdentifier("missing.read")
    registration = ModuleRegistration[APIRouter](
        manifest=ModuleManifest(
            module_id=ModuleId("example"),
            version=1,
            required_capabilities=frozenset({missing}),
        )
    )

    with pytest.raises(MissingRequiredCapabilityError):
        create_app(Settings(_env_file=None), module_registrations=(registration,))


def test_duplicate_module_fails_application_construction() -> None:
    registration = ModuleRegistration[APIRouter](
        manifest=ModuleManifest(module_id=ModuleId("example"), version=1)
    )

    with pytest.raises(DuplicateModuleError):
        create_app(
            Settings(_env_file=None),
            module_registrations=(registration, registration),
        )
