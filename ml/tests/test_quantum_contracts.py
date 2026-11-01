"""Adversarial tests for the detached P19-A synthetic backend boundary."""

from __future__ import annotations

import inspect
import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

from ml.quantum.contracts import (
    QuantumApprovalState,
    QuantumBackendKind,
    QuantumBoundaryCode,
    QuantumBoundaryError,
    QuantumClaimState,
    QuantumEncodingKind,
    QuantumExecutionState,
    SyntheticQuantumRequest,
    build_synthetic_quantum_request,
    synthetic_quantum_request_fingerprint,
    validate_synthetic_quantum_request,
)
from ml.research.contracts import ResearchEnvironment
from ml.tests.test_candidates import build_candidate, build_card

NOW = datetime(2026, 11, 2, 9, tzinfo=UTC)


def request(**changes: object) -> SyntheticQuantumRequest:
    values: dict[str, object] = {
        "request_id": "syn_qml_request_0001",
        "request_version": "engineering.v1",
        "candidate": build_candidate(),
        "card": build_card(),
        "encoding": QuantumEncodingKind.METADATA_BINDING_ONLY,
        "requested_at": NOW,
        "environment": ResearchEnvironment.TEST,
    }
    values.update(changes)
    return build_synthetic_quantum_request(**values)  # type: ignore[arg-type]


class SyntheticQuantumRequestTests(unittest.TestCase):
    def test_request_binds_exact_p18_candidate_and_card_without_payload(self) -> None:
        candidate = build_candidate()
        card = build_card()

        value = request(candidate=candidate, card=card)

        self.assertEqual(value.candidate_id, candidate.candidate_id)
        self.assertEqual(value.candidate_version, candidate.candidate_version)
        self.assertEqual(value.card_id, card.card_id)
        self.assertEqual(value.card_version, card.card_version)
        self.assertEqual(value.dataset_fingerprint, card.dataset_fingerprint)
        self.assertEqual(value.split_fingerprint, card.split_fingerprint)
        self.assertEqual(value.preprocessing_fingerprint, card.preprocessing_fingerprint)
        self.assertIs(value.environment, ResearchEnvironment.TEST)
        self.assertFalse(hasattr(value, "features"))
        self.assertFalse(hasattr(value, "labels"))
        self.assertFalse(hasattr(value, "circuit"))
        self.assertFalse(hasattr(value, "patient"))

    def test_request_is_immutable_and_fingerprint_is_deterministic(self) -> None:
        first = request()
        second = request()

        self.assertEqual(first, second)
        self.assertEqual(
            synthetic_quantum_request_fingerprint(first),
            synthetic_quantum_request_fingerprint(second),
        )
        with self.assertRaises(FrozenInstanceError):
            first.request_id = "syn_qml_request_0002"  # type: ignore[misc]

    def test_request_is_explicitly_unapproved_and_not_executed(self) -> None:
        value = request()

        self.assertIs(value.backend_kind, QuantumBackendKind.DETERMINISTIC_NO_QUANTUM_FAKE)
        self.assertIs(value.execution_state, QuantumExecutionState.NOT_EXECUTED)
        self.assertIs(value.approval_state, QuantumApprovalState.TEST_ONLY_UNAPPROVED)
        self.assertIs(value.claim_state, QuantumClaimState.NO_COMPARATIVE_CLAIM)

    def test_candidate_and_card_mismatch_is_rejected(self) -> None:
        candidate = build_candidate()
        other_card = build_card(card_id="syn_ml_card_beta")

        with self.assertRaises(QuantumBoundaryError) as error:
            request(candidate=candidate, card=other_card)

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environment_rejects_before_candidate_inspection(self) -> None:
        class HostileCandidate:
            def __getattribute__(self, name: str) -> object:
                raise RuntimeError("private-canary")

        with self.assertRaises(QuantumBoundaryError) as error:
            request(
                candidate=HostileCandidate(),
                card=HostileCandidate(),
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.PROTECTED_ENVIRONMENT)
        self.assertNotIn("private-canary", str(error.exception))

    def test_direct_constructor_rejects_environment_drift(self) -> None:
        value = request()

        with self.assertRaises(QuantumBoundaryError) as error:
            replace(value, environment=ResearchEnvironment.LOCAL)

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_non_utc_time_is_normalized_and_naive_time_is_rejected(self) -> None:
        india = timezone(timedelta(hours=5, minutes=30))
        value = request(requested_at=datetime(2026, 11, 2, 14, 30, tzinfo=india))

        self.assertEqual(value.requested_at, NOW)
        with self.assertRaises(QuantumBoundaryError) as error:
            request(requested_at=datetime(2026, 11, 2, 9))
        self.assertIs(error.exception.code, QuantumBoundaryCode.INVALID_TYPE)

    def test_direct_constructor_rejects_evidence_or_state_drift(self) -> None:
        value = request()
        variants = (
            {"candidate_fingerprint": "f" * 64},
            {"evidence_fingerprint": "f" * 64},
            {"execution_state": "EXECUTED"},
            {"claim_state": "QUANTUM_ADVANTAGE"},
        )

        for changes in variants:
            with self.subTest(changes=changes), self.assertRaises(QuantumBoundaryError):
                replace(value, **changes)  # type: ignore[arg-type]

    def test_validator_reconstructs_and_rejects_forced_mutation(self) -> None:
        value = request()
        object.__setattr__(value, "split_fingerprint", "f" * 64)

        with self.assertRaises(QuantumBoundaryError) as error:
            validate_synthetic_quantum_request(value)

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_errors_are_content_free(self) -> None:
        canary = "private-canary-sensitive-text"

        with self.assertRaises(QuantumBoundaryError) as error:
            request(request_id=canary)

        self.assertNotIn(canary, str(error.exception))

    def test_contract_surface_has_no_execution_or_claim_methods(self) -> None:
        forbidden = {
            "execute",
            "run",
            "train",
            "infer",
            "predict",
            "promote",
            "approve",
            "claim_advantage",
        }

        self.assertTrue(forbidden.isdisjoint(dir(SyntheticQuantumRequest)))
        source = inspect.getsource(SyntheticQuantumRequest).lower()
        self.assertNotIn("quantum advantage", source)


if __name__ == "__main__":
    unittest.main()
