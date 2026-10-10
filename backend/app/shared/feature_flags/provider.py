"""Feature-flag provider contract and immutable configuration provider."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from app.shared.feature_flags.flags import FeatureFlag


class FeatureFlagProvider(Protocol):
    """Framework-independent source of feature activation decisions."""

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Return whether the explicitly identified optional feature is enabled."""
        ...


@dataclass(frozen=True, slots=True)
class ConfigurationFeatureFlagProvider:
    """Immutable provider whose absent flags always evaluate safe/off."""

    enabled: frozenset[FeatureFlag]

    @classmethod
    def from_names(cls, names: Iterable[str]) -> "ConfigurationFeatureFlagProvider":
        """Build a provider from validated configuration names."""
        return cls(enabled=frozenset(FeatureFlag(name) for name in names))

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Return true only for a flag explicitly present in configuration."""
        return flag in self.enabled
