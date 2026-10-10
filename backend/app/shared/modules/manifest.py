"""Immutable module manifest metadata mandated by the architecture."""

import re
from dataclasses import dataclass, field

from app.shared.capabilities import CapabilityIdentifier

_MODULE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


@dataclass(frozen=True, slots=True, order=True)
class ModuleId:
    """Stable machine-readable module identifier."""

    value: str

    def __post_init__(self) -> None:
        if not _MODULE_ID_PATTERN.fullmatch(self.value):
            raise ValueError(
                "Module identifier must start with a lowercase letter and contain only "
                "lowercase letters, digits, underscores, or hyphens"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ModuleManifest:
    """Versioned declarations for a bounded module's public integration surface."""

    module_id: ModuleId
    version: int
    provided_capabilities: frozenset[CapabilityIdentifier] = field(default_factory=frozenset)
    required_capabilities: frozenset[CapabilityIdentifier] = field(default_factory=frozenset)
    api_prefixes: tuple[str, ...] = ()
    events_published: tuple[str, ...] = ()
    events_consumed: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    configuration_keys: tuple[str, ...] = ()
    feature_flags: tuple[str, ...] = ()
    data_ownership: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("Manifest version must be a positive integer")
        metadata = (
            self.events_published
            + self.events_consumed
            + self.required_permissions
            + self.configuration_keys
            + self.feature_flags
            + self.data_ownership
        )
        if any(not value.strip() for value in metadata):
            raise ValueError("Manifest metadata values must not be empty")
        if any(not prefix.startswith("/") for prefix in self.api_prefixes):
            raise ValueError("API prefixes must start with '/'")
