"""Content-free contracts for a detached synthetic admin authorization preflight."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

SYNTHETIC_ADMIN_CONTRACT_VERSION: Final = "synthetic-admin-authorization.v1"
MAX_SYNTHETIC_GRANTS: Final = 16

_REQUEST_ID = re.compile(r"^syn_admin_request_(?:alpha|beta|gamma|delta)$")
_GRANT_ID = re.compile(r"^syn_admin_grant_(?:alpha|beta|gamma|delta)$")
_ACTOR_ID = re.compile(r"^syn_admin_actor_(?:alpha|beta|gamma|delta)$")
_OBJECT_ID = re.compile(r"^syn_admin_object_(?:alpha|beta|gamma|delta)$")
_INSTITUTION_ID = re.compile(r"^syn_admin_institution_(?:alpha|beta|gamma|delta)$")
_SOURCE_ID = re.compile(r"^syn_admin_source_(?:alpha|beta|gamma|delta)$")
_PURPOSE_ID = re.compile(r"^syn_admin_purpose_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class AdminContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    DUPLICATE_GRANT = "DUPLICATE_GRANT"
    AMBIGUOUS_GRANT = "AMBIGUOUS_GRANT"
    INCONSISTENT_DECISION = "INCONSISTENT_DECISION"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class AdminContractError(ValueError):
    """Stable content-free synthetic admin contract failure."""

    def __init__(self, code: AdminContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class AdminAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class AdminClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class AdminVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticAdminAction(StrEnum):
    SYNTHETIC_ACTION_ALPHA = "SYNTHETIC_ACTION_ALPHA"
    SYNTHETIC_ACTION_BETA = "SYNTHETIC_ACTION_BETA"
    SYNTHETIC_ACTION_GAMMA = "SYNTHETIC_ACTION_GAMMA"


class AdminDecisionDisposition(StrEnum):
    MATCHED_SYNTHETIC_CONTRACT = "MATCHED_SYNTHETIC_CONTRACT"
    ABSTAINED = "ABSTAINED"


class AdminDecisionReason(StrEnum):
    EXACT_SYNTHETIC_MATCH = "EXACT_SYNTHETIC_MATCH"
    MFA_NOT_VERIFIED = "MFA_NOT_VERIFIED"
    NO_EXACT_ACTIVE_GRANT = "NO_EXACT_ACTIVE_GRANT"


def _error(code: AdminContractCode) -> AdminContractError:
    return AdminContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(AdminContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(AdminContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(AdminContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(AdminContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(authority: object, classification: object, verification: object) -> None:
    _strict_enum(authority, AdminAuthority)
    _strict_enum(classification, AdminClassification)
    _strict_enum(verification, AdminVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAdminRequest:
    request_id: str
    actor_id: str
    action: SyntheticAdminAction
    object_id: str
    object_version: str
    object_hash: str
    institution_id: str
    source_id: str
    purpose_id: str
    mfa_verified: bool
    created_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.actor_id, _ACTOR_ID)
        _strict_enum(self.action, SyntheticAdminAction)
        _machine_string(self.object_id, _OBJECT_ID)
        _machine_string(self.object_version, _VERSION)
        _machine_string(self.object_hash, _SHA256)
        _machine_string(self.institution_id, _INSTITUTION_ID)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.purpose_id, _PURPOSE_ID)
        if type(self.mfa_verified) is not bool:
            raise _error(AdminContractCode.INVALID_TYPE)
        created_at = _utc(self.created_at)
        _authority(self.authority, self.classification, self.verification)
        payload = {
            "action": self.action.value,
            "actor_id": self.actor_id,
            "contract_version": SYNTHETIC_ADMIN_CONTRACT_VERSION,
            "created_at": created_at.isoformat(),
            "institution_id": self.institution_id,
            "mfa_verified": self.mfa_verified,
            "object_hash": self.object_hash,
            "object_id": self.object_id,
            "object_version": self.object_version,
            "purpose_id": self.purpose_id,
            "request_id": self.request_id,
            "source_id": self.source_id,
        }
        fingerprint = sha256(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAdminGrant:
    grant_id: str
    actor_id: str
    action: SyntheticAdminAction
    object_id: str
    object_version: str
    object_hash: str
    institution_id: str
    source_id: str
    purpose_id: str
    valid_from: datetime
    expires_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.grant_id, _GRANT_ID)
        _machine_string(self.actor_id, _ACTOR_ID)
        _strict_enum(self.action, SyntheticAdminAction)
        _machine_string(self.object_id, _OBJECT_ID)
        _machine_string(self.object_version, _VERSION)
        _machine_string(self.object_hash, _SHA256)
        _machine_string(self.institution_id, _INSTITUTION_ID)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.purpose_id, _PURPOSE_ID)
        valid_from = _utc(self.valid_from)
        expires_at = _utc(self.expires_at)
        if valid_from >= expires_at:
            raise _error(AdminContractCode.INVALID_CHRONOLOGY)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "valid_from", valid_from)
        object.__setattr__(self, "expires_at", expires_at)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAdminDecision:
    request_id: str
    request_fingerprint: str
    disposition: AdminDecisionDisposition
    reason: AdminDecisionReason
    matched_grant_id: str | None
    evaluated_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_ADMIN_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _strict_enum(self.disposition, AdminDecisionDisposition)
        _strict_enum(self.reason, AdminDecisionReason)
        evaluated_at = _utc(self.evaluated_at)
        if self.disposition is AdminDecisionDisposition.MATCHED_SYNTHETIC_CONTRACT:
            consistent = (
                self.reason is AdminDecisionReason.EXACT_SYNTHETIC_MATCH
                and self.matched_grant_id is not None
            )
        else:
            consistent = (
                self.reason
                in {
                    AdminDecisionReason.MFA_NOT_VERIFIED,
                    AdminDecisionReason.NO_EXACT_ACTIVE_GRANT,
                }
                and self.matched_grant_id is None
            )
        if not consistent:
            raise _error(AdminContractCode.INCONSISTENT_DECISION)
        if self.matched_grant_id is not None:
            _machine_string(self.matched_grant_id, _GRANT_ID)
        _authority(self.authority, self.classification, self.verification)
        if (
            type(self.contract_version) is not str
            or self.contract_version != SYNTHETIC_ADMIN_CONTRACT_VERSION
        ):
            raise _error(AdminContractCode.INVALID_VALUE)
        object.__setattr__(self, "evaluated_at", evaluated_at)


def snapshot_admin_request(value: object) -> SyntheticAdminRequest:
    if type(value) is not SyntheticAdminRequest:
        raise _error(AdminContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticAdminRequest(
            request_id=value.request_id,
            actor_id=value.actor_id,
            action=value.action,
            object_id=value.object_id,
            object_version=value.object_version,
            object_hash=value.object_hash,
            institution_id=value.institution_id,
            source_id=value.source_id,
            purpose_id=value.purpose_id,
            mfa_verified=value.mfa_verified,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except AdminContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AdminContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(AdminContractCode.SNAPSHOT_DRIFT)
    return snapshot


def snapshot_admin_grant(value: object) -> SyntheticAdminGrant:
    if type(value) is not SyntheticAdminGrant:
        raise _error(AdminContractCode.INVALID_TYPE)
    try:
        return SyntheticAdminGrant(
            grant_id=value.grant_id,
            actor_id=value.actor_id,
            action=value.action,
            object_id=value.object_id,
            object_version=value.object_version,
            object_hash=value.object_hash,
            institution_id=value.institution_id,
            source_id=value.source_id,
            purpose_id=value.purpose_id,
            valid_from=value.valid_from,
            expires_at=value.expires_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except AdminContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AdminContractCode.INVALID_TYPE) from None


__all__ = [
    "MAX_SYNTHETIC_GRANTS",
    "SYNTHETIC_ADMIN_CONTRACT_VERSION",
    "AdminAuthority",
    "AdminClassification",
    "AdminContractCode",
    "AdminContractError",
    "AdminDecisionDisposition",
    "AdminDecisionReason",
    "AdminVerification",
    "SyntheticAdminAction",
    "SyntheticAdminDecision",
    "SyntheticAdminGrant",
    "SyntheticAdminRequest",
    "snapshot_admin_grant",
    "snapshot_admin_request",
]
