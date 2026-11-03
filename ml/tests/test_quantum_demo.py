"""Tests for the offline synthetic quantum-planning demonstration."""

from __future__ import annotations

import unittest
from dataclasses import asdict, replace

from ml.quantum.contracts import (
    QuantumApprovalState,
    QuantumBackendKind,
    QuantumBoundaryCode,
    QuantumBoundaryError,
    QuantumClaimState,
    QuantumEncodingKind,
    QuantumExecutionState,
)
from ml.quantum.demo import (
    SyntheticQuantumDemoActivationState,
    run_synthetic_quantum_demo,
    validate_synthetic_quantum_demo_receipt,
)
from ml.quantum.planning import (
    QuantumBackendSelection,
    QuantumCircuitDesignState,
    QuantumFrameworkSelection,
    QuantumOptimizerSelection,
    QuantumPlanApprovalState,
    QuantumPlanExecutionState,
    QuantumShotSelection,
    SymbolicEncodingSelection,
)
from ml.research.contracts import ResearchAuthority, ResearchEnvironment


class SyntheticQuantumDemoTests(unittest.TestCase):
    def test_replay_is_deterministic_and_exactly_bound_to_p18_evidence(self) -> None:
        first = run_synthetic_quantum_demo(ResearchEnvironment.TEST)
        second = run_synthetic_quantum_demo(ResearchEnvironment.TEST)

        self.assertEqual(first, second)
        self.assertIs(first.environment, ResearchEnvironment.TEST)
        self.assertIs(first.authority, ResearchAuthority.ENGINEERING_ONLY)
        self.assertEqual(first.candidate_id, "syn_ml_candidate_0001")
        self.assertEqual(first.candidate_version, "engineering.v1")
        for fingerprint in (
            first.candidate_fingerprint,
            first.card_fingerprint,
            first.dataset_fingerprint,
            first.split_fingerprint,
            first.preprocessing_fingerprint,
            first.request_fingerprint,
            first.backend_receipt_fingerprint,
            first.plan_fingerprint,
            first.evidence_fingerprint,
        ):
            self.assertRegex(fingerprint, r"^[a-f0-9]{64}$")

    def test_replay_preserves_no_quantum_and_non_executable_states(self) -> None:
        receipt = run_synthetic_quantum_demo(ResearchEnvironment.LOCAL)

        self.assertIs(receipt.request_encoding, QuantumEncodingKind.METADATA_BINDING_ONLY)
        self.assertIs(receipt.backend_kind, QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE)
        self.assertIs(receipt.gateway_execution_state, QuantumExecutionState.NOT_EXECUTED)
        self.assertIs(receipt.gateway_approval_state, QuantumApprovalState.TEST_ONLY_UNAPPROVED)
        self.assertIs(receipt.gateway_claim_state, QuantumClaimState.NO_COMPARATIVE_CLAIM)
        self.assertIs(receipt.plan_encoding, SymbolicEncodingSelection.NOT_SELECTED)
        self.assertIs(receipt.plan_circuit, QuantumCircuitDesignState.NOT_DESIGNED)
        self.assertIs(receipt.plan_optimizer, QuantumOptimizerSelection.NOT_SELECTED)
        self.assertIs(receipt.plan_shots, QuantumShotSelection.NOT_SELECTED)
        self.assertIs(receipt.plan_backend, QuantumBackendSelection.NO_BACKEND_SELECTED)
        self.assertIs(receipt.plan_framework, QuantumFrameworkSelection.NOT_SELECTED)
        self.assertIs(receipt.plan_execution_state, QuantumPlanExecutionState.NOT_EXECUTED)
        self.assertIs(receipt.plan_approval_state, QuantumPlanApprovalState.TEST_ONLY_UNAPPROVED)
        self.assertIs(receipt.activation_state, SyntheticQuantumDemoActivationState.NOT_ACTIVATED)

    def test_receipt_is_content_free_and_rejects_forgery(self) -> None:
        receipt = run_synthetic_quantum_demo(ResearchEnvironment.TEST)
        serialized = repr(asdict(receipt)).lower()
        for forbidden in (
            "feature_values",
            "labels",
            "circuit_payload",
            "statevector",
            "probabilities",
            "prediction",
            "patient",
        ):
            self.assertNotIn(forbidden, serialized)

        with self.assertRaises(QuantumBoundaryError) as state_error:
            replace(receipt, plan_execution_state="EXECUTED")  # type: ignore[arg-type]
        self.assertIs(state_error.exception.code, QuantumBoundaryCode.INVALID_TYPE)

        object.__setattr__(receipt, "request_fingerprint", "f" * 64)
        with self.assertRaises(QuantumBoundaryError) as mutation_error:
            validate_synthetic_quantum_demo_receipt(receipt)
        self.assertIs(mutation_error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environments_fail_closed(self) -> None:
        for environment in (
            ResearchEnvironment.STAGING,
            ResearchEnvironment.PILOT,
            ResearchEnvironment.PRODUCTION,
        ):
            with self.assertRaises(QuantumBoundaryError) as error:
                run_synthetic_quantum_demo(environment)
            self.assertIs(error.exception.code, QuantumBoundaryCode.PROTECTED_ENVIRONMENT)


if __name__ == "__main__":
    unittest.main()
