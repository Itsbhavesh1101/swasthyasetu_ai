"""Opaque engineering-only contracts for an inactive ABDM adapter boundary."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from app.config.settings import Environment

_REQUEST_ID = re.compile(r"^syn_abdm_request_(?:alpha|beta|gamma|delta)$")
_ARTIFACT_ID = re.compile(r"^syn_abdm_artifact_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class ABDMBoundaryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ABDMBoundaryError(ValueError):
    """Stable content-free failure for the inactive synthetic boundary."""

    def __init__(self, code: ABDMBoundaryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: ABDMBoundaryCode) -> ABDMBoundaryError:
    return ABDMBoundaryError(code)


class ABDMIntegrationMode(StrEnum):
    DISABLED = "DISABLED"
    SYNTHETIC_OFFLINE_MOCK = "SYNTHETIC_OFFLINE_MOCK"


class SyntheticABDMOperation(StrEnum):
    ALPHA = "SYNTHETIC_OPERATION_ALPHA"
    BETA = "SYNTHETIC_OPERATION_BETA"


class SyntheticABDMBoundaryAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticABDMBoundaryVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticABDMResultState(StrEnum):
    SYNTHETIC_ACCEPTED = "SYNTHETIC_ACCEPTED"
    SYNTHETIC_REJECTED = "SYNTHETIC_REJECTED"
    SYNTHETIC_UNAVAILABLE = "SYNTHETIC_UNAVAILABLE"


class SyntheticABDMIssue(StrEnum):
    SYNTHETIC_REJECTED = "SYNTHETIC_REJECTED"
    SYNTHETIC_UNAVAILABLE = "SYNTHETIC_UNAVAILABLE"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ABDMBoundaryCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticABDMArtifactReference:
    artifact_id: str
    artifact_version: str
    content_hash: str
    authority: SyntheticABDMBoundaryAuthority = SyntheticABDMBoundaryAuthority.ENGINEERING_ONLY
    verification: SyntheticABDMBoundaryVerification = SyntheticABDMBoundaryVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.artifact_id, _ARTIFACT_ID)
        _machine_string(self.artifact_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)
        _strict_enum(self.authority, SyntheticABDMBoundaryAuthority)
        _strict_enum(self.verification, SyntheticABDMBoundaryVerification)


def _artifact(value: object) -> SyntheticABDMArtifactReference:
    if type(value) is not SyntheticABDMArtifactReference:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticABDMArtifactReference(
            artifact_id=value.artifact_id,
            artifact_version=value.artifact_version,
            content_hash=value.content_hash,
            authority=value.authority,
            verification=value.verification,
        )
    except ABDMBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ABDMBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticABDMRequest:
    request_id: str
    mode: ABDMIntegrationMode
    operation: SyntheticABDMOperation
    artifact: SyntheticABDMArtifactReference
    idempotency_key: str
    created_at: datetime
    authority: SyntheticABDMBoundaryAuthority = SyntheticABDMBoundaryAuthority.ENGINEERING_ONLY
    verification: SyntheticABDMBoundaryVerification = SyntheticABDMBoundaryVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _strict_enum(self.mode, ABDMIntegrationMode)
        if self.mode is not ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK:
            raise _error(ABDMBoundaryCode.INVALID_VALUE)
        _strict_enum(self.operation, SyntheticABDMOperation)
        artifact = _artifact(self.artifact)
        _machine_string(self.idempotency_key, _SHA256)
        created_at = _utc(self.created_at)
        _strict_enum(self.authority, SyntheticABDMBoundaryAuthority)
        _strict_enum(self.verification, SyntheticABDMBoundaryVerification)
        object.__setattr__(self, "artifact", artifact)
        object.__setattr__(self, "created_at", created_at)


def validate_synthetic_abdm_request(value: object) -> SyntheticABDMRequest:
    if type(value) is not SyntheticABDMRequest:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticABDMRequest(
            request_id=value.request_id,
            mode=value.mode,
            operation=value.operation,
            artifact=value.artifact,
            idempotency_key=value.idempotency_key,
            created_at=value.created_at,
            authority=value.authority,
            verification=value.verification,
        )
    except ABDMBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ABDMBoundaryCode.INVALID_TYPE) from None


def synthetic_abdm_request_fingerprint(request: SyntheticABDMRequest) -> str:
    snapshot = validate_synthetic_abdm_request(request)
    fields = (
        snapshot.request_id,
        snapshot.mode.value,
        snapshot.operation.value,
        snapshot.artifact.artifact_id,
        snapshot.artifact.artifact_version,
        snapshot.artifact.content_hash,
        snapshot.idempotency_key,
        snapshot.created_at.isoformat(),
        snapshot.authority.value,
        snapshot.verification.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticABDMResult:
    request_id: str
    operation: SyntheticABDMOperation
    request_fingerprint: str
    state: SyntheticABDMResultState
    issues: tuple[SyntheticABDMIssue, ...]
    completed_at: datetime
    authority: SyntheticABDMBoundaryAuthority = SyntheticABDMBoundaryAuthority.ENGINEERING_ONLY
    verification: SyntheticABDMBoundaryVerification = SyntheticABDMBoundaryVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _strict_enum(self.operation, SyntheticABDMOperation)
        _machine_string(self.request_fingerprint, _SHA256)
        _strict_enum(self.state, SyntheticABDMResultState)
        if type(self.issues) is not tuple:
            raise _error(ABDMBoundaryCode.INVALID_TYPE)
        for issue in self.issues:
            _strict_enum(issue, SyntheticABDMIssue)
        values = tuple(issue.value for issue in self.issues)
        if len(set(values)) != len(values) or values != tuple(sorted(values)):
            raise _error(ABDMBoundaryCode.INVALID_VALUE)
        expected_issues = {
            SyntheticABDMResultState.SYNTHETIC_ACCEPTED: (),
            SyntheticABDMResultState.SYNTHETIC_REJECTED: (SyntheticABDMIssue.SYNTHETIC_REJECTED,),
            SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE: (
                SyntheticABDMIssue.SYNTHETIC_UNAVAILABLE,
            ),
        }
        if self.issues != expected_issues[self.state]:
            raise _error(ABDMBoundaryCode.INVALID_VALUE)
        completed_at = _utc(self.completed_at)
        _strict_enum(self.authority, SyntheticABDMBoundaryAuthority)
        _strict_enum(self.verification, SyntheticABDMBoundaryVerification)
        object.__setattr__(self, "issues", tuple(self.issues))
        object.__setattr__(self, "completed_at", completed_at)


@runtime_checkable
class ABDMAdapterPort(Protocol):
    """Opaque port with no official ABDM operation or payload semantics."""

    def execute(self, request: SyntheticABDMRequest) -> SyntheticABDMResult: ...


def validate_synthetic_abdm_environment(
    *,
    mode: ABDMIntegrationMode,
    environment: Environment,
) -> None:
    if type(environment) is not Environment or type(mode) is not ABDMIntegrationMode:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    if mode is ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK and environment not in {
        Environment.LOCAL,
        Environment.TEST,
    }:
        raise _error(ABDMBoundaryCode.PROTECTED_ENVIRONMENT)


def validate_synthetic_abdm_result(
    *, request: SyntheticABDMRequest, result: SyntheticABDMResult
) -> SyntheticABDMResult:
    request_snapshot = validate_synthetic_abdm_request(request)
    if type(result) is not SyntheticABDMResult:
        raise _error(ABDMBoundaryCode.INVALID_TYPE)
    recreated = SyntheticABDMResult(
        request_id=result.request_id,
        operation=result.operation,
        request_fingerprint=result.request_fingerprint,
        state=result.state,
        issues=result.issues,
        completed_at=result.completed_at,
        authority=result.authority,
        verification=result.verification,
    )
    if (
        recreated.request_id != request_snapshot.request_id
        or recreated.operation is not request_snapshot.operation
        or recreated.request_fingerprint != synthetic_abdm_request_fingerprint(request_snapshot)
        or recreated.completed_at < request_snapshot.created_at
    ):
        raise _error(ABDMBoundaryCode.IDENTITY_MISMATCH)
    return recreated


__all__ = [
    "ABDMAdapterPort",
    "ABDMBoundaryCode",
    "ABDMBoundaryError",
    "ABDMIntegrationMode",
    "SyntheticABDMArtifactReference",
    "SyntheticABDMBoundaryAuthority",
    "SyntheticABDMBoundaryVerification",
    "SyntheticABDMIssue",
    "SyntheticABDMOperation",
    "SyntheticABDMRequest",
    "SyntheticABDMResult",
    "SyntheticABDMResultState",
    "synthetic_abdm_request_fingerprint",
    "validate_synthetic_abdm_environment",
    "validate_synthetic_abdm_request",
    "validate_synthetic_abdm_result",
]
