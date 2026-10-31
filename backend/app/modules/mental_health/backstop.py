"""Detached synthetic backstop contracts with no lexicon or route authority."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.modules.mental_health.contracts import (
    MentalHealthContractError,
    SyntheticArtifactReference,
    SyntheticAuthority,
    SyntheticClassification,
    SyntheticSignalObservation,
    SyntheticVerification,
)

MAX_SYNTHETIC_EVIDENCE_TOKENS: Final = 4

_FIXTURE_SUFFIX = r"(?:alpha|beta|gamma|delta)"
_ARTIFACT_ID = re.compile(r"^syn_mh_backstop_fixture$")
_REQUEST_ID = re.compile(rf"^syn_mh_backstop_request_{_FIXTURE_SUFFIX}$")
_RESULT_ID = re.compile(rf"^syn_mh_backstop_result_{_FIXTURE_SUFFIX}$")
_FAILURE_ID = re.compile(rf"^syn_mh_backstop_failure_{_FIXTURE_SUFFIX}$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class BackstopContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_TOKEN = "DUPLICATE_TOKEN"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCONSISTENT_RESULT = "INCONSISTENT_RESULT"


class BackstopContractError(ValueError):
    """Stable content-free error for synthetic backstop mechanics."""

    def __init__(self, code: BackstopContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: BackstopContractCode) -> BackstopContractError:
    return BackstopContractError(code)


class SyntheticEvidenceToken(StrEnum):
    ALPHA = "SYN_MH_EVIDENCE_ALPHA"
    BETA = "SYN_MH_EVIDENCE_BETA"
    GAMMA = "SYN_MH_EVIDENCE_GAMMA"
    DELTA = "SYN_MH_EVIDENCE_DELTA"


class SyntheticBackstopOutcome(StrEnum):
    SYNTHETIC_MATCHED = "SYNTHETIC_MATCHED"
    SYNTHETIC_NO_MATCH = "SYNTHETIC_NO_MATCH"


class SyntheticBackstopFailureCode(StrEnum):
    SIMULATED_TIMEOUT = "SIMULATED_TIMEOUT"
    SIMULATED_UNAVAILABLE = "SIMULATED_UNAVAILABLE"
    SIMULATED_CANCELLED = "SIMULATED_CANCELLED"


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(BackstopContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(BackstopContractCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(BackstopContractCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(BackstopContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticAuthority)
    _strict_enum(classification, SyntheticClassification)
    _strict_enum(verification, SyntheticVerification)


def _input_artifact(value: object) -> SyntheticArtifactReference:
    if type(value) is not SyntheticArtifactReference:
        raise _error(BackstopContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticArtifactReference(
            artifact_id=value.artifact_id,
            artifact_version=value.artifact_version,
            content_hash=value.content_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except MentalHealthContractError:
        raise _error(BackstopContractCode.INVALID_VALUE) from None
    except (AttributeError, TypeError, ValueError):
        raise _error(BackstopContractCode.INVALID_TYPE) from None
    if not snapshot.artifact_id.startswith("syn_mh_input_fixture_"):
        raise _error(BackstopContractCode.INVALID_VALUE)
    return snapshot


def _signal(value: object) -> SyntheticSignalObservation:
    if type(value) is not SyntheticSignalObservation:
        raise _error(BackstopContractCode.INVALID_TYPE)
    try:
        return SyntheticSignalObservation(code=value.code, state=value.state)
    except MentalHealthContractError:
        raise _error(BackstopContractCode.INVALID_VALUE) from None
    except (AttributeError, TypeError, ValueError):
        raise _error(BackstopContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticBackstopArtifact:
    artifact_id: str
    artifact_version: str
    content_hash: str
    created_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.artifact_id, _ARTIFACT_ID)
        _machine_string(self.artifact_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "created_at", _utc(self.created_at))


def _backstop_artifact(value: object) -> SyntheticBackstopArtifact:
    if type(value) is not SyntheticBackstopArtifact:
        raise _error(BackstopContractCode.INVALID_TYPE)
    try:
        return SyntheticBackstopArtifact(
            artifact_id=value.artifact_id,
            artifact_version=value.artifact_version,
            content_hash=value.content_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except BackstopContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(BackstopContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticBackstopRequest:
    request_id: str
    input_artifact: SyntheticArtifactReference
    backstop_artifact: SyntheticBackstopArtifact
    evidence_tokens: tuple[SyntheticEvidenceToken, ...]
    created_at: datetime
    deadline_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        input_artifact = _input_artifact(self.input_artifact)
        backstop_artifact = _backstop_artifact(self.backstop_artifact)
        if type(self.evidence_tokens) is not tuple:
            raise _error(BackstopContractCode.INVALID_TYPE)
        if len(self.evidence_tokens) > MAX_SYNTHETIC_EVIDENCE_TOKENS:
            raise _error(BackstopContractCode.LIMIT_EXCEEDED)
        for token in self.evidence_tokens:
            _strict_enum(token, SyntheticEvidenceToken)
        token_values = tuple(token.value for token in self.evidence_tokens)
        if len(set(token_values)) != len(token_values):
            raise _error(BackstopContractCode.DUPLICATE_TOKEN)
        if token_values != tuple(sorted(token_values)):
            raise _error(BackstopContractCode.INVALID_VALUE)
        created_at = _utc(self.created_at)
        deadline_at = _utc(self.deadline_at)
        if input_artifact.created_at > created_at or backstop_artifact.created_at > created_at:
            raise _error(BackstopContractCode.INVALID_CHRONOLOGY)
        if deadline_at <= created_at:
            raise _error(BackstopContractCode.INVALID_CHRONOLOGY)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "input_artifact", input_artifact)
        object.__setattr__(self, "backstop_artifact", backstop_artifact)
        object.__setattr__(self, "evidence_tokens", tuple(self.evidence_tokens))
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "deadline_at", deadline_at)


def _request(value: object) -> SyntheticBackstopRequest:
    if type(value) is not SyntheticBackstopRequest:
        raise _error(BackstopContractCode.INVALID_TYPE)
    try:
        return SyntheticBackstopRequest(
            request_id=value.request_id,
            input_artifact=value.input_artifact,
            backstop_artifact=value.backstop_artifact,
            evidence_tokens=value.evidence_tokens,
            created_at=value.created_at,
            deadline_at=value.deadline_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except BackstopContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(BackstopContractCode.INVALID_TYPE) from None


def validate_synthetic_backstop_request(
    request: SyntheticBackstopRequest,
) -> SyntheticBackstopRequest:
    """Return a revalidated immutable snapshot before any backstop evaluation."""

    return _request(request)


def synthetic_backstop_request_fingerprint(request: SyntheticBackstopRequest) -> str:
    """Bind every content-free request field without retaining evidence outside the request."""

    snapshot = _request(request)
    fields = (
        snapshot.request_id,
        snapshot.input_artifact.artifact_id,
        snapshot.input_artifact.artifact_version,
        snapshot.input_artifact.content_hash,
        snapshot.backstop_artifact.artifact_id,
        snapshot.backstop_artifact.artifact_version,
        snapshot.backstop_artifact.content_hash,
        *(token.value for token in snapshot.evidence_tokens),
        snapshot.created_at.isoformat(),
        snapshot.deadline_at.isoformat(),
        snapshot.authority.value,
        snapshot.classification.value,
        snapshot.verification.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticBackstopResult:
    result_id: str
    request_id: str
    request_fingerprint: str
    input_artifact_id: str
    input_artifact_version: str
    input_artifact_hash: str
    backstop_artifact_id: str
    backstop_artifact_version: str
    backstop_artifact_hash: str
    outcome: SyntheticBackstopOutcome
    signals: tuple[SyntheticSignalObservation, ...]
    completed_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.result_id, _RESULT_ID)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _machine_string(
            self.input_artifact_id, re.compile(r"^syn_mh_input_fixture_(?:alpha|beta|gamma|delta)$")
        )
        _machine_string(self.input_artifact_version, _VERSION)
        _machine_string(self.input_artifact_hash, _SHA256)
        _machine_string(self.backstop_artifact_id, _ARTIFACT_ID)
        _machine_string(self.backstop_artifact_version, _VERSION)
        _machine_string(self.backstop_artifact_hash, _SHA256)
        _strict_enum(self.outcome, SyntheticBackstopOutcome)
        if type(self.signals) is not tuple or len(self.signals) > MAX_SYNTHETIC_EVIDENCE_TOKENS:
            raise _error(BackstopContractCode.LIMIT_EXCEEDED)
        signals = tuple(_signal(item) for item in self.signals)
        codes = tuple(item.code.value for item in signals)
        if len(set(codes)) != len(codes):
            raise _error(BackstopContractCode.DUPLICATE_TOKEN)
        if codes != tuple(sorted(codes)):
            raise _error(BackstopContractCode.INVALID_VALUE)
        if self.outcome is SyntheticBackstopOutcome.SYNTHETIC_MATCHED and not signals:
            raise _error(BackstopContractCode.INCONSISTENT_RESULT)
        if self.outcome is SyntheticBackstopOutcome.SYNTHETIC_NO_MATCH and signals:
            raise _error(BackstopContractCode.INCONSISTENT_RESULT)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "signals", signals)
        object.__setattr__(self, "completed_at", _utc(self.completed_at))


def _result(value: object) -> SyntheticBackstopResult:
    if type(value) is not SyntheticBackstopResult:
        raise _error(BackstopContractCode.INVALID_TYPE)
    try:
        return SyntheticBackstopResult(
            result_id=value.result_id,
            request_id=value.request_id,
            request_fingerprint=value.request_fingerprint,
            input_artifact_id=value.input_artifact_id,
            input_artifact_version=value.input_artifact_version,
            input_artifact_hash=value.input_artifact_hash,
            backstop_artifact_id=value.backstop_artifact_id,
            backstop_artifact_version=value.backstop_artifact_version,
            backstop_artifact_hash=value.backstop_artifact_hash,
            outcome=value.outcome,
            signals=value.signals,
            completed_at=value.completed_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except BackstopContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(BackstopContractCode.INVALID_TYPE) from None


def validate_synthetic_backstop_result(
    request: SyntheticBackstopRequest,
    result: SyntheticBackstopResult,
) -> SyntheticBackstopResult:
    """Revalidate and bind a synthetic backstop result to its exact request."""

    backstop_request = _request(request)
    backstop_result = _result(result)
    if (
        backstop_result.request_id != backstop_request.request_id
        or backstop_result.request_fingerprint
        != synthetic_backstop_request_fingerprint(backstop_request)
        or backstop_result.input_artifact_id != backstop_request.input_artifact.artifact_id
        or backstop_result.input_artifact_version
        != backstop_request.input_artifact.artifact_version
        or backstop_result.input_artifact_hash != backstop_request.input_artifact.content_hash
        or backstop_result.backstop_artifact_id != backstop_request.backstop_artifact.artifact_id
        or backstop_result.backstop_artifact_version
        != backstop_request.backstop_artifact.artifact_version
        or backstop_result.backstop_artifact_hash != backstop_request.backstop_artifact.content_hash
    ):
        raise _error(BackstopContractCode.IDENTITY_MISMATCH)
    if (
        not backstop_request.created_at
        <= backstop_result.completed_at
        < backstop_request.deadline_at
    ):
        raise _error(BackstopContractCode.INVALID_CHRONOLOGY)
    return backstop_result


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticBackstopFailure:
    failure_id: str
    request_id: str
    request_fingerprint: str
    code: SyntheticBackstopFailureCode
    occurred_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.failure_id, _FAILURE_ID)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _strict_enum(self.code, SyntheticBackstopFailureCode)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))

    def validate_for(self, request: SyntheticBackstopRequest) -> SyntheticBackstopFailure:
        backstop_request = _request(request)
        validated = SyntheticBackstopFailure(
            failure_id=self.failure_id,
            request_id=self.request_id,
            request_fingerprint=self.request_fingerprint,
            code=self.code,
            occurred_at=self.occurred_at,
            authority=self.authority,
            classification=self.classification,
            verification=self.verification,
        )
        if (
            validated.request_id != backstop_request.request_id
            or validated.request_fingerprint
            != synthetic_backstop_request_fingerprint(backstop_request)
        ):
            raise _error(BackstopContractCode.IDENTITY_MISMATCH)
        if validated.code is SyntheticBackstopFailureCode.SIMULATED_TIMEOUT:
            if validated.occurred_at < backstop_request.deadline_at:
                raise _error(BackstopContractCode.INVALID_CHRONOLOGY)
        elif (
            not backstop_request.created_at <= validated.occurred_at < backstop_request.deadline_at
        ):
            raise _error(BackstopContractCode.INVALID_CHRONOLOGY)
        return validated


SyntheticBackstopResponse = SyntheticBackstopResult | SyntheticBackstopFailure


__all__ = [
    "BackstopContractCode",
    "BackstopContractError",
    "SyntheticBackstopArtifact",
    "SyntheticBackstopFailure",
    "SyntheticBackstopFailureCode",
    "SyntheticBackstopOutcome",
    "SyntheticBackstopRequest",
    "SyntheticBackstopResponse",
    "SyntheticBackstopResult",
    "SyntheticEvidenceToken",
    "validate_synthetic_backstop_request",
    "validate_synthetic_backstop_result",
    "synthetic_backstop_request_fingerprint",
]
