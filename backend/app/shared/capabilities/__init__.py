"""Typed, explicitly composed application capabilities."""

from app.shared.capabilities.keys import CapabilityBinding, CapabilityIdentifier, CapabilityKey
from app.shared.capabilities.registry import (
    CapabilityNotFoundError,
    CapabilityRegistry,
    CapabilityRegistryError,
    DuplicateCapabilityError,
    RegistryNotSealedError,
    RegistrySealedError,
)

__all__ = [
    "CapabilityBinding",
    "CapabilityIdentifier",
    "CapabilityKey",
    "CapabilityNotFoundError",
    "CapabilityRegistry",
    "CapabilityRegistryError",
    "DuplicateCapabilityError",
    "RegistryNotSealedError",
    "RegistrySealedError",
]
