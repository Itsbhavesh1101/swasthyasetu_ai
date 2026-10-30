"""Provider-neutral immutable rate-limit contracts."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

_RULE_NAME = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class RateLimitRule:
    """One named sliding-window budget."""

    name: str
    limit: int
    window_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _RULE_NAME.fullmatch(self.name):
            raise ValueError("rate-limit rule name must use lowercase snake case")
        if not isinstance(self.limit, int) or isinstance(self.limit, bool) or self.limit <= 0:
            raise ValueError("rate-limit rule limit must be positive")
        if (
            not isinstance(self.window_seconds, (int, float))
            or isinstance(self.window_seconds, bool)
            or not math.isfinite(self.window_seconds)
            or self.window_seconds <= 0
        ):
            raise ValueError("rate-limit rule window must be finite and positive")


@dataclass(frozen=True, slots=True)
class RateLimitSubject:
    """A rule applied to one privacy-bounded subject key."""

    rule: RateLimitRule
    key: str

    def __post_init__(self) -> None:
        if not isinstance(self.rule, RateLimitRule):
            raise ValueError("rate-limit subject rule must be a RateLimitRule")
        if not isinstance(self.key, str) or not self.key or len(self.key) > 256:
            raise ValueError("rate-limit subject key must contain 1 to 256 characters")

    @property
    def storage_key(self) -> str:
        return f"{self.rule.name}:{self.key}"


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Atomic result for every applicable layer."""

    allowed: bool
    retry_after_seconds: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise ValueError("rate-limit decision allowed flag must be boolean")
        if self.allowed and self.retry_after_seconds is not None:
            raise ValueError("allowed rate-limit decision cannot include retry delay")
        if not self.allowed and (
            self.retry_after_seconds is None
            or not isinstance(self.retry_after_seconds, (int, float))
            or isinstance(self.retry_after_seconds, bool)
            or not math.isfinite(self.retry_after_seconds)
            or self.retry_after_seconds <= 0
        ):
            raise ValueError("denied rate-limit decision requires a positive finite retry delay")

    @classmethod
    def allowed_request(cls) -> RateLimitDecision:
        return cls(allowed=True)

    @classmethod
    def denied_request(cls, retry_after_seconds: float) -> RateLimitDecision:
        return cls(allowed=False, retry_after_seconds=retry_after_seconds)


class RateLimiter(Protocol):
    """Atomically evaluate every limit applicable to one request."""

    async def check(self, subjects: Sequence[RateLimitSubject]) -> RateLimitDecision: ...
