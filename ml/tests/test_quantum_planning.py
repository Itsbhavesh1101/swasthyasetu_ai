"""Adversarial tests for non-executable P19-B quantum experiment plans."""

from __future__ import annotations

import inspect
import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

from ml.quantum.contracts import (
    QuantumBoundaryCode,
    QuantumBoundaryError,
    SyntheticQuantumRequest,
    synthetic_quantum_request_fingerprint,
)
from ml.quantum.planning import (
    QuantumBackendSelection,
    QuantumCircuitDesignState,
    QuantumExperimentPlan,
    QuantumExperimentPurpose,
    QuantumFrameworkSelection,
    QuantumOptimizerSelection,
    QuantumPlanApprovalState,
    QuantumPlanExecutionState,
    QuantumShotSelection,
    SymbolicEncodingSelection,
    build_quantum_experiment_plan,
    quantum_experiment_plan_fingerprint,
    validate_quantum_experiment_plan,
)
from ml.research.contracts import ResearchEnvironment
from ml.tests.test_quantum_contracts import request

NOW = datetime(2026, 11, 2, 11, tzinfo=UTC)


def plan(**changes: object) -> QuantumExperimentPlan:
    values: dict[str, object] = {
        "plan_id": "syn_qml_plan_0001",
        "plan_version": "engineering.v1",
        "request": request(),
        "code_commit": "a" * 40,
        "dependency_lock_hash": "b" * 64,
        "configuration_hash": "c" * 64,
        "created_at": NOW,
        "environment": ResearchEnvironment.TEST,
    }
    values.update(changes)
    return build_quantum_experiment_plan(**values)  # type: ignore[arg-type]


class HostileRequest:
    def __getattribute__(self, name: str) -> object:
        raise RuntimeError("private-canary")


