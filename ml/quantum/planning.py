"""Immutable, non-executable P19-B synthetic experiment planning contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from ml.quantum.contracts import (
    QuantumBoundaryCode,
    QuantumBoundaryError,
    QuantumClaimState,
    SyntheticQuantumRequest,
    synthetic_quantum_request_fingerprint,
    validate_quantum_environment,
    validate_synthetic_quantum_request,
)
from ml.research.contracts import ResearchAuthority, ResearchEnvironment

_PLAN_ID = re.compile(r"^syn_qml_plan_[0-9]{4}$")
_REQUEST_ID = re.compile(r"^syn_qml_request_[0-9]{4}$")
_CANDIDATE_ID = re.compile(r"^syn_ml_candidate_[0-9]{4}$")
_CARD_ID = re.compile(r"^syn_ml_card_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")


def _error(code: QuantumBoundaryCode) -> QuantumBoundaryError:
    return QuantumBoundaryError(code)


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


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class QuantumExperimentPurpose(StrEnum):
    ENGINEERING_PLAN_INTEGRITY_ONLY = "ENGINEERING_PLAN_INTEGRITY_ONLY"


class SymbolicEncodingSelection(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"


class QuantumCircuitDesignState(StrEnum):
    NOT_DESIGNED = "NOT_DESIGNED"


class QuantumOptimizerSelection(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"


class QuantumShotSelection(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"


class QuantumBackendSelection(StrEnum):
    NO_BACKEND_SELECTED = "NO_BACKEND_SELECTED"


class QuantumFrameworkSelection(StrEnum):
    NOT_SELECTED = "NOT_SELECTED"


class QuantumPlanExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class QuantumPlanApprovalState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


def _plan_evidence_fingerprint(
    *,
    plan_id: str,
    plan_version: str,
    request_id: str,
    request_version: str,
    request_fingerprint: str,
    candidate_id: str,
    candidate_version: str,
    candidate_fingerprint: str,
    card_id: str,
    card_version: str,
    card_fingerprint: str,
    dataset_fingerprint: str,
    split_fingerprint: str,
    preprocessing_fingerprint: str,
    code_commit: str,
    dependency_lock_hash: str,
    configuration_hash: str,
    purpose: QuantumExperimentPurpose,
    encoding: SymbolicEncodingSelection,
    circuit: QuantumCircuitDesignState,
    optimizer: QuantumOptimizerSelection,
    shots: QuantumShotSelection,
    backend: QuantumBackendSelection,
    framework: QuantumFrameworkSelection,
    execution_state: QuantumPlanExecutionState,
    approval_state: QuantumPlanApprovalState,
    claim_state: QuantumClaimState,
    environment: ResearchEnvironment,
    authority: ResearchAuthority,
    created_at: datetime,
) -> str:
    return _canonical_hash(
        (
            plan_id,
            plan_version,
            request_id,
            request_version,
            request_fingerprint,
            candidate_id,
            candidate_version,
            candidate_fingerprint,
            card_id,
            card_version,
            card_fingerprint,
            dataset_fingerprint,
            split_fingerprint,
            preprocessing_fingerprint,
            code_commit,
            dependency_lock_hash,
            configuration_hash,
            purpose.value,
            encoding.value,
            circuit.value,
            optimizer.value,
            shots.value,
            backend.value,
            framework.value,
            execution_state.value,
            approval_state.value,
            claim_state.value,
            environment.value,
            authority.value,
            created_at.isoformat(),
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class QuantumExperimentPlan:
    plan_id: str
    plan_version: str
    request_id: str
    request_version: str
    request_fingerprint: str
    candidate_id: str
    candidate_version: str
    candidate_fingerprint: str
    card_id: str
    card_version: str
    card_fingerprint: str
    dataset_fingerprint: str
    split_fingerprint: str
    preprocessing_fingerprint: str
    code_commit: str
    dependency_lock_hash: str
    configuration_hash: str
    created_at: datetime
    environment: ResearchEnvironment
    evidence_fingerprint: str
    purpose: QuantumExperimentPurpose = QuantumExperimentPurpose.ENGINEERING_PLAN_INTEGRITY_ONLY
    encoding: SymbolicEncodingSelection = SymbolicEncodingSelection.NOT_SELECTED
    circuit: QuantumCircuitDesignState = QuantumCircuitDesignState.NOT_DESIGNED
    optimizer: QuantumOptimizerSelection = QuantumOptimizerSelection.NOT_SELECTED
    shots: QuantumShotSelection = QuantumShotSelection.NOT_SELECTED
    backend: QuantumBackendSelection = QuantumBackendSelection.NO_BACKEND_SELECTED
    framework: QuantumFrameworkSelection = QuantumFrameworkSelection.NOT_SELECTED
    execution_state: QuantumPlanExecutionState = QuantumPlanExecutionState.NOT_EXECUTED
    approval_state: QuantumPlanApprovalState = QuantumPlanApprovalState.TEST_ONLY_UNAPPROVED
    claim_state: QuantumClaimState = QuantumClaimState.NO_COMPARATIVE_CLAIM
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.plan_id, _PLAN_ID)
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_version, _VERSION)
        _machine_string(self.request_fingerprint, _SHA256)
        _machine_string(self.candidate_id, _CANDIDATE_ID)
        _machine_string(self.candidate_version, _VERSION)
        _machine_string(self.candidate_fingerprint, _SHA256)
        _machine_string(self.card_id, _CARD_ID)
        _machine_string(self.card_version, _VERSION)
        _machine_string(self.card_fingerprint, _SHA256)
        _machine_string(self.dataset_fingerprint, _SHA256)
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        _machine_string(self.code_commit, _GIT_SHA)
        _machine_string(self.dependency_lock_hash, _SHA256)
        _machine_string(self.configuration_hash, _SHA256)
        created_at = _utc(self.created_at)
        environment = validate_quantum_environment(self.environment)
        _machine_string(self.evidence_fingerprint, _SHA256)
        _strict_enum(self.purpose, QuantumExperimentPurpose)
        _strict_enum(self.encoding, SymbolicEncodingSelection)
        _strict_enum(self.circuit, QuantumCircuitDesignState)
        _strict_enum(self.optimizer, QuantumOptimizerSelection)
        _strict_enum(self.shots, QuantumShotSelection)
        _strict_enum(self.backend, QuantumBackendSelection)
        _strict_enum(self.framework, QuantumFrameworkSelection)
        _strict_enum(self.execution_state, QuantumPlanExecutionState)
        _strict_enum(self.approval_state, QuantumPlanApprovalState)
        _strict_enum(self.claim_state, QuantumClaimState)
        _strict_enum(self.authority, ResearchAuthority)
        expected = _plan_evidence_fingerprint(
            plan_id=self.plan_id,
            plan_version=self.plan_version,
            request_id=self.request_id,
            request_version=self.request_version,
            request_fingerprint=self.request_fingerprint,
            candidate_id=self.candidate_id,
            candidate_version=self.candidate_version,
            candidate_fingerprint=self.candidate_fingerprint,
            card_id=self.card_id,
            card_version=self.card_version,
            card_fingerprint=self.card_fingerprint,
            dataset_fingerprint=self.dataset_fingerprint,
            split_fingerprint=self.split_fingerprint,
            preprocessing_fingerprint=self.preprocessing_fingerprint,
            code_commit=self.code_commit,
            dependency_lock_hash=self.dependency_lock_hash,
            configuration_hash=self.configuration_hash,
            purpose=self.purpose,
            encoding=self.encoding,
            circuit=self.circuit,
            optimizer=self.optimizer,
            shots=self.shots,
            backend=self.backend,
            framework=self.framework,
            execution_state=self.execution_state,
            approval_state=self.approval_state,
            claim_state=self.claim_state,
            environment=environment,
            authority=self.authority,
            created_at=created_at,
        )
        if self.evidence_fingerprint != expected:
            raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "environment", environment)


def validate_quantum_experiment_plan(value: object) -> QuantumExperimentPlan:
    if type(value) is not QuantumExperimentPlan:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        return QuantumExperimentPlan(
            plan_id=value.plan_id,
            plan_version=value.plan_version,
            request_id=value.request_id,
            request_version=value.request_version,
            request_fingerprint=value.request_fingerprint,
            candidate_id=value.candidate_id,
            candidate_version=value.candidate_version,
            candidate_fingerprint=value.candidate_fingerprint,
            card_id=value.card_id,
            card_version=value.card_version,
            card_fingerprint=value.card_fingerprint,
            dataset_fingerprint=value.dataset_fingerprint,
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            code_commit=value.code_commit,
            dependency_lock_hash=value.dependency_lock_hash,
            configuration_hash=value.configuration_hash,
            created_at=value.created_at,
            environment=value.environment,
            evidence_fingerprint=value.evidence_fingerprint,
            purpose=value.purpose,
            encoding=value.encoding,
            circuit=value.circuit,
            optimizer=value.optimizer,
            shots=value.shots,
            backend=value.backend,
            framework=value.framework,
            execution_state=value.execution_state,
            approval_state=value.approval_state,
            claim_state=value.claim_state,
            authority=value.authority,
        )
    except QuantumBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None


def quantum_experiment_plan_fingerprint(value: QuantumExperimentPlan) -> str:
    return validate_quantum_experiment_plan(value).evidence_fingerprint


def build_quantum_experiment_plan(
    *,
    plan_id: str,
    plan_version: str,
    request: SyntheticQuantumRequest,
    code_commit: str,
    dependency_lock_hash: str,
    configuration_hash: str,
    created_at: datetime,
    environment: ResearchEnvironment,
) -> QuantumExperimentPlan:
    validate_quantum_environment(environment)
    safe_request = validate_synthetic_quantum_request(request)
    _machine_string(plan_id, _PLAN_ID)
    _machine_string(plan_version, _VERSION)
    _machine_string(code_commit, _GIT_SHA)
    _machine_string(dependency_lock_hash, _SHA256)
    _machine_string(configuration_hash, _SHA256)
    normalized_time = _utc(created_at)
    if safe_request.environment is not environment:
        raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
    if normalized_time < safe_request.requested_at:
        raise _error(QuantumBoundaryCode.INVALID_VALUE)
    purpose = QuantumExperimentPurpose.ENGINEERING_PLAN_INTEGRITY_ONLY
    encoding = SymbolicEncodingSelection.NOT_SELECTED
    circuit = QuantumCircuitDesignState.NOT_DESIGNED
    optimizer = QuantumOptimizerSelection.NOT_SELECTED
    shots = QuantumShotSelection.NOT_SELECTED
    backend = QuantumBackendSelection.NO_BACKEND_SELECTED
    framework = QuantumFrameworkSelection.NOT_SELECTED
    execution_state = QuantumPlanExecutionState.NOT_EXECUTED
    approval_state = QuantumPlanApprovalState.TEST_ONLY_UNAPPROVED
    claim_state = QuantumClaimState.NO_COMPARATIVE_CLAIM
    authority = ResearchAuthority.ENGINEERING_ONLY
    request_fingerprint = synthetic_quantum_request_fingerprint(safe_request)
    evidence_fingerprint = _plan_evidence_fingerprint(
        plan_id=plan_id,
        plan_version=plan_version,
        request_id=safe_request.request_id,
        request_version=safe_request.request_version,
        request_fingerprint=request_fingerprint,
        candidate_id=safe_request.candidate_id,
        candidate_version=safe_request.candidate_version,
        candidate_fingerprint=safe_request.candidate_fingerprint,
        card_id=safe_request.card_id,
        card_version=safe_request.card_version,
        card_fingerprint=safe_request.card_fingerprint,
        dataset_fingerprint=safe_request.dataset_fingerprint,
        split_fingerprint=safe_request.split_fingerprint,
        preprocessing_fingerprint=safe_request.preprocessing_fingerprint,
        code_commit=code_commit,
        dependency_lock_hash=dependency_lock_hash,
        configuration_hash=configuration_hash,
        purpose=purpose,
        encoding=encoding,
        circuit=circuit,
        optimizer=optimizer,
        shots=shots,
        backend=backend,
        framework=framework,
        execution_state=execution_state,
        approval_state=approval_state,
        claim_state=claim_state,
        environment=environment,
        authority=authority,
        created_at=normalized_time,
    )
    return QuantumExperimentPlan(
        plan_id=plan_id,
        plan_version=plan_version,
        request_id=safe_request.request_id,
        request_version=safe_request.request_version,
        request_fingerprint=request_fingerprint,
        candidate_id=safe_request.candidate_id,
        candidate_version=safe_request.candidate_version,
        candidate_fingerprint=safe_request.candidate_fingerprint,
        card_id=safe_request.card_id,
        card_version=safe_request.card_version,
        card_fingerprint=safe_request.card_fingerprint,
        dataset_fingerprint=safe_request.dataset_fingerprint,
        split_fingerprint=safe_request.split_fingerprint,
        preprocessing_fingerprint=safe_request.preprocessing_fingerprint,
        code_commit=code_commit,
        dependency_lock_hash=dependency_lock_hash,
        configuration_hash=configuration_hash,
        created_at=normalized_time,
        environment=environment,
        evidence_fingerprint=evidence_fingerprint,
        purpose=purpose,
        encoding=encoding,
        circuit=circuit,
        optimizer=optimizer,
        shots=shots,
        backend=backend,
        framework=framework,
        execution_state=execution_state,
        approval_state=approval_state,
        claim_state=claim_state,
        authority=authority,
    )


__all__ = [
    "QuantumBackendSelection",
    "QuantumCircuitDesignState",
    "QuantumExperimentPlan",
    "QuantumExperimentPurpose",
    "QuantumFrameworkSelection",
    "QuantumOptimizerSelection",
    "QuantumPlanApprovalState",
    "QuantumPlanExecutionState",
    "QuantumShotSelection",
    "SymbolicEncodingSelection",
    "build_quantum_experiment_plan",
    "quantum_experiment_plan_fingerprint",
    "validate_quantum_experiment_plan",
]
