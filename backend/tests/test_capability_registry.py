"""Typed capability identifier, binding, and registry tests."""

from dataclasses import FrozenInstanceError
from typing import Protocol

import pytest

from app.shared.capabilities import (
    CapabilityIdentifier,
    CapabilityKey,
    CapabilityNotFoundError,
    CapabilityRegistry,
    DuplicateCapabilityError,
    RegistryNotSealedError,
    RegistrySealedError,
)


class GreetingCapability(Protocol):
    def greet(self) -> str: ...


class SyntheticGreeter:
    def greet(self) -> str:
        return "hello"


GREETING_KEY = CapabilityKey[GreetingCapability](CapabilityIdentifier("example.greet"))


def test_capability_identifier_is_stable_hashable_and_validated() -> None:
    identifier = CapabilityIdentifier("catalog.read")

    assert str(identifier) == "catalog.read"
    assert {identifier: "registered"}[CapabilityIdentifier("catalog.read")] == "registered"
    with pytest.raises(ValueError):
        CapabilityIdentifier("")
    with pytest.raises(ValueError):
        CapabilityIdentifier("not_dotted")


def test_capability_key_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        GREETING_KEY.identifier = CapabilityIdentifier("example.other")  # type: ignore[misc]


def test_typed_provider_registration_and_resolution() -> None:
    registry = CapabilityRegistry()
    registry.register_bindings(
        module_id="example",
        bindings=(GREETING_KEY.bind(SyntheticGreeter()),),
    )
    registry.seal()

    capability = registry.resolve(GREETING_KEY)

    assert capability.greet() == "hello"
    assert registry.registered_names == ("example.greet",)


def test_resolution_requires_sealed_registry() -> None:
    registry = CapabilityRegistry()

    with pytest.raises(RegistryNotSealedError):
        registry.resolve(GREETING_KEY)


def test_missing_capability_resolution_is_deterministic() -> None:
    registry = CapabilityRegistry()
    registry.seal()

    with pytest.raises(CapabilityNotFoundError, match="example.greet"):
        registry.resolve(GREETING_KEY)


def test_duplicate_provider_is_rejected_without_replacement() -> None:
    registry = CapabilityRegistry()
    first = SyntheticGreeter()
    registry.register_bindings(module_id="alpha", bindings=(GREETING_KEY.bind(first),))

    with pytest.raises(DuplicateCapabilityError, match="alpha"):
        registry.register_bindings(
            module_id="beta",
            bindings=(GREETING_KEY.bind(SyntheticGreeter()),),
        )

    registry.seal()
    assert registry.resolve(GREETING_KEY) is first


def test_capability_registration_after_seal_is_rejected() -> None:
    registry = CapabilityRegistry()
    registry.seal()

    with pytest.raises(RegistrySealedError):
        registry.register_bindings(
            module_id="example",
            bindings=(GREETING_KEY.bind(SyntheticGreeter()),),
        )
