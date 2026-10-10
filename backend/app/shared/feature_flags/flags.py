"""Stable feature-flag identifiers."""

import re
from typing import Final

_FEATURE_FLAG_PATTERN: Final = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class FeatureFlag(str):
    """A validated, lowercase snake-case feature-flag identifier."""

    def __new__(cls, value: str) -> "FeatureFlag":
        if not isinstance(value, str) or not _FEATURE_FLAG_PATTERN.fullmatch(value):
            raise ValueError("feature flag must use lowercase snake case")
        return super().__new__(cls, value)
