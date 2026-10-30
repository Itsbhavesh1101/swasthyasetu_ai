"""Immutable provider-neutral retention and purge contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from app.shared.types import OpaqueId

_POLICY_CODE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_POLICY_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_ERROR_CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


class PolicyCode(str):
    """Bounded policy identifier without embedded legal meaning."""

    def __new__(cls, value: str) -> PolicyCode:
        if not isinstance(value, str):
            raise TypeError("policy code must be a string")
        if _POLICY_CODE.fullmatch(value) is None:
            raise ValueError("policy code must be a bounded lowercase dotted name")
        return super().__new__(cls, value)


class PolicyVersion(str):
    """Bounded opaque version selected by the owning policy authority."""

    def __new__(cls, value: str) -> PolicyVersion:
        if not isinstance(value, str):
            raise TypeError("policy version must be a string")
        if _POLICY_VERSION.fullmatch(value) is None:
            raise ValueError("policy version must be a bounded machine-readable value")
        return super().__new__(cls, value)


class PurgeTargetKind(StrEnum):
    """Closed storage classes named by canonical architecture."""

    DATABASE_RECORD = "DATABASE_RECORD"
    OBJECT_STORAGE_OBJECT = "OBJECT_STORAGE_OBJECT"
    SEARCH_INDEX_ENTRY = "SEARCH_INDEX_ENTRY"
    CACHE_ENTRY = "CACHE_ENTRY"
    BACKUP_RECORD = "BACKUP_RECORD"


class PurgeAuthorizationDecision(StrEnum):
    """Decision supplied by an external policy/records authority."""

    AUTHORIZED = "AUTHORIZED"
    BLOCKED_BY_HOLD = "BLOCKED_BY_HOLD"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"


class PurgeTargetOutcome(StrEnum):
    """One idempotent target execution outcome."""

    DELETED = "DELETED"
    ALREADY_ABSENT = "ALREADY_ABSENT"
    FAILED = "FAILED"


class PurgeRunStatus(StrEnum):
    """Honest aggregate execution state."""

    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"
    FAILED = "FAILED"


def _utc(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _references(values: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError("hold references must be a tuple")
    if any(not isinstance(value, str) or _REFERENCE.fullmatch(value) is None for value in values):
        raise ValueError("hold references must be bounded machine-readable values")
    if len(set(values)) != len(values):
        raise ValueError("hold references must be unique")
    return values


@dataclass(frozen=True, slots=True)
class PurgeAuthorization:
    """Immutable result of policy evaluation performed outside this package."""

    decision: PurgeAuthorizationDecision
    policy_code: PolicyCode
    policy_version: PolicyVersion
    evaluated_at: datetime
    hold_references: tuple[str, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.decision, PurgeAuthorizationDecision):
            raise TypeError("authorization decision must be a PurgeAuthorizationDecision")
        if not isinstance(self.policy_code, PolicyCode):
            raise TypeError("policy_code must be a PolicyCode")
        if not isinstance(self.policy_version, PolicyVersion):
            raise TypeError("policy_version must be a PolicyVersion")
        object.__setattr__(self, "evaluated_at", _utc("evaluated_at", self.evaluated_at))
        holds = _references(self.hold_references)
        if self.decision is PurgeAuthorizationDecision.AUTHORIZED and holds:
            raise ValueError("authorized purge cannot include active hold references")
        if self.decision is PurgeAuthorizationDecision.BLOCKED_BY_HOLD and not holds:
            raise ValueError("hold-blocked purge requires at least one hold reference")


@dataclass(frozen=True, slots=True)
class PurgeTargetIdentity:
    """Opaque target identity without a store locator."""

    kind: PurgeTargetKind
    target_id: OpaqueId = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, PurgeTargetKind):
            raise TypeError("target kind must be a PurgeTargetKind")
        if not isinstance(self.target_id, OpaqueId):
            raise TypeError("target_id must be an OpaqueId")


@dataclass(frozen=True, slots=True)
class PurgeTarget:
    """One versioned deletion target; locator is deliberately representation-private."""

    identity: PurgeTargetIdentity
    generation: int
    locator: str = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.identity, PurgeTargetIdentity):
            raise TypeError("target identity must be a PurgeTargetIdentity")
        if not isinstance(self.generation, int) or isinstance(self.generation, bool):
            raise TypeError("target generation must be an integer")
        if self.generation <= 0:
            raise ValueError("target generation must be positive")
        if not isinstance(self.locator, str):
            raise TypeError("target locator must be a string")
        if (
            not self.locator
            or self.locator != self.locator.strip()
            or len(self.locator) > 512
            or not self.locator.isprintable()
        ):
            raise ValueError("target locator must be a bounded printable opaque value")


@dataclass(frozen=True, slots=True)
class PurgePlan:
    """Immutable explicit plan; it never derives policy or retention duration."""

    plan_id: OpaqueId
    subject_id: OpaqueId = field(repr=False)
    requested_at: datetime
    authorization: PurgeAuthorization
    targets: tuple[PurgeTarget, ...] = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, OpaqueId):
            raise TypeError("plan_id must be an OpaqueId")
        if not isinstance(self.subject_id, OpaqueId):
            raise TypeError("subject_id must be an OpaqueId")
        if not isinstance(self.authorization, PurgeAuthorization):
            raise TypeError("authorization must be a PurgeAuthorization")
        if not isinstance(self.targets, tuple) or not self.targets:
            raise ValueError("purge plan requires at least one target")
        if any(not isinstance(item, PurgeTarget) for item in self.targets):
            raise TypeError("purge plan targets must be PurgeTarget values")
        identities = [item.identity for item in self.targets]
        if len(set(identities)) != len(identities):
            raise ValueError("purge plan cannot contain duplicate target identities")
        object.__setattr__(self, "requested_at", _utc("requested_at", self.requested_at))


@dataclass(frozen=True, slots=True)
class PurgeTargetReceipt:
    """Privacy-safe result for one exact target."""

    target: PurgeTarget = field(repr=False)
    outcome: PurgeTargetOutcome
    error_code: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target, PurgeTarget):
            raise TypeError("receipt target must be a PurgeTarget")
        if not isinstance(self.outcome, PurgeTargetOutcome):
            raise TypeError("receipt outcome must be a PurgeTargetOutcome")
        if self.outcome is PurgeTargetOutcome.FAILED:
            if (
                not isinstance(self.error_code, str)
                or _ERROR_CODE.fullmatch(self.error_code) is None
            ):
                raise ValueError("failed purge receipt requires a generic error code")
        elif self.error_code is not None:
            raise ValueError("successful purge receipt cannot include an error code")


@dataclass(frozen=True, slots=True)
class PurgeRunResult:
    """Aggregate run result with strict status/receipt consistency."""

    plan_id: OpaqueId
    status: PurgeRunStatus
    receipts: tuple[PurgeTargetReceipt, ...] = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, OpaqueId):
            raise TypeError("plan_id must be an OpaqueId")
        if not isinstance(self.status, PurgeRunStatus):
            raise TypeError("run status must be a PurgeRunStatus")
        if not isinstance(self.receipts, tuple) or any(
            not isinstance(item, PurgeTargetReceipt) for item in self.receipts
        ):
            raise TypeError("run receipts must be a tuple of PurgeTargetReceipt values")
        failed = any(item.outcome is PurgeTargetOutcome.FAILED for item in self.receipts)
        if self.status is PurgeRunStatus.BLOCKED and self.receipts:
            raise ValueError("blocked purge cannot contain receipts")
        if self.status is PurgeRunStatus.COMPLETED and (not self.receipts or failed):
            raise ValueError("completed purge requires only successful receipts")
        failed_count = sum(item.outcome is PurgeTargetOutcome.FAILED for item in self.receipts)
        if self.status is PurgeRunStatus.PARTIAL_FAILURE and (
            failed_count == 0 or failed_count == len(self.receipts)
        ):
            raise ValueError("partial purge requires both successful and failed receipts")
        if self.status is PurgeRunStatus.FAILED and (
            not self.receipts or failed_count != len(self.receipts)
        ):
            raise ValueError("failed purge requires every receipt to be failed")


class PurgeTargetAdapter(Protocol):
    """Idempotently delete one exact target generation from one storage class."""

    kind: PurgeTargetKind

    async def purge(self, target: PurgeTarget) -> PurgeTargetReceipt: ...


class PurgeObserver(Protocol):
    """Observe bounded target outcomes without identifiers or content."""

    def record(self, receipt: PurgeTargetReceipt) -> None: ...
