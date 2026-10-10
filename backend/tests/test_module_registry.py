"""Immutable module manifest and explicit registry composition tests."""

from dataclasses import FrozenInstanceError

import pytest

from app.shared.capabilities import (
    CapabilityIdentifier,
    CapabilityKey,
    DuplicateCapabilityError,
    RegistryNotSealedError,
    RegistrySealedError,
)
from app.shared.modules import (
    CapabilityDeclarationError,
    DuplicateModuleError,
    MissingRequiredCapabilityError,
    ModuleId,
    ModuleManifest,
    ModuleRegistration,
    ModuleRegistry,
)

ALPHA_READ = CapabilityIdentifier("alpha.read")
BETA_READ = CapabilityIdentifier("beta.read")
ALPHA_KEY = CapabilityKey[str](ALPHA_READ)
BETA_KEY = CapabilityKey[str](BETA_READ)


def manifest(
    module_id: str,
    *,
    provides: frozenset[CapabilityIdentifier] = frozenset(),
    requires: frozenset[CapabilityIdentifier] = frozenset(),
) -> ModuleManifest:
    return ModuleManifest(
        module_id=ModuleId(module_id),
        version=1,
        provided_capabilities=provides,
        required_capabilities=requires,
    )


def test_manifest_records_all_immutable_metadata() -> None:
    value = ModuleManifest(
        module_id=ModuleId("catalog"),
        version=2,
        provided_capabilities=frozenset({CapabilityIdentifier("catalog.read")}),
        required_capabilities=frozenset({CapabilityIdentifier("alpha.read")}),
        api_prefixes=("/catalog",),
        events_published=("CatalogUpdated",),
        events_consumed=("AlphaUpdated",),
        required_permissions=("catalog:read",),
        configuration_keys=("catalog.endpoint",),
        feature_flags=("catalog_enabled",),
        data_ownership=("catalog_metadata",),
    )

    assert value.version == 2
    assert value.api_prefixes == ("/catalog",)
    assert value.events_published == ("CatalogUpdated",)
    assert value.events_consumed == ("AlphaUpdated",)
    assert value.required_permissions == ("catalog:read",)
    assert value.configuration_keys == ("catalog.endpoint",)
    assert value.feature_flags == ("catalog_enabled",)
    assert value.data_ownership == ("catalog_metadata",)
    with pytest.raises(FrozenInstanceError):
        value.version = 3  # type: ignore[misc]


def test_manifest_defaults_are_empty_and_immutable() -> None:
    value = manifest("alpha")

    assert value.provided_capabilities == frozenset()
    assert value.required_capabilities == frozenset()
    assert value.api_prefixes == ()


@pytest.mark.parametrize("module_id", ["", "Alpha", "alpha.module", "1alpha"])
def test_invalid_module_identifier_is_rejected(module_id: str) -> None:
    with pytest.raises(ValueError):
        ModuleId(module_id)


def test_invalid_manifest_version_and_metadata_are_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        ModuleManifest(module_id=ModuleId("alpha"), version=0)
    with pytest.raises(ValueError, match="API prefixes"):
        ModuleManifest(module_id=ModuleId("alpha"), version=1, api_prefixes=("alpha",))
    with pytest.raises(ValueError, match="must not be empty"):
        ModuleManifest(module_id=ModuleId("alpha"), version=1, feature_flags=("",))


def test_register_multiple_modules_and_retrieve_manifests() -> None:
    registry = ModuleRegistry[object]()
    alpha = manifest("alpha")
    beta = manifest("beta")

    registry.register(ModuleRegistration(manifest=alpha))
    registry.register(ModuleRegistration(manifest=beta))
    registry.finalize()

    assert registry.module_ids == ("alpha", "beta")
    assert registry.get_manifest(ModuleId("alpha")) is alpha
    assert registry.is_sealed is True
    assert registry.capability_registry.is_sealed is True


def test_duplicate_module_and_registration_after_finalize_are_rejected() -> None:
    registry = ModuleRegistry[object]()
    registration = ModuleRegistration[object](manifest=manifest("alpha"))
    registry.register(registration)

    with pytest.raises(DuplicateModuleError):
        registry.register(registration)

    registry.finalize()
    with pytest.raises(RegistrySealedError):
        registry.register(ModuleRegistration(manifest=manifest("beta")))


def test_runtime_composition_is_not_exposed_before_finalize() -> None:
    registry = ModuleRegistry[object]()

    with pytest.raises(RegistryNotSealedError):
        _ = registry.capability_registry
    with pytest.raises(RegistryNotSealedError):
        _ = registry.routers


def test_requirement_can_be_satisfied_by_later_registered_provider() -> None:
    registry = ModuleRegistry[object]()
    registry.register(
        ModuleRegistration(manifest=manifest("alpha", requires=frozenset({BETA_READ})))
    )
    registry.register(
        ModuleRegistration(
            manifest=manifest("beta", provides=frozenset({BETA_READ})),
            capability_bindings=(BETA_KEY.bind("provider"),),
        )
    )

    registry.finalize()

    assert registry.capability_registry.resolve(BETA_KEY) == "provider"


def test_multiple_modules_may_require_same_provider() -> None:
    registry = ModuleRegistry[object]()
    for module_id in ("alpha", "catalog"):
        registry.register(
            ModuleRegistration(manifest=manifest(module_id, requires=frozenset({BETA_READ})))
        )
    registry.register(
        ModuleRegistration(
            manifest=manifest("beta", provides=frozenset({BETA_READ})),
            capability_bindings=(BETA_KEY.bind("provider"),),
        )
    )

    registry.finalize()

    assert registry.is_sealed is True


def test_missing_required_capability_fails_without_sealing() -> None:
    registry = ModuleRegistry[object]()
    registry.register(
        ModuleRegistration(manifest=manifest("alpha", requires=frozenset({BETA_READ})))
    )

    with pytest.raises(MissingRequiredCapabilityError, match="beta.read"):
        registry.finalize()

    assert registry.is_sealed is False


@pytest.mark.parametrize(
    ("provides", "bindings"),
    [
        (frozenset(), (ALPHA_KEY.bind("provider"),)),
        (frozenset({ALPHA_READ}), ()),
    ],
)
def test_provider_bindings_must_match_manifest_declarations(
    provides: frozenset[CapabilityIdentifier],
    bindings: tuple[object, ...],
) -> None:
    registry = ModuleRegistry[object]()

    with pytest.raises(CapabilityDeclarationError):
        registry.register(
            ModuleRegistration(
                manifest=manifest("alpha", provides=provides),
                capability_bindings=bindings,  # type: ignore[arg-type]
            )
        )


def test_capability_provider_cannot_be_replaced_by_another_module() -> None:
    registry = ModuleRegistry[object]()
    for module_id in ("alpha", "beta"):
        registration = ModuleRegistration[object](
            manifest=manifest(module_id, provides=frozenset({ALPHA_READ})),
            capability_bindings=(ALPHA_KEY.bind(module_id),),
        )
        if module_id == "alpha":
            registry.register(registration)
        else:
            with pytest.raises(DuplicateCapabilityError):
                registry.register(registration)
