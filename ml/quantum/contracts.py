"""Strict metadata-only contracts for the detached P19-A research boundary."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from ml.research.candidates import (
    SyntheticModelCandidate,
    SyntheticModelCard,
    synthetic_model_candidate_fingerprint,
    synthetic_model_card_fingerprint,
    validate_synthetic_model_candidate,
    validate_synthetic_model_card,
)
from ml.research.contracts import ResearchBoundaryError, ResearchEnvironment

_REQUEST_ID = re.compile(r"^syn_qml_request_[0-9]{4}$")
_BACKEND_ID = re.compile(r"^syn_qml_backend_no_quantum$")
_CANDIDATE_ID = re.compile(r"^syn_ml_candidate_[0-9]{4}$")
_CARD_ID = re.compile(r"^syn_ml_card_(?:alpha|beta|gamma|delta)$")
_MODEL_ID = re.compile(r"^syn_ml_model_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class QuantumBoundaryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    BACKEND_FAILURE = "BACKEND_FAILURE"


class QuantumBoundaryError(ValueError):
    """Stable content-free failure at the synthetic quantum boundary."""

    def __init__(self, code: QuantumBoundaryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: QuantumBoundaryCode) -> QuantumBoundaryError:
    return QuantumBoundaryError(code)


class QuantumBackendKind(StrEnum):
    DETERMINISTIC_NO_QUANTUM_FAKE = "DETERMINISTIC_NO_QUANTUM_FAKE"


class QuantumEncodingKind(StrEnum):
    METADATA_BINDING_ONLY = "METADATA_BINDING_ONLY"


class QuantumExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class QuantumApprovalState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


class QuantumClaimState(StrEnum):
    NO_COMPARATIVE_CLAIM = "NO_COMPARATIVE_CLAIM"


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(QuantumBoundaryCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        offset = value.utcoffset()
    except Exception:  # noqa: BLE001 - hostile tzinfo is a trust-boundary input
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None
    if offset is None:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        return value.astimezone(UTC)
    except Exception:  # noqa: BLE001 - hostile tzinfo is a trust-boundary input
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None


def validate_quantum_environment(environment: object) -> ResearchEnvironment:
    if type(environment) is not ResearchEnvironment:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    if environment not in {ResearchEnvironment.LOCAL, ResearchEnvironment.TEST}:
        raise _error(QuantumBoundaryCode.PROTECTED_ENVIRONMENT)
    return environment


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


def _request_evidence_fingerprint(
    *,
    request_id: str,
    request_version: str,
    candidate_id: str,
    candidate_version: str,
    candidate_fingerprint: str,
    card_id: str,
    card_version: str,
    card_fingerprint: str,
    model_id: str,
    model_version: str,
    model_fingerprint: str,
    dataset_fingerprint: str,
    split_fingerprint: str,
    preprocessing_fingerprint: str,
    encoding: QuantumEncodingKind,
    environment: ResearchEnvironment,
    requested_at: datetime,
    backend_kind: QuantumBackendKind,
    execution_state: QuantumExecutionState,
    approval_state: QuantumApprovalState,
    claim_state: QuantumClaimState,
) -> str:
    return _canonical_hash(
        (
            request_id,
            request_version,
            candidate_id,
            candidate_version,
            candidate_fingerprint,
            card_id,
            card_version,
            card_fingerprint,
            model_id,
            model_version,
            model_fingerprint,
            dataset_fingerprint,
            split_fingerprint,
            preprocessing_fingerprint,
            encoding.value,
            environment.value,
            requested_at.isoformat(),
            backend_kind.value,
            execution_state.value,
            approval_state.value,
            claim_state.value,
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticQuantumRequest:
    request_id: str
    request_version: str
    candidate_id: str
    candidate_version: str
    candidate_fingerprint: str
    card_id: str
    card_version: str
    card_fingerprint: str
    model_id: str
    model_version: str
    model_fingerprint: str
    dataset_fingerprint: str
    split_fingerprint: str
    preprocessing_fingerprint: str
    encoding: QuantumEncodingKind
    environment: ResearchEnvironment
    requested_at: datetime
    evidence_fingerprint: str
    backend_kind: QuantumBackendKind = QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE
    execution_state: QuantumExecutionState = QuantumExecutionState.NOT_EXECUTED
    approval_state: QuantumApprovalState = QuantumApprovalState.TEST_ONLY_UNAPPROVED
    claim_state: QuantumClaimState = QuantumClaimState.NO_COMPARATIVE_CLAIM

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_version, _VERSION)
        _machine_string(self.candidate_id, _CANDIDATE_ID)
        _machine_string(self.candidate_version, _VERSION)
        _machine_string(self.candidate_fingerprint, _SHA256)
        _machine_string(self.card_id, _CARD_ID)
        _machine_string(self.card_version, _VERSION)
        _machine_string(self.card_fingerprint, _SHA256)
        _machine_string(self.model_id, _MODEL_ID)
        _machine_string(self.model_version, _VERSION)
        _machine_string(self.model_fingerprint, _SHA256)
        _machine_string(self.dataset_fingerprint, _SHA256)
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        _strict_enum(self.encoding, QuantumEncodingKind)
        environment = validate_quantum_environment(self.environment)
        requested_at = _utc(self.requested_at)
        _machine_string(self.evidence_fingerprint, _SHA256)
        _strict_enum(self.backend_kind, QuantumBackendKind)
        _strict_enum(self.execution_state, QuantumExecutionState)
        _strict_enum(self.approval_state, QuantumApprovalState)
        _strict_enum(self.claim_state, QuantumClaimState)
        expected = _request_evidence_fingerprint(
            request_id=self.request_id,
            request_version=self.request_version,
            candidate_id=self.candidate_id,
            candidate_version=self.candidate_version,
            candidate_fingerprint=self.candidate_fingerprint,
            card_id=self.card_id,
            card_version=self.card_version,
            card_fingerprint=self.card_fingerprint,
            model_id=self.model_id,
            model_version=self.model_version,
            model_fingerprint=self.model_fingerprint,
            dataset_fingerprint=self.dataset_fingerprint,
            split_fingerprint=self.split_fingerprint,
            preprocessing_fingerprint=self.preprocessing_fingerprint,
            encoding=self.encoding,
            environment=environment,
            requested_at=requested_at,
            backend_kind=self.backend_kind,
            execution_state=self.execution_state,
            approval_state=self.approval_state,
            claim_state=self.claim_state,
        )
        if self.evidence_fingerprint != expected:
            raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
        object.__setattr__(self, "requested_at", requested_at)
        object.__setattr__(self, "environment", environment)


def validate_synthetic_quantum_request(value: object) -> SyntheticQuantumRequest:
    if type(value) is not SyntheticQuantumRequest:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticQuantumRequest(
            request_id=value.request_id,
            request_version=value.request_version,
            candidate_id=value.candidate_id,
            candidate_version=value.candidate_version,
            candidate_fingerprint=value.candidate_fingerprint,
            card_id=value.card_id,
            card_version=value.card_version,
            card_fingerprint=value.card_fingerprint,
            model_id=value.model_id,
            model_version=value.model_version,
            model_fingerprint=value.model_fingerprint,
            dataset_fingerprint=value.dataset_fingerprint,
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            encoding=value.encoding,
            environment=value.environment,
            requested_at=value.requested_at,
            evidence_fingerprint=value.evidence_fingerprint,
            backend_kind=value.backend_kind,
            execution_state=value.execution_state,
            approval_state=value.approval_state,
            claim_state=value.claim_state,
        )
    except QuantumBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None


def synthetic_quantum_request_fingerprint(value: SyntheticQuantumRequest) -> str:
    return validate_synthetic_quantum_request(value).evidence_fingerprint


def build_synthetic_quantum_request(
    *,
    request_id: str,
    request_version: str,
    candidate: SyntheticModelCandidate,
    card: SyntheticModelCard,
    encoding: QuantumEncodingKind,
    requested_at: datetime,
    environment: ResearchEnvironment,
) -> SyntheticQuantumRequest:
    validate_quantum_environment(environment)
    try:
        safe_candidate = validate_synthetic_model_candidate(candidate)
        safe_card = validate_synthetic_model_card(card)
    except ResearchBoundaryError:
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None
    _machine_string(request_id, _REQUEST_ID)
    _machine_string(request_version, _VERSION)
    _strict_enum(encoding, QuantumEncodingKind)
    normalized_time = _utc(requested_at)
    candidate_fingerprint = synthetic_model_candidate_fingerprint(safe_candidate)
    card_fingerprint = synthetic_model_card_fingerprint(safe_card)
    if (
        safe_candidate.card_id != safe_card.card_id
        or safe_candidate.card_version != safe_card.card_version
        or safe_candidate.card_fingerprint != card_fingerprint
        or safe_candidate.model_id != safe_card.model_id
        or safe_candidate.model_version != safe_card.model_version
        or safe_candidate.model_fingerprint != safe_card.model_fingerprint
    ):
        raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
    backend_kind = QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE
    execution_state = QuantumExecutionState.NOT_EXECUTED
    approval_state = QuantumApprovalState.TEST_ONLY_UNAPPROVED
    claim_state = QuantumClaimState.NO_COMPARATIVE_CLAIM
    evidence_fingerprint = _request_evidence_fingerprint(
        request_id=request_id,
        request_version=request_version,
        candidate_id=safe_candidate.candidate_id,
        candidate_version=safe_candidate.candidate_version,
        candidate_fingerprint=candidate_fingerprint,
        card_id=safe_card.card_id,
        card_version=safe_card.card_version,
        card_fingerprint=card_fingerprint,
        model_id=safe_card.model_id,
        model_version=safe_card.model_version,
        model_fingerprint=safe_card.model_fingerprint,
        dataset_fingerprint=safe_card.dataset_fingerprint,
        split_fingerprint=safe_card.split_fingerprint,
        preprocessing_fingerprint=safe_card.preprocessing_fingerprint,
        encoding=encoding,
        environment=environment,
        requested_at=normalized_time,
        backend_kind=backend_kind,
        execution_state=execution_state,
        approval_state=approval_state,
        claim_state=claim_state,
    )
    return SyntheticQuantumRequest(
        request_id=request_id,
        request_version=request_version,
        candidate_id=safe_candidate.candidate_id,
        candidate_version=safe_candidate.candidate_version,
        candidate_fingerprint=candidate_fingerprint,
        card_id=safe_card.card_id,
        card_version=safe_card.card_version,
        card_fingerprint=card_fingerprint,
        model_id=safe_card.model_id,
        model_version=safe_card.model_version,
        model_fingerprint=safe_card.model_fingerprint,
        dataset_fingerprint=safe_card.dataset_fingerprint,
        split_fingerprint=safe_card.split_fingerprint,
        preprocessing_fingerprint=safe_card.preprocessing_fingerprint,
        encoding=encoding,
        environment=environment,
        requested_at=normalized_time,
        evidence_fingerprint=evidence_fingerprint,
        backend_kind=backend_kind,
        execution_state=execution_state,
        approval_state=approval_state,
        claim_state=claim_state,
    )


def _receipt_evidence_fingerprint(
    *,
    backend_id: str,
    backend_version: str,
    request_id: str,
    request_version: str,
    request_fingerprint: str,
    recorded_at: datetime,
    backend_kind: QuantumBackendKind,
    execution_state: QuantumExecutionState,
    approval_state: QuantumApprovalState,
    claim_state: QuantumClaimState,
) -> str:
    return _canonical_hash(
        (
            backend_id,
            backend_version,
            request_id,
            request_version,
            request_fingerprint,
            recorded_at.isoformat(),
            backend_kind.value,
            execution_state.value,
            approval_state.value,
            claim_state.value,
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticQuantumReceipt:
    backend_id: str
    backend_version: str
    request_id: str
    request_version: str
    request_fingerprint: str
    recorded_at: datetime
    receipt_fingerprint: str
    backend_kind: QuantumBackendKind = QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE
    execution_state: QuantumExecutionState = QuantumExecutionState.NOT_EXECUTED
    approval_state: QuantumApprovalState = QuantumApprovalState.TEST_ONLY_UNAPPROVED
    claim_state: QuantumClaimState = QuantumClaimState.NO_COMPARATIVE_CLAIM

    def __post_init__(self) -> None:
        _machine_string(self.backend_id, _BACKEND_ID)
        _machine_string(self.backend_version, _VERSION)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_version, _VERSION)
        _machine_string(self.request_fingerprint, _SHA256)
        recorded_at = _utc(self.recorded_at)
        _machine_string(self.receipt_fingerprint, _SHA256)
        _strict_enum(self.backend_kind, QuantumBackendKind)
        _strict_enum(self.execution_state, QuantumExecutionState)
        _strict_enum(self.approval_state, QuantumApprovalState)
        _strict_enum(self.claim_state, QuantumClaimState)
        expected = _receipt_evidence_fingerprint(
            backend_id=self.backend_id,
            backend_version=self.backend_version,
            request_id=self.request_id,
            request_version=self.request_version,
            request_fingerprint=self.request_fingerprint,
            recorded_at=recorded_at,
            backend_kind=self.backend_kind,
            execution_state=self.execution_state,
            approval_state=self.approval_state,
            claim_state=self.claim_state,
        )
        if self.receipt_fingerprint != expected:
            raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
        object.__setattr__(self, "recorded_at", recorded_at)


def build_synthetic_quantum_receipt(
    *, request: SyntheticQuantumRequest, backend_id: str, backend_version: str
) -> SyntheticQuantumReceipt:
    safe_request = validate_synthetic_quantum_request(request)
    _machine_string(backend_id, _BACKEND_ID)
    _machine_string(backend_version, _VERSION)
    request_fingerprint = synthetic_quantum_request_fingerprint(safe_request)
    receipt_fingerprint = _receipt_evidence_fingerprint(
        backend_id=backend_id,
        backend_version=backend_version,
        request_id=safe_request.request_id,
        request_version=safe_request.request_version,
        request_fingerprint=request_fingerprint,
        recorded_at=safe_request.requested_at,
        backend_kind=safe_request.backend_kind,
        execution_state=safe_request.execution_state,
        approval_state=safe_request.approval_state,
        claim_state=safe_request.claim_state,
    )
    return SyntheticQuantumReceipt(
        backend_id=backend_id,
        backend_version=backend_version,
        request_id=safe_request.request_id,
        request_version=safe_request.request_version,
        request_fingerprint=request_fingerprint,
        recorded_at=safe_request.requested_at,
        receipt_fingerprint=receipt_fingerprint,
        backend_kind=safe_request.backend_kind,
        execution_state=safe_request.execution_state,
        approval_state=safe_request.approval_state,
        claim_state=safe_request.claim_state,
    )


def validate_synthetic_quantum_receipt(value: object) -> SyntheticQuantumReceipt:
    if type(value) is not SyntheticQuantumReceipt:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticQuantumReceipt(
            backend_id=value.backend_id,
            backend_version=value.backend_version,
            request_id=value.request_id,
            request_version=value.request_version,
            request_fingerprint=value.request_fingerprint,
            recorded_at=value.recorded_at,
            receipt_fingerprint=value.receipt_fingerprint,
            backend_kind=value.backend_kind,
            execution_state=value.execution_state,
            approval_state=value.approval_state,
            claim_state=value.claim_state,
        )
    except QuantumBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None


__all__ = [
    "QuantumApprovalState",
    "QuantumBackendKind",
    "QuantumBoundaryCode",
    "QuantumBoundaryError",
    "QuantumClaimState",
    "QuantumEncodingKind",
    "QuantumExecutionState",
    "SyntheticQuantumReceipt",
    "SyntheticQuantumRequest",
    "build_synthetic_quantum_receipt",
    "build_synthetic_quantum_request",
    "synthetic_quantum_request_fingerprint",
    "validate_quantum_environment",
    "validate_synthetic_quantum_receipt",
    "validate_synthetic_quantum_request",
]
