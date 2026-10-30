"""Strict provider-neutral contracts for optional dependency resilience."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol


class OptionalCapability(StrEnum):
    """Closed optional capability inventory derived from canonical P22 documents."""

    LLM_GENERATION = "LLM_GENERATION"
    OCR_PROCESSING = "OCR_PROCESSING"
    SPEECH_PROCESSING = "SPEECH_PROCESSING"
    REFERRAL_DELIVERY = "REFERRAL_DELIVERY"
    FHIR_EXCHANGE = "FHIR_EXCHANGE"
    ABDM_SYNC = "ABDM_SYNC"
    SELF_CARE = "SELF_CARE"
    QML_INFERENCE = "QML_INFERENCE"
    RESOURCE_DIRECTORY = "RESOURCE_DIRECTORY"
    LANGUAGE_PATH = "LANGUAGE_PATH"
    POLICY_VERSION = "POLICY_VERSION"


class CapabilityControlState(StrEnum):
    """Process-local fail-safe state; disabled states never authorize execution."""

    AVAILABLE = "AVAILABLE"
    DISABLED_BY_DEFAULT = "DISABLED_BY_DEFAULT"
    TRIPPED = "TRIPPED"


class KillSwitchReason(StrEnum):
    """Bounded operational reasons without incident or patient content."""

    MANUAL_SAFETY = "MANUAL_SAFETY"
    DEPENDENCY_UNHEALTHY = "DEPENDENCY_UNHEALTHY"
    INCIDENT = "INCIDENT"
    STALE_RESOURCE = "STALE_RESOURCE"
    POLICY_ROLLBACK = "POLICY_ROLLBACK"


class DependencyFailureKind(StrEnum):
    """Closed failure classification supplied by optional dependency adapters."""

    TIMEOUT = "TIMEOUT"
    UNAVAILABLE = "UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    REJECTED = "REJECTED"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    UNKNOWN = "UNKNOWN"


class DependencyOutcomeState(StrEnum):
    """Honest aggregate state for one guarded optional dependency call."""

    SUCCEEDED = "SUCCEEDED"
    DEGRADED_DISABLED = "DEGRADED_DISABLED"
    DEGRADED_FAILURE = "DEGRADED_FAILURE"


class ResilienceFailureCode(StrEnum):
    """Privacy-safe failure codes returned to callers and telemetry."""

    SWITCH_DISABLED = "SWITCH_DISABLED"
    DEPENDENCY_TIMEOUT = "DEPENDENCY_TIMEOUT"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    DEPENDENCY_RATE_LIMITED = "DEPENDENCY_RATE_LIMITED"
    DEPENDENCY_REJECTED = "DEPENDENCY_REJECTED"
    DEPENDENCY_INVALID_RESPONSE = "DEPENDENCY_INVALID_RESPONSE"
    DEPENDENCY_UNKNOWN = "DEPENDENCY_UNKNOWN"


def normalize_utc(name: str, value: datetime) -> datetime:
    """Reject naive timestamps and normalize aware values to UTC."""
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded per-attempt and total deadline policy for an idempotent operation."""

    attempt_timeout_seconds: float
    total_timeout_seconds: float
    retry_budget: int = 0
    idempotent: bool = False

    def __post_init__(self) -> None:
        for name, value in (
            ("attempt_timeout_seconds", self.attempt_timeout_seconds),
            ("total_timeout_seconds", self.total_timeout_seconds),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be a number")
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.attempt_timeout_seconds > 10:
            raise ValueError("attempt timeout cannot exceed 10 seconds")
        if self.total_timeout_seconds > 30:
            raise ValueError("total timeout cannot exceed 30 seconds")
        if self.total_timeout_seconds < self.attempt_timeout_seconds:
            raise ValueError("total timeout cannot be shorter than attempt timeout")
        if not isinstance(self.retry_budget, int) or isinstance(self.retry_budget, bool):
            raise TypeError("retry budget must be an integer")
        if not 0 <= self.retry_budget <= 3:
            raise ValueError("retry budget must be between zero and three")
        if not isinstance(self.idempotent, bool):
            raise TypeError("idempotent must be a boolean")
        if self.retry_budget and not self.idempotent:
            raise ValueError("non-idempotent operations cannot be retried")


@dataclass(frozen=True, slots=True)
class CapabilitySwitchSnapshot:
    """Immutable privacy-safe state for one optional capability."""

    capability: OptionalCapability
    state: CapabilityControlState
    reason: KillSwitchReason | None = None
    tripped_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability, OptionalCapability):
            raise TypeError("capability must be an OptionalCapability")
        if not isinstance(self.state, CapabilityControlState):
            raise TypeError("state must be a CapabilityControlState")
        if self.state is CapabilityControlState.TRIPPED:
            if not isinstance(self.reason, KillSwitchReason) or self.tripped_at is None:
                raise ValueError("tripped switch requires reason and timestamp")
            object.__setattr__(self, "tripped_at", normalize_utc("tripped_at", self.tripped_at))
        elif self.reason is not None or self.tripped_at is not None:
            raise ValueError("non-tripped switch cannot include trip metadata")


@dataclass(frozen=True, slots=True)
class DependencyOutcome[T]:
    """Typed outcome that cannot represent degraded work as success."""

    capability: OptionalCapability
    state: DependencyOutcomeState
    attempts: int
    value: T | None = field(default=None, repr=False)
    failure_code: ResilienceFailureCode | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability, OptionalCapability):
            raise TypeError("capability must be an OptionalCapability")
        if not isinstance(self.state, DependencyOutcomeState):
            raise TypeError("state must be a DependencyOutcomeState")
        if not isinstance(self.attempts, int) or isinstance(self.attempts, bool):
            raise TypeError("attempts must be an integer")
        if self.attempts < 0 or self.attempts > 4:
            raise ValueError("attempts must be between zero and four")
        if self.state is DependencyOutcomeState.SUCCEEDED:
            if self.attempts < 1 or self.value is None or self.failure_code is not None:
                raise ValueError("successful outcome requires attempts and a value only")
        else:
            if self.value is not None or not isinstance(self.failure_code, ResilienceFailureCode):
                raise ValueError("degraded outcome requires only a failure code")
            if (
                self.state is DependencyOutcomeState.DEGRADED_DISABLED
                and self.failure_code is not ResilienceFailureCode.SWITCH_DISABLED
            ):
                raise ValueError("disabled outcome requires SWITCH_DISABLED")
            if (
                self.state is DependencyOutcomeState.DEGRADED_FAILURE
                and self.failure_code is ResilienceFailureCode.SWITCH_DISABLED
            ):
                raise ValueError("dependency failure cannot use SWITCH_DISABLED")


class DependencyFailure(Exception):
    """Adapter failure containing only closed, privacy-safe fields."""

    def __init__(self, kind: DependencyFailureKind, *, retryable: bool) -> None:
        if not isinstance(kind, DependencyFailureKind):
            raise TypeError("failure kind must be a DependencyFailureKind")
        if not isinstance(retryable, bool):
            raise TypeError("retryable must be a boolean")
        self.kind = kind
        self.retryable = retryable
        super().__init__(kind.value)


class ResilienceObserver(Protocol):
    """Observe only bounded switch and outcome fields."""

    def record_switch(self, snapshot: CapabilitySwitchSnapshot) -> None: ...

    def record_outcome(self, outcome: DependencyOutcome[object]) -> None: ...
