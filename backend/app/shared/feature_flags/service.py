"""Stable application-facing feature-flag service."""

from dataclasses import dataclass

from app.shared.feature_flags.flags import FeatureFlag
from app.shared.feature_flags.provider import FeatureFlagProvider


@dataclass(frozen=True, slots=True)
class FeatureFlagService:
    """Evaluate typed feature flags without authorization or clinical policy."""

    provider: FeatureFlagProvider

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Return a concrete boolean activation decision."""
        return self.provider.is_enabled(flag)
