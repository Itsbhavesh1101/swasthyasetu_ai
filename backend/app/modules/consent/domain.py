"""Framework-independent consent domain values and invariants."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType

from app.shared.types import OpaqueId

_SCOPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_REVOCATION_REASON_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
MAX_SCOPE_ITEMS = 32
MAX_NOTICE_VERSION_LENGTH = 64


class ConsentPurpose(StrEnum):
    GENERAL_PRODUCT_USE = "GENERAL_PRODUCT_USE"
    EXTERNAL_AI_PROCESSING = "EXTERNAL_AI_PROCESSING"
    REFERRAL_SHARING = "REFERRAL_SHARING"
    ABDM_EXCHANGE = "ABDM_EXCHANGE"
    RESEARCH_USE = "RESEARCH_USE"
    CAREGIVER_ACCESS = "CAREGIVER_ACCESS"


class ConsentStatus(StrEnum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"


class ConsentSubjectType(StrEnum):
    SESSION = "SESSION"
    ACTOR = "ACTOR"
    PATIENT = "PATIENT"


@dataclass(frozen=True, slots=True)
class ConsentScope:
    """Canonical non-empty collection of least-privilege machine scopes."""

    values: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.values, tuple):
            raise TypeError("consent scope values must be a tuple")
        if not self.values or len(self.values) > MAX_SCOPE_ITEMS:
            raise ValueError("consent scope must contain between 1 and 32 values")
        if len(set(self.values)) != len(self.values):
            raise ValueError("consent scope values must be unique")
        if any(_SCOPE_PATTERN.fullmatch(value) is None for value in self.values):
            raise ValueError("consent scope values must be bounded lowercase machine codes")
        object.__setattr__(self, "values", tuple(sorted(self.values)))

    def covers(self, required: ConsentScope) -> bool:
        return frozenset(required.values).issubset(self.values)


@dataclass(frozen=True, slots=True, order=True)
class NoticeVersion:
    value: str

    def __post_init__(self) -> None:
        if (
            not self.value
            or self.value != self.value.strip()
            or len(self.value) > MAX_NOTICE_VERSION_LENGTH
            or not self.value.isprintable()
        ):
            raise ValueError("notice version must be non-empty and at most 64 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class RevocationReason:
    value: str

    def __post_init__(self) -> None:
        if _REVOCATION_REASON_PATTERN.fullmatch(self.value) is None:
            raise ValueError("revocation reason must be a bounded machine-readable code")

    def __str__(self) -> str:
        return self.value


def normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    """Purpose-specific consent state with opaque subject references only."""

    consent_id: OpaqueId
    subject_type: ConsentSubjectType
    subject_id: OpaqueId
    actor_id: OpaqueId | None
    purpose: ConsentPurpose
    scope: ConsentScope
    notice_version: NoticeVersion
    status: ConsentStatus
    granted_at: datetime
    revoked_at: datetime | None
    revocation_reason: RevocationReason | None
    expires_at: datetime | None
    metadata: Mapping[str, object] | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        for name in ("granted_at", "created_at", "updated_at"):
            object.__setattr__(self, name, normalize_utc(name, getattr(self, name)))
        for name in ("revoked_at", "expires_at"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, normalize_utc(name, value))
        if self.status is ConsentStatus.GRANTED and (
            self.revoked_at is not None or self.revocation_reason is not None
        ):
            raise ValueError("GRANTED consent cannot contain revocation state")
        if self.status is ConsentStatus.REVOKED and (
            self.revoked_at is None or self.revocation_reason is None
        ):
            raise ValueError("REVOKED consent requires time and reason")
        if self.expires_at is not None and self.expires_at <= self.granted_at:
            raise ValueError("expires_at must be after granted_at")
        if self.revoked_at is not None and self.revoked_at < self.granted_at:
            raise ValueError("revoked_at must not precede granted_at")
        if self.metadata is not None:
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
