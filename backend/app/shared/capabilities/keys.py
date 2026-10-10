"""Stable identifiers and typed keys for public application capabilities."""

import re
from dataclasses import dataclass
from typing import cast

_CAPABILITY_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


@dataclass(frozen=True, slots=True, order=True)
class CapabilityIdentifier:
    """Immutable dotted name identifying a public capability contract."""

    value: str

    def __post_init__(self) -> None:
        if not _CAPABILITY_NAME_PATTERN.fullmatch(self.value):
            raise ValueError("Capability identifier must be a lowercase dotted name")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CapabilityKey[T]:
    """A capability name parameterized by its expected public contract type."""

    identifier: CapabilityIdentifier

    def bind(self, provider: T) -> "CapabilityBinding":
        """Create an explicit provider binding while preserving caller-side typing."""
        return CapabilityBinding(key=self, provider=provider)

    def __str__(self) -> str:
        return str(self.identifier)


@dataclass(frozen=True, slots=True)
class CapabilityBinding:
    """An immutable association between a typed key and its implementation."""

    key: CapabilityKey[object]
    provider: object

    def __init__[T](self, key: CapabilityKey[T], provider: T) -> None:
        object.__setattr__(self, "key", cast(CapabilityKey[object], key))
        object.__setattr__(self, "provider", provider)
