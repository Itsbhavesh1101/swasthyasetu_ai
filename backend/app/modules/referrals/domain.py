"""Synthetic-only referral lifecycle and idempotency mechanics.

The status names mirror the canonical vocabulary, but this module deliberately bundles no
transition policy and represents no consent, destination, delivery, or external evidence.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

REFERRAL_LIFECYCLE_SCHEMA_VERSION: Final = "synthetic-referral-lifecycle.v1"
MAX_REFERRAL_VERSION: Final = 1_000_000
MAX_TRANSITIONS: Final = 128
MAX_RECEIPTS: Final = 256

_REFERRAL_ID = re.compile(r"^syn_referral_[a-z0-9][a-z0-9_]{0,95}$")
_COMMAND_ID = re.compile(r"^syn_referral_command_[a-z0-9][a-z0-9_]{0,95}$")
_IDEMPOTENCY_KEY = re.compile(r"^syn_referral_idem_[a-z0-9][a-z0-9_]{0,95}$")
_POLICY_ID = re.compile(r"^syn_referral_policy_[a-z0-9][a-z0-9_]{0,95}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class ReferralDomainCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    STALE_STATE = "STALE_STATE"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"


class ReferralDomainError(ValueError):
    """Stable, content-free failure for detached synthetic mechanics."""

    def __init__(self, code: ReferralDomainCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: ReferralDomainCode) -> ReferralDomainError:
    return ReferralDomainError(code)


class SyntheticReferralAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticReferralClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class SyntheticReferralVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticReferralStatus(StrEnum):
    OFFERED = "OFFERED"
    CONSENTED = "CONSENTED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    UNREACHABLE = "UNREACHABLE"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReferralApplicationDisposition(StrEnum):
    APPLIED = "APPLIED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


def _machine_value(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise _fail(ReferralDomainCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _fail(ReferralDomainCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _positive(value: object) -> int:
    if type(value) is not int:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    if not 1 <= value <= MAX_REFERRAL_VERSION:
        raise _fail(ReferralDomainCode.LIMIT_EXCEEDED)
    return value


def _fixed_authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticReferralAuthority)
    _strict_enum(classification, SyntheticReferralClassification)
    _strict_enum(verification, SyntheticReferralVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReferral:
    referral_id: str
    version: int
    status: SyntheticReferralStatus
    created_at: datetime
    updated_at: datetime
    schema_version: str = REFERRAL_LIFECYCLE_SCHEMA_VERSION
    authority: SyntheticReferralAuthority = SyntheticReferralAuthority.ENGINEERING_ONLY
    classification: SyntheticReferralClassification = (
        SyntheticReferralClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticReferralVerification = SyntheticReferralVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.referral_id, _REFERRAL_ID)
        version = _positive(self.version)
        _strict_enum(self.status, SyntheticReferralStatus)
        created_at = _utc(self.created_at)
        updated_at = _utc(self.updated_at)
        if updated_at < created_at:
            raise _fail(ReferralDomainCode.INVALID_CHRONOLOGY)
        if self.schema_version != REFERRAL_LIFECYCLE_SCHEMA_VERSION:
            raise _fail(ReferralDomainCode.INVALID_VALUE)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)


def _snapshot_referral(value: object) -> SyntheticReferral:
    if type(value) is not SyntheticReferral:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    try:
        return SyntheticReferral(
            referral_id=value.referral_id,
            version=value.version,
            status=value.status,
            created_at=value.created_at,
            updated_at=value.updated_at,
            schema_version=value.schema_version,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except ReferralDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(ReferralDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferralTransitionPair:
    from_status: SyntheticReferralStatus
    to_status: SyntheticReferralStatus

    def __post_init__(self) -> None:
        _strict_enum(self.from_status, SyntheticReferralStatus)
        _strict_enum(self.to_status, SyntheticReferralStatus)
        if self.from_status is self.to_status:
            raise _fail(ReferralDomainCode.INVALID_TRANSITION)


def _snapshot_pair(value: object) -> ReferralTransitionPair:
    if type(value) is not ReferralTransitionPair:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    try:
        return ReferralTransitionPair(from_status=value.from_status, to_status=value.to_status)
    except ReferralDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(ReferralDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticTransitionPolicy:
    policy_id: str
    policy_version: str
    artifact_hash: str = field(repr=False)
    allowed_transitions: tuple[ReferralTransitionPair, ...]
    activated_at: datetime
    authority: SyntheticReferralAuthority = SyntheticReferralAuthority.ENGINEERING_ONLY
    classification: SyntheticReferralClassification = (
        SyntheticReferralClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticReferralVerification = SyntheticReferralVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.policy_id, _POLICY_ID)
        _machine_value(self.policy_version, _VERSION)
        _machine_value(self.artifact_hash, _SHA256)
        if type(self.allowed_transitions) is not tuple:
            raise _fail(ReferralDomainCode.INVALID_TYPE)
        if not self.allowed_transitions or len(self.allowed_transitions) > MAX_TRANSITIONS:
            raise _fail(ReferralDomainCode.LIMIT_EXCEEDED)
        transitions = tuple(
            sorted(
                (_snapshot_pair(item) for item in self.allowed_transitions),
                key=lambda item: (item.from_status.value, item.to_status.value),
            )
        )
        if len(set(transitions)) != len(transitions):
            raise _fail(ReferralDomainCode.DUPLICATE_IDENTITY)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "allowed_transitions", transitions)
        object.__setattr__(self, "activated_at", _utc(self.activated_at))


def _snapshot_policy(value: object) -> SyntheticTransitionPolicy:
    if type(value) is not SyntheticTransitionPolicy:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    try:
        return SyntheticTransitionPolicy(
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            artifact_hash=value.artifact_hash,
            allowed_transitions=value.allowed_transitions,
            activated_at=value.activated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except ReferralDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(ReferralDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferralTransitionCommand:
    command_id: str
    referral_id: str
    idempotency_key: str = field(repr=False)
    expected_version: int
    from_status: SyntheticReferralStatus
    to_status: SyntheticReferralStatus
    occurred_at: datetime
    authority: SyntheticReferralAuthority = SyntheticReferralAuthority.ENGINEERING_ONLY
    classification: SyntheticReferralClassification = (
        SyntheticReferralClassification.ENGINEERING_SYNTHETIC
    )

    def __post_init__(self) -> None:
        _machine_value(self.command_id, _COMMAND_ID)
        _machine_value(self.referral_id, _REFERRAL_ID)
        _machine_value(self.idempotency_key, _IDEMPOTENCY_KEY)
        expected_version = _positive(self.expected_version)
        _strict_enum(self.from_status, SyntheticReferralStatus)
        _strict_enum(self.to_status, SyntheticReferralStatus)
        if self.from_status is self.to_status:
            raise _fail(ReferralDomainCode.INVALID_TRANSITION)
        _strict_enum(self.authority, SyntheticReferralAuthority)
        _strict_enum(self.classification, SyntheticReferralClassification)
        object.__setattr__(self, "expected_version", expected_version)
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))


def _snapshot_command(value: object) -> ReferralTransitionCommand:
    if type(value) is not ReferralTransitionCommand:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    try:
        return ReferralTransitionCommand(
            command_id=value.command_id,
            referral_id=value.referral_id,
            idempotency_key=value.idempotency_key,
            expected_version=value.expected_version,
            from_status=value.from_status,
            to_status=value.to_status,
            occurred_at=value.occurred_at,
            authority=value.authority,
            classification=value.classification,
        )
    except ReferralDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(ReferralDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferralTransitionReceipt:
    command_id: str
    referral_id: str
    idempotency_key: str = field(repr=False)
    command_fingerprint: str = field(repr=False)
    previous_status: SyntheticReferralStatus
    result_status: SyntheticReferralStatus
    previous_version: int
    result_version: int
    applied_at: datetime
    policy_id: str
    policy_version: str
    policy_artifact_hash: str = field(repr=False)
    authority: SyntheticReferralAuthority = SyntheticReferralAuthority.ENGINEERING_ONLY
    classification: SyntheticReferralClassification = (
        SyntheticReferralClassification.ENGINEERING_SYNTHETIC
    )

    def __post_init__(self) -> None:
        _machine_value(self.command_id, _COMMAND_ID)
        _machine_value(self.referral_id, _REFERRAL_ID)
        _machine_value(self.idempotency_key, _IDEMPOTENCY_KEY)
        _machine_value(self.command_fingerprint, _SHA256)
        _strict_enum(self.previous_status, SyntheticReferralStatus)
        _strict_enum(self.result_status, SyntheticReferralStatus)
        if self.previous_status is self.result_status:
            raise _fail(ReferralDomainCode.INVALID_TRANSITION)
        previous_version = _positive(self.previous_version)
        result_version = _positive(self.result_version)
        if result_version != previous_version + 1:
            raise _fail(ReferralDomainCode.STALE_STATE)
        _machine_value(self.policy_id, _POLICY_ID)
        _machine_value(self.policy_version, _VERSION)
        _machine_value(self.policy_artifact_hash, _SHA256)
        _strict_enum(self.authority, SyntheticReferralAuthority)
        _strict_enum(self.classification, SyntheticReferralClassification)
        object.__setattr__(self, "previous_version", previous_version)
        object.__setattr__(self, "result_version", result_version)
        object.__setattr__(self, "applied_at", _utc(self.applied_at))


def _snapshot_receipt(value: object) -> ReferralTransitionReceipt:
    if type(value) is not ReferralTransitionReceipt:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    try:
        return ReferralTransitionReceipt(
            command_id=value.command_id,
            referral_id=value.referral_id,
            idempotency_key=value.idempotency_key,
            command_fingerprint=value.command_fingerprint,
            previous_status=value.previous_status,
            result_status=value.result_status,
            previous_version=value.previous_version,
            result_version=value.result_version,
            applied_at=value.applied_at,
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            policy_artifact_hash=value.policy_artifact_hash,
            authority=value.authority,
            classification=value.classification,
        )
    except ReferralDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(ReferralDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferralTransitionApplication:
    referral: SyntheticReferral
    receipt: ReferralTransitionReceipt
    disposition: ReferralApplicationDisposition

    def __post_init__(self) -> None:
        referral = _snapshot_referral(self.referral)
        receipt = _snapshot_receipt(self.receipt)
        _strict_enum(self.disposition, ReferralApplicationDisposition)
        if referral.referral_id != receipt.referral_id or referral.version < receipt.result_version:
            raise _fail(ReferralDomainCode.STALE_STATE)
        if referral.version == receipt.result_version and (
            referral.status is not receipt.result_status
            or referral.updated_at != receipt.applied_at
        ):
            raise _fail(ReferralDomainCode.STALE_STATE)
        if referral.updated_at < receipt.applied_at:
            raise _fail(ReferralDomainCode.INVALID_CHRONOLOGY)
        if self.disposition is ReferralApplicationDisposition.APPLIED and (
            referral.version != receipt.result_version
            or referral.status is not receipt.result_status
            or referral.updated_at != receipt.applied_at
        ):
            raise _fail(ReferralDomainCode.STALE_STATE)
        object.__setattr__(self, "referral", referral)
        object.__setattr__(self, "receipt", receipt)


def _command_fingerprint(
    command: ReferralTransitionCommand, policy: SyntheticTransitionPolicy
) -> str:
    value = "|".join(
        (
            command.command_id,
            command.referral_id,
            command.idempotency_key,
            str(command.expected_version),
            command.from_status.value,
            command.to_status.value,
            command.occurred_at.isoformat(),
            policy.policy_id,
            policy.policy_version,
            policy.artifact_hash,
        )
    )
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _receipt_matches_command(
    receipt: ReferralTransitionReceipt,
    command: ReferralTransitionCommand,
    policy: SyntheticTransitionPolicy,
    fingerprint: str,
) -> bool:
    return (
        receipt.command_id == command.command_id
        and receipt.referral_id == command.referral_id
        and receipt.command_fingerprint == fingerprint
        and receipt.previous_status is command.from_status
        and receipt.result_status is command.to_status
        and receipt.previous_version == command.expected_version
        and receipt.applied_at == command.occurred_at
        and receipt.policy_id == policy.policy_id
        and receipt.policy_version == policy.policy_version
        and receipt.policy_artifact_hash == policy.artifact_hash
    )


def apply_synthetic_transition(
    referral: SyntheticReferral,
    command: ReferralTransitionCommand,
    policy: SyntheticTransitionPolicy,
    *,
    prior_receipts: tuple[ReferralTransitionReceipt, ...] = (),
) -> ReferralTransitionApplication:
    """Apply one explicit synthetic policy pair or return an exact idempotent no-op."""

    current = _snapshot_referral(referral)
    transition = _snapshot_command(command)
    configured_policy = _snapshot_policy(policy)
    if type(prior_receipts) is not tuple:
        raise _fail(ReferralDomainCode.INVALID_TYPE)
    if len(prior_receipts) > MAX_RECEIPTS:
        raise _fail(ReferralDomainCode.LIMIT_EXCEEDED)
    receipts = tuple(_snapshot_receipt(item) for item in prior_receipts)
    keys = tuple(item.idempotency_key for item in receipts)
    command_ids = tuple(item.command_id for item in receipts)
    if len(set(keys)) != len(keys) or len(set(command_ids)) != len(command_ids):
        raise _fail(ReferralDomainCode.DUPLICATE_IDENTITY)

    if current.referral_id != transition.referral_id:
        raise _fail(ReferralDomainCode.IDENTITY_MISMATCH)
    if any(item.referral_id != current.referral_id for item in receipts):
        raise _fail(ReferralDomainCode.IDENTITY_MISMATCH)
    if configured_policy.activated_at > transition.occurred_at:
        raise _fail(ReferralDomainCode.INVALID_CHRONOLOGY)
    transition_pair = ReferralTransitionPair(
        from_status=transition.from_status,
        to_status=transition.to_status,
    )
    if transition_pair not in configured_policy.allowed_transitions:
        raise _fail(ReferralDomainCode.TRANSITION_NOT_ALLOWED)

    fingerprint = _command_fingerprint(transition, configured_policy)
    existing = next(
        (item for item in receipts if item.idempotency_key == transition.idempotency_key), None
    )
    if existing is not None:
        if not _receipt_matches_command(existing, transition, configured_policy, fingerprint):
            raise _fail(ReferralDomainCode.IDEMPOTENCY_CONFLICT)
        if current.version < existing.result_version:
            raise _fail(ReferralDomainCode.STALE_STATE)
        return ReferralTransitionApplication(
            referral=current,
            receipt=existing,
            disposition=ReferralApplicationDisposition.IDEMPOTENT_REPLAY,
        )

    if (
        current.version != transition.expected_version
        or current.status is not transition.from_status
    ):
        raise _fail(ReferralDomainCode.STALE_STATE)
    if transition.occurred_at < current.updated_at:
        raise _fail(ReferralDomainCode.INVALID_CHRONOLOGY)
    if current.version == MAX_REFERRAL_VERSION:
        raise _fail(ReferralDomainCode.LIMIT_EXCEEDED)

    result = SyntheticReferral(
        referral_id=current.referral_id,
        version=current.version + 1,
        status=transition.to_status,
        created_at=current.created_at,
        updated_at=transition.occurred_at,
    )
    receipt = ReferralTransitionReceipt(
        command_id=transition.command_id,
        referral_id=transition.referral_id,
        idempotency_key=transition.idempotency_key,
        command_fingerprint=fingerprint,
        previous_status=transition.from_status,
        result_status=transition.to_status,
        previous_version=transition.expected_version,
        result_version=result.version,
        applied_at=transition.occurred_at,
        policy_id=configured_policy.policy_id,
        policy_version=configured_policy.policy_version,
        policy_artifact_hash=configured_policy.artifact_hash,
    )
    return ReferralTransitionApplication(
        referral=result,
        receipt=receipt,
        disposition=ReferralApplicationDisposition.APPLIED,
    )


__all__ = [
    "ReferralApplicationDisposition",
    "ReferralDomainCode",
    "ReferralDomainError",
    "ReferralTransitionApplication",
    "ReferralTransitionCommand",
    "ReferralTransitionPair",
    "ReferralTransitionReceipt",
    "SyntheticReferral",
    "SyntheticReferralAuthority",
    "SyntheticReferralClassification",
    "SyntheticReferralStatus",
    "SyntheticReferralVerification",
    "SyntheticTransitionPolicy",
    "apply_synthetic_transition",
]
