"""Offline no-quantum demonstration of the synthetic P19 boundaries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from ml.quantum.contracts import (
    QuantumApprovalState,
    QuantumBackendKind,
    QuantumBoundaryCode,
    QuantumBoundaryError,
    QuantumClaimState,
    QuantumEncodingKind,
    QuantumExecutionState,
    build_synthetic_quantum_request,
    synthetic_quantum_request_fingerprint,
    validate_quantum_environment,
)
from ml.quantum.gateway import validate_quantum_contract
from ml.quantum.planning import (
    QuantumBackendSelection,
    QuantumCircuitDesignState,
    QuantumFrameworkSelection,
    QuantumOptimizerSelection,
    QuantumPlanApprovalState,
    QuantumPlanExecutionState,
    QuantumShotSelection,
    SymbolicEncodingSelection,
    build_quantum_experiment_plan,
    quantum_experiment_plan_fingerprint,
)
from ml.quantum.testing import DeterministicNoQuantumBackend
from ml.research.contracts import ResearchAuthority, ResearchEnvironment
from ml.research.demo import _build_synthetic_classical_demo_bundle

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_CANDIDATE_ID = re.compile(r"^syn_ml_candidate_[0-9]{4}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_REQUESTED_AT = datetime(2026, 11, 3, 11, 0, tzinfo=UTC)
_PLANNED_AT = datetime(2026, 11, 3, 11, 1, tzinfo=UTC)


def _error(code: QuantumBoundaryCode) -> QuantumBoundaryError:
    return QuantumBoundaryError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(QuantumBoundaryCode.INVALID_VALUE)
    return value


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class SyntheticQuantumDemoActivationState(StrEnum):
    NOT_ACTIVATED = "NOT_ACTIVATED"


def _evidence_fingerprint(values: tuple[object, ...]) -> str:
    return _canonical_hash(
        tuple(value.value if isinstance(value, StrEnum) else str(value) for value in values)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticQuantumDemoReceipt:
    demo_version: str
    environment: ResearchEnvironment
    authority: ResearchAuthority
    candidate_id: str
    candidate_version: str
    candidate_fingerprint: str
    card_fingerprint: str
    dataset_fingerprint: str
    split_fingerprint: str
    preprocessing_fingerprint: str
    request_encoding: QuantumEncodingKind
    backend_kind: QuantumBackendKind
    gateway_execution_state: QuantumExecutionState
    gateway_approval_state: QuantumApprovalState
    gateway_claim_state: QuantumClaimState
    plan_encoding: SymbolicEncodingSelection
    plan_circuit: QuantumCircuitDesignState
    plan_optimizer: QuantumOptimizerSelection
    plan_shots: QuantumShotSelection
    plan_backend: QuantumBackendSelection
    plan_framework: QuantumFrameworkSelection
    plan_execution_state: QuantumPlanExecutionState
    plan_approval_state: QuantumPlanApprovalState
    plan_claim_state: QuantumClaimState
    activation_state: SyntheticQuantumDemoActivationState
    request_fingerprint: str
    backend_receipt_fingerprint: str
    plan_fingerprint: str
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        _machine_string(self.demo_version, _VERSION)
        validate_quantum_environment(self.environment)
        for value, expected in (
            (self.authority, ResearchAuthority),
            (self.request_encoding, QuantumEncodingKind),
            (self.backend_kind, QuantumBackendKind),
            (self.gateway_execution_state, QuantumExecutionState),
            (self.gateway_approval_state, QuantumApprovalState),
            (self.gateway_claim_state, QuantumClaimState),
            (self.plan_encoding, SymbolicEncodingSelection),
            (self.plan_circuit, QuantumCircuitDesignState),
            (self.plan_optimizer, QuantumOptimizerSelection),
            (self.plan_shots, QuantumShotSelection),
            (self.plan_backend, QuantumBackendSelection),
            (self.plan_framework, QuantumFrameworkSelection),
            (self.plan_execution_state, QuantumPlanExecutionState),
            (self.plan_approval_state, QuantumPlanApprovalState),
            (self.plan_claim_state, QuantumClaimState),
            (self.activation_state, SyntheticQuantumDemoActivationState),
        ):
            _strict_enum(value, expected)
        _machine_string(self.candidate_id, _CANDIDATE_ID)
        _machine_string(self.candidate_version, _VERSION)
        for fingerprint in (
            self.candidate_fingerprint,
            self.card_fingerprint,
            self.dataset_fingerprint,
            self.split_fingerprint,
            self.preprocessing_fingerprint,
            self.request_fingerprint,
            self.backend_receipt_fingerprint,
            self.plan_fingerprint,
            self.evidence_fingerprint,
        ):
            _machine_string(fingerprint, _SHA256)
        if (
            self.authority is not ResearchAuthority.ENGINEERING_ONLY
            or self.request_encoding is not QuantumEncodingKind.METADATA_BINDING_ONLY
            or self.backend_kind is not QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE
            or self.gateway_execution_state is not QuantumExecutionState.NOT_EXECUTED
            or self.gateway_approval_state is not QuantumApprovalState.TEST_ONLY_UNAPPROVED
            or self.gateway_claim_state is not QuantumClaimState.NO_COMPARATIVE_CLAIM
            or self.plan_encoding is not SymbolicEncodingSelection.NOT_SELECTED
            or self.plan_circuit is not QuantumCircuitDesignState.NOT_DESIGNED
            or self.plan_optimizer is not QuantumOptimizerSelection.NOT_SELECTED
            or self.plan_shots is not QuantumShotSelection.NOT_SELECTED
            or self.plan_backend is not QuantumBackendSelection.NO_BACKEND_SELECTED
            or self.plan_framework is not QuantumFrameworkSelection.NOT_SELECTED
            or self.plan_execution_state is not QuantumPlanExecutionState.NOT_EXECUTED
            or self.plan_approval_state is not QuantumPlanApprovalState.TEST_ONLY_UNAPPROVED
            or self.plan_claim_state is not QuantumClaimState.NO_COMPARATIVE_CLAIM
            or self.activation_state is not SyntheticQuantumDemoActivationState.NOT_ACTIVATED
        ):
            raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)
        expected_evidence = _evidence_fingerprint(
            tuple(
                getattr(self, field)
                for field in self.__dataclass_fields__
                if field != "evidence_fingerprint"
            )
        )
        if self.evidence_fingerprint != expected_evidence:
            raise _error(QuantumBoundaryCode.IDENTITY_MISMATCH)


def validate_synthetic_quantum_demo_receipt(value: object) -> SyntheticQuantumDemoReceipt:
    if type(value) is not SyntheticQuantumDemoReceipt:
        raise _error(QuantumBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticQuantumDemoReceipt(
            **{field: getattr(value, field) for field in value.__dataclass_fields__}
        )
    except QuantumBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(QuantumBoundaryCode.INVALID_TYPE) from None


def run_synthetic_quantum_demo(
    environment: ResearchEnvironment,
) -> SyntheticQuantumDemoReceipt:
    """Validate and plan metadata without quantum execution or comparison."""

    safe_environment = validate_quantum_environment(environment)
    classical = _build_synthetic_classical_demo_bundle(safe_environment)
    request = build_synthetic_quantum_request(
        request_id="syn_qml_request_0001",
        request_version="engineering.v1",
        candidate=classical.candidate,
        card=classical.card,
        encoding=QuantumEncodingKind.METADATA_BINDING_ONLY,
        requested_at=_REQUESTED_AT,
        environment=safe_environment,
    )
    gateway_receipt = validate_quantum_contract(
        backend=DeterministicNoQuantumBackend(),
        request=request,
        environment=safe_environment,
    )
    plan = build_quantum_experiment_plan(
        plan_id="syn_qml_plan_0001",
        plan_version="engineering.v1",
        request=request,
        code_commit="a" * 40,
        dependency_lock_hash="b" * 64,
        configuration_hash="c" * 64,
        created_at=_PLANNED_AT,
        environment=safe_environment,
    )
    fields: dict[str, object] = {
        "demo_version": "engineering.v1",
        "environment": safe_environment,
        "authority": plan.authority,
        "candidate_id": request.candidate_id,
        "candidate_version": request.candidate_version,
        "candidate_fingerprint": request.candidate_fingerprint,
        "card_fingerprint": request.card_fingerprint,
        "dataset_fingerprint": request.dataset_fingerprint,
        "split_fingerprint": request.split_fingerprint,
        "preprocessing_fingerprint": request.preprocessing_fingerprint,
        "request_encoding": request.encoding,
        "backend_kind": gateway_receipt.backend_kind,
        "gateway_execution_state": gateway_receipt.execution_state,
        "gateway_approval_state": gateway_receipt.approval_state,
        "gateway_claim_state": gateway_receipt.claim_state,
        "plan_encoding": plan.encoding,
        "plan_circuit": plan.circuit,
        "plan_optimizer": plan.optimizer,
        "plan_shots": plan.shots,
        "plan_backend": plan.backend,
        "plan_framework": plan.framework,
        "plan_execution_state": plan.execution_state,
        "plan_approval_state": plan.approval_state,
        "plan_claim_state": plan.claim_state,
        "activation_state": SyntheticQuantumDemoActivationState.NOT_ACTIVATED,
        "request_fingerprint": synthetic_quantum_request_fingerprint(request),
        "backend_receipt_fingerprint": gateway_receipt.receipt_fingerprint,
        "plan_fingerprint": quantum_experiment_plan_fingerprint(plan),
    }
    return SyntheticQuantumDemoReceipt(
        **fields,  # type: ignore[arg-type]
        evidence_fingerprint=_evidence_fingerprint(tuple(fields.values())),
    )


__all__ = [
    "SyntheticQuantumDemoActivationState",
    "SyntheticQuantumDemoReceipt",
    "run_synthetic_quantum_demo",
    "validate_synthetic_quantum_demo_receipt",
]
