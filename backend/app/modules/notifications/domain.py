"""Synthetic notification intent and simulated-failure contracts.

This module has no recipient, channel, message body, delivery port, success state, or retry policy.
It records offline engineering failures only and cannot send a notification.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

MAX_SAFE_VARIABLES: Final = 32

_VARIABLE_KEY = re.compile(r"^syn_var_[a-z0-9][a-z0-9_]{0,63}$")
_VARIABLE_VALUE = re.compile(r"^syn_value_[a-z0-9][a-z0-9_]{0,95}$")
_TEMPLATE_ID = re.compile(r"^syn_notification_template_[a-z0-9][a-z0-9_]{0,95}$")
_NOTIFICATION_ID = re.compile(
    r"^syn_notification_(?!(?:template|correlation|failure)_)[a-z0-9][a-z0-9_]{0,95}$"
)
_CORRELATION_ID = re.compile(r"^syn_notification_correlation_[a-z0-9][a-z0-9_]{0,95}$")
_FAILURE_ID = re.compile(r"^syn_notification_failure_[a-z0-9][a-z0-9_]{0,95}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class NotificationDomainCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    TEMPLATE_MISMATCH = "TEMPLATE_MISMATCH"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"


class NotificationDomainError(ValueError):
    """Stable, content-free failure for synthetic notification contracts."""

    def __init__(self, code: NotificationDomainCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: NotificationDomainCode) -> NotificationDomainError:
    return NotificationDomainError(code)


class SyntheticNotificationAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticNotificationClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class SyntheticNotificationVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticFailureCode(StrEnum):
    SIMULATED_UNAVAILABLE = "SIMULATED_UNAVAILABLE"
    SIMULATED_TIMEOUT = "SIMULATED_TIMEOUT"
    SIMULATED_REJECTED = "SIMULATED_REJECTED"
    SIMULATED_AMBIGUOUS = "SIMULATED_AMBIGUOUS"


def _machine_value(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise _fail(NotificationDomainCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _fail(NotificationDomainCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _fail(NotificationDomainCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _fixed_authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticNotificationAuthority)
    _strict_enum(classification, SyntheticNotificationClassification)
    _strict_enum(verification, SyntheticNotificationVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SafeSyntheticVariable:
    key: str
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        _machine_value(self.key, _VARIABLE_KEY)
        _machine_value(self.value, _VARIABLE_VALUE)


def _snapshot_variable(value: object) -> SafeSyntheticVariable:
    if type(value) is not SafeSyntheticVariable:
        raise _fail(NotificationDomainCode.INVALID_TYPE)
    try:
        return SafeSyntheticVariable(key=value.key, value=value.value)
    except NotificationDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(NotificationDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticNotificationTemplate:
    """Metadata allowlist only; it intentionally contains no message copy."""

    template_id: str
    template_version: str
    artifact_hash: str = field(repr=False)
    allowed_variable_keys: tuple[str, ...]
    created_at: datetime
    authority: SyntheticNotificationAuthority = SyntheticNotificationAuthority.ENGINEERING_ONLY
    classification: SyntheticNotificationClassification = (
        SyntheticNotificationClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticNotificationVerification = SyntheticNotificationVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.template_id, _TEMPLATE_ID)
        _machine_value(self.template_version, _VERSION)
        _machine_value(self.artifact_hash, _SHA256)
        if type(self.allowed_variable_keys) is not tuple:
            raise _fail(NotificationDomainCode.INVALID_TYPE)
        if not self.allowed_variable_keys or len(self.allowed_variable_keys) > MAX_SAFE_VARIABLES:
            raise _fail(NotificationDomainCode.LIMIT_EXCEEDED)
        keys = tuple(
            sorted(_machine_value(item, _VARIABLE_KEY) for item in self.allowed_variable_keys)
        )
        if len(set(keys)) != len(keys):
            raise _fail(NotificationDomainCode.DUPLICATE_IDENTITY)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "allowed_variable_keys", keys)
        object.__setattr__(self, "created_at", _utc(self.created_at))


def _snapshot_template(value: object) -> SyntheticNotificationTemplate:
    if type(value) is not SyntheticNotificationTemplate:
        raise _fail(NotificationDomainCode.INVALID_TYPE)
    try:
        return SyntheticNotificationTemplate(
            template_id=value.template_id,
            template_version=value.template_version,
            artifact_hash=value.artifact_hash,
            allowed_variable_keys=value.allowed_variable_keys,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except NotificationDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(NotificationDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticNotificationIntent:
    """Content-free offline intent metadata; not a request to deliver anything."""

    notification_id: str
    correlation_id: str
    template_id: str
    template_version: str
    template_artifact_hash: str = field(repr=False)
    variables: tuple[SafeSyntheticVariable, ...]
    created_at: datetime
    authority: SyntheticNotificationAuthority = SyntheticNotificationAuthority.ENGINEERING_ONLY
    classification: SyntheticNotificationClassification = (
        SyntheticNotificationClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticNotificationVerification = SyntheticNotificationVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.notification_id, _NOTIFICATION_ID)
        _machine_value(self.correlation_id, _CORRELATION_ID)
        _machine_value(self.template_id, _TEMPLATE_ID)
        _machine_value(self.template_version, _VERSION)
        _machine_value(self.template_artifact_hash, _SHA256)
        if type(self.variables) is not tuple:
            raise _fail(NotificationDomainCode.INVALID_TYPE)
        if not self.variables or len(self.variables) > MAX_SAFE_VARIABLES:
            raise _fail(NotificationDomainCode.LIMIT_EXCEEDED)
        variables = tuple(
            sorted((_snapshot_variable(item) for item in self.variables), key=lambda item: item.key)
        )
        if len({item.key for item in variables}) != len(variables):
            raise _fail(NotificationDomainCode.DUPLICATE_IDENTITY)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "variables", variables)
        object.__setattr__(self, "created_at", _utc(self.created_at))


def _snapshot_intent(value: object) -> SyntheticNotificationIntent:
    if type(value) is not SyntheticNotificationIntent:
        raise _fail(NotificationDomainCode.INVALID_TYPE)
    try:
        return SyntheticNotificationIntent(
            notification_id=value.notification_id,
            correlation_id=value.correlation_id,
            template_id=value.template_id,
            template_version=value.template_version,
            template_artifact_hash=value.template_artifact_hash,
            variables=value.variables,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except NotificationDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(NotificationDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticNotificationFailure:
    failure_id: str
    notification_id: str
    code: SyntheticFailureCode
    occurred_at: datetime
    authority: SyntheticNotificationAuthority = SyntheticNotificationAuthority.ENGINEERING_ONLY
    classification: SyntheticNotificationClassification = (
        SyntheticNotificationClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticNotificationVerification = SyntheticNotificationVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.failure_id, _FAILURE_ID)
        _machine_value(self.notification_id, _NOTIFICATION_ID)
        _strict_enum(self.code, SyntheticFailureCode)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))


def _snapshot_failure(value: object) -> SyntheticNotificationFailure:
    if type(value) is not SyntheticNotificationFailure:
        raise _fail(NotificationDomainCode.INVALID_TYPE)
    try:
        return SyntheticNotificationFailure(
            failure_id=value.failure_id,
            notification_id=value.notification_id,
            code=value.code,
            occurred_at=value.occurred_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except NotificationDomainError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _fail(NotificationDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFailureReceipt:
    failure_id: str
    notification_id: str
    correlation_id: str
    intent_fingerprint: str = field(repr=False)
    template_id: str
    template_version: str
    template_artifact_hash: str = field(repr=False)
    code: SyntheticFailureCode
    recorded_at: datetime
    authority: SyntheticNotificationAuthority = SyntheticNotificationAuthority.ENGINEERING_ONLY
    classification: SyntheticNotificationClassification = (
        SyntheticNotificationClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticNotificationVerification = SyntheticNotificationVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.failure_id, _FAILURE_ID)
        _machine_value(self.notification_id, _NOTIFICATION_ID)
        _machine_value(self.correlation_id, _CORRELATION_ID)
        _machine_value(self.intent_fingerprint, _SHA256)
        _machine_value(self.template_id, _TEMPLATE_ID)
        _machine_value(self.template_version, _VERSION)
        _machine_value(self.template_artifact_hash, _SHA256)
        _strict_enum(self.code, SyntheticFailureCode)
        _fixed_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "recorded_at", _utc(self.recorded_at))


def _intent_fingerprint(intent: SyntheticNotificationIntent) -> str:
    parts = [
        intent.notification_id,
        intent.correlation_id,
        intent.template_id,
        intent.template_version,
        intent.template_artifact_hash,
        intent.created_at.isoformat(),
    ]
    parts.extend(f"{item.key}={item.value}" for item in intent.variables)
    return hashlib.sha256("|".join(parts).encode("ascii")).hexdigest()


def record_synthetic_failure(
    intent: SyntheticNotificationIntent,
    template: SyntheticNotificationTemplate,
    failure: SyntheticNotificationFailure,
) -> SyntheticFailureReceipt:
    """Validate an offline fixture and record only its simulated failure metadata."""

    notification = _snapshot_intent(intent)
    configured_template = _snapshot_template(template)
    simulated_failure = _snapshot_failure(failure)

    if simulated_failure.notification_id != notification.notification_id:
        raise _fail(NotificationDomainCode.IDENTITY_MISMATCH)
    if (
        notification.template_id != configured_template.template_id
        or notification.template_version != configured_template.template_version
        or notification.template_artifact_hash != configured_template.artifact_hash
    ):
        raise _fail(NotificationDomainCode.TEMPLATE_MISMATCH)
    variable_keys = tuple(item.key for item in notification.variables)
    if variable_keys != configured_template.allowed_variable_keys:
        raise _fail(NotificationDomainCode.TEMPLATE_MISMATCH)
    if configured_template.created_at > notification.created_at:
        raise _fail(NotificationDomainCode.INVALID_CHRONOLOGY)
    if notification.created_at > simulated_failure.occurred_at:
        raise _fail(NotificationDomainCode.INVALID_CHRONOLOGY)

    return SyntheticFailureReceipt(
        failure_id=simulated_failure.failure_id,
        notification_id=notification.notification_id,
        correlation_id=notification.correlation_id,
        intent_fingerprint=_intent_fingerprint(notification),
        template_id=configured_template.template_id,
        template_version=configured_template.template_version,
        template_artifact_hash=configured_template.artifact_hash,
        code=simulated_failure.code,
        recorded_at=simulated_failure.occurred_at,
    )


__all__ = [
    "NotificationDomainCode",
    "NotificationDomainError",
    "SafeSyntheticVariable",
    "SyntheticFailureCode",
    "SyntheticFailureReceipt",
    "SyntheticNotificationAuthority",
    "SyntheticNotificationClassification",
    "SyntheticNotificationFailure",
    "SyntheticNotificationIntent",
    "SyntheticNotificationTemplate",
    "SyntheticNotificationVerification",
    "record_synthetic_failure",
]