class QuantumExperimentPlanningTests(unittest.TestCase):
    def test_plan_binds_exact_request_and_build_metadata(self) -> None:
        source = request()

        value = plan(request=source)

        self.assertEqual(value.request_id, source.request_id)
        self.assertEqual(value.request_version, source.request_version)
        self.assertEqual(
            value.request_fingerprint,
            synthetic_quantum_request_fingerprint(source),
        )
        self.assertEqual(value.candidate_fingerprint, source.candidate_fingerprint)
        self.assertEqual(value.card_fingerprint, source.card_fingerprint)
        self.assertEqual(value.dataset_fingerprint, source.dataset_fingerprint)
        self.assertEqual(value.split_fingerprint, source.split_fingerprint)
        self.assertEqual(value.preprocessing_fingerprint, source.preprocessing_fingerprint)

    def test_all_experiment_choices_remain_explicitly_unselected(self) -> None:
        value = plan()

        self.assertIs(value.purpose, QuantumExperimentPurpose.ENGINEERING_PLAN_INTEGRITY_ONLY)
        self.assertIs(value.encoding, SymbolicEncodingSelection.NOT_SELECTED)
        self.assertIs(value.circuit, QuantumCircuitDesignState.NOT_DESIGNED)
        self.assertIs(value.optimizer, QuantumOptimizerSelection.NOT_SELECTED)
        self.assertIs(value.shots, QuantumShotSelection.NOT_SELECTED)
        self.assertIs(value.backend, QuantumBackendSelection.NO_BACKEND_SELECTED)
        self.assertIs(value.framework, QuantumFrameworkSelection.NOT_SELECTED)
        self.assertIs(value.execution_state, QuantumPlanExecutionState.NOT_EXECUTED)
        self.assertIs(value.approval_state, QuantumPlanApprovalState.TEST_ONLY_UNAPPROVED)

    def test_plan_is_immutable_and_fingerprint_is_deterministic(self) -> None:
        first = plan()
        second = plan()

        self.assertEqual(first, second)
        self.assertEqual(
            quantum_experiment_plan_fingerprint(first),
            quantum_experiment_plan_fingerprint(second),
        )
        with self.assertRaises(FrozenInstanceError):
            first.plan_id = "syn_qml_plan_0002"  # type: ignore[misc]

    def test_non_utc_time_is_normalized_and_naive_time_is_rejected(self) -> None:
        india = timezone(timedelta(hours=5, minutes=30))
        value = plan(created_at=datetime(2026, 11, 2, 16, 30, tzinfo=india))

        self.assertEqual(value.created_at, NOW)
        with self.assertRaises(QuantumBoundaryError) as error:
            plan(created_at=datetime(2026, 11, 2, 11))
        self.assertIs(error.exception.code, QuantumBoundaryCode.INVALID_TYPE)

    def test_plan_cannot_predate_bound_request(self) -> None:
        future_request = request(requested_at=NOW + timedelta(minutes=1))

        with self.assertRaises(QuantumBoundaryError) as error:
            plan(request=future_request)

        self.assertIs(error.exception.code, QuantumBoundaryCode.INVALID_VALUE)

    def test_protected_environment_denies_before_request_inspection(self) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            plan(
                request=HostileRequest(),
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.PROTECTED_ENVIRONMENT)
        self.assertNotIn("private-canary", str(error.exception))

    def test_safe_environment_replay_is_rejected(self) -> None:
        local_request = request(environment=ResearchEnvironment.LOCAL)

        with self.assertRaises(QuantumBoundaryError) as error:
            plan(request=local_request, environment=ResearchEnvironment.TEST)

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_direct_constructor_rejects_request_or_state_drift(self) -> None:
        value = plan()
        variants = (
            {"request_fingerprint": "f" * 64},
            {"candidate_fingerprint": "f" * 64},
            {"evidence_fingerprint": "f" * 64},
            {"encoding": "ANGLE"},
            {"circuit": "VQC"},
            {"backend": "SIMULATOR"},
            {"execution_state": "EXECUTED"},
            {"approval_state": "APPROVED"},
        )

        for changes in variants:
            with self.subTest(changes=changes), self.assertRaises(QuantumBoundaryError):
                replace(value, **changes)  # type: ignore[arg-type]

    def test_validator_reconstructs_and_rejects_forced_mutation(self) -> None:
        value = plan()
        object.__setattr__(value, "configuration_hash", "f" * 64)

        with self.assertRaises(QuantumBoundaryError) as error:
            validate_quantum_experiment_plan(value)

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_plan_exposes_no_runtime_or_result_payload(self) -> None:
        value = plan()
        forbidden_attributes = {
            "features",
            "labels",
            "parameters",
            "circuit_payload",
            "statevector",
            "probabilities",
            "predictions",
            "metric",
            "score",
            "runtime",
            "cost",
            "queue_time",
        }

        self.assertTrue(forbidden_attributes.isdisjoint(dir(value)))

    def test_plan_has_no_execution_promotion_or_claim_surface(self) -> None:
        forbidden_methods = {
            "execute",
            "run",
            "submit",
            "train",
            "infer",
            "predict",
            "compare",
            "promote",
            "approve",
            "claim_advantage",
        }

        self.assertTrue(forbidden_methods.isdisjoint(dir(QuantumExperimentPlan)))
        source = inspect.getsource(QuantumExperimentPlan).lower()
        self.assertNotIn("quantum advantage", source)

    def test_errors_do_not_echo_hostile_values(self) -> None:
        canary = "private-canary-sensitive-text"

        with self.assertRaises(QuantumBoundaryError) as error:
            plan(plan_id=canary)

        self.assertNotIn(canary, str(error.exception))

    def test_wrong_request_type_is_rejected(self) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            plan(request=object())

        self.assertIs(error.exception.code, QuantumBoundaryCode.INVALID_TYPE)

    def test_bound_request_snapshot_survives_caller_mutation(self) -> None:
        source: SyntheticQuantumRequest = request()
        value = plan(request=source)
        object.__setattr__(source, "request_id", "syn_qml_request_0002")

        self.assertEqual(value.request_id, "syn_qml_request_0001")


if __name__ == "__main__":
    unittest.main()
