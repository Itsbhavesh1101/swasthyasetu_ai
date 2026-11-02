"""Tests for the offline synthetic classical-ML demonstration."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import asdict, replace
from pathlib import Path

from ml.research.candidates import (
    SyntheticCandidateStatus,
    SyntheticCardMetric,
    SyntheticCardPurpose,
    SyntheticCardState,
)
from ml.research.contracts import (
    DatasetAdmissionState,
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    SyntheticDataClassification,
)
from ml.research.demo import (
    SyntheticDemoActivationState,
    SyntheticDemoClaimState,
    SyntheticDemoRuntimeState,
    run_synthetic_classical_demo,
    validate_synthetic_classical_demo_receipt,
)
from ml.research.pipeline import (
    MissingValuePolicy,
    ScalingPolicy,
    SyntheticEvaluationState,
)

ROOT = Path(__file__).resolve().parents[2]


class SyntheticClassicalDemoTests(unittest.TestCase):
    def test_replay_is_deterministic_and_preserves_unapproved_states(self) -> None:
        first = run_synthetic_classical_demo(ResearchEnvironment.TEST)
        second = run_synthetic_classical_demo(ResearchEnvironment.TEST)

        self.assertEqual(first, second)
        self.assertEqual(first.demo_version, "engineering.v1")
        self.assertIs(first.environment, ResearchEnvironment.TEST)
        self.assertIs(first.authority, ResearchAuthority.ENGINEERING_ONLY)
        self.assertIs(
            first.data_classification,
            SyntheticDataClassification.SYNTHETIC_NON_MEDICAL,
        )
        self.assertIs(first.dataset_admission_state, DatasetAdmissionState.TEST_ONLY_UNAPPROVED)
        self.assertIs(first.evaluation_state, SyntheticEvaluationState.TEST_ONLY_UNAPPROVED)
        self.assertIs(first.card_state, SyntheticCardState.TEST_ONLY_UNAPPROVED)
        self.assertIs(first.candidate_status, SyntheticCandidateStatus.TEST_ONLY_UNAPPROVED)
        self.assertIs(first.card_purpose, SyntheticCardPurpose.ENGINEERING_DETERMINISM_ONLY)
        self.assertIs(first.card_metric, SyntheticCardMetric.EXACT_MATCH_COUNTS_ONLY)
        self.assertIs(
            first.claim_state,
            SyntheticDemoClaimState.NO_PERFORMANCE_OR_CLINICAL_CLAIM,
        )
        self.assertIs(first.runtime_state, SyntheticDemoRuntimeState.OFFLINE_NO_EGRESS)
        self.assertIs(first.activation_state, SyntheticDemoActivationState.NOT_ACTIVATED)

    def test_replay_uses_train_only_preprocessing_and_exact_test_counts(self) -> None:
        receipt = run_synthetic_classical_demo(ResearchEnvironment.LOCAL)

        self.assertIs(receipt.missing_value_policy, MissingValuePolicy.TRAIN_MEAN)
        self.assertIs(receipt.scaling_policy, ScalingPolicy.STANDARD_SCORE)
        self.assertGreater(receipt.train_count, 0)
        self.assertGreater(receipt.validation_count, 0)
        self.assertGreater(receipt.test_count, 0)
        self.assertEqual(
            receipt.train_count + receipt.validation_count + receipt.test_count,
            12,
        )
        self.assertEqual(receipt.evaluated_count, receipt.test_count)
        self.assertEqual(
            receipt.correct_count + receipt.error_count,
            receipt.evaluated_count,
        )

    def test_replay_resolves_exact_candidate_and_binds_provenance(self) -> None:
        receipt = run_synthetic_classical_demo(ResearchEnvironment.TEST)

        self.assertEqual(receipt.candidate_id, "syn_ml_candidate_0001")
        self.assertEqual(receipt.candidate_version, "engineering.v1")
        for fingerprint in (
            receipt.dataset_fingerprint,
            receipt.split_fingerprint,
            receipt.preprocessing_fingerprint,
            receipt.model_fingerprint,
            receipt.evaluation_fingerprint,
            receipt.card_fingerprint,
            receipt.candidate_fingerprint,
            receipt.evidence_fingerprint,
        ):
            with self.subTest(fingerprint=fingerprint):
                self.assertRegex(fingerprint, r"^[a-f0-9]{64}$")

    def test_receipt_exposes_no_rows_labels_feature_values_or_patient_data(self) -> None:
        serialized = repr(asdict(run_synthetic_classical_demo(ResearchEnvironment.TEST))).lower()

        for forbidden in ("row_id", "group_id", "feature_values", "expected_labels", "patient"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, serialized)

    def test_direct_constructor_and_validator_reject_forged_receipts(self) -> None:
        receipt = run_synthetic_classical_demo(ResearchEnvironment.TEST)

        with self.assertRaises(ResearchBoundaryError) as count_error:
            replace(receipt, correct_count=receipt.correct_count + 1)
        self.assertIs(count_error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

        with self.assertRaises(ResearchBoundaryError) as claim_error:
            replace(receipt, claim_state="APPROVED")  # type: ignore[arg-type]
        self.assertIs(claim_error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

        object.__setattr__(receipt, "candidate_fingerprint", "f" * 64)
        with self.assertRaises(ResearchBoundaryError) as mutation_error:
            validate_synthetic_classical_demo_receipt(receipt)
        self.assertIs(mutation_error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environments_fail_closed(self) -> None:
        for environment in (
            ResearchEnvironment.STAGING,
            ResearchEnvironment.PILOT,
            ResearchEnvironment.PRODUCTION,
        ):
            with (
                self.subTest(environment=environment),
                self.assertRaises(ResearchBoundaryError) as error,
            ):
                run_synthetic_classical_demo(environment)
            self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticClassicalDemoCliTests(unittest.TestCase):
    def test_cli_emits_canonical_content_free_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "ml.research.demo", "--environment", "TEST"],
            check=False,
            capture_output=True,
            cwd=ROOT,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr, "")
        payload = json.loads(completed.stdout)
        self.assertEqual(
            set(payload),
            {
                "activation_state",
                "authority",
                "baseline_kind",
                "candidate_fingerprint",
                "candidate_id",
                "candidate_status",
                "candidate_version",
                "card_fingerprint",
                "card_metric",
                "card_purpose",
                "card_state",
                "claim_state",
                "correct_count",
                "data_classification",
                "dataset_admission_state",
                "dataset_fingerprint",
                "demo_version",
                "environment",
                "error_count",
                "evaluated_count",
                "evaluation_fingerprint",
                "evaluation_state",
                "evidence_fingerprint",
                "missing_value_policy",
                "model_fingerprint",
                "preprocessing_fingerprint",
                "runtime_state",
                "scaling_policy",
                "split_fingerprint",
                "test_count",
                "train_count",
                "validation_count",
            },
        )
        self.assertEqual(payload["environment"], "TEST")
        self.assertEqual(payload["claim_state"], "NO_PERFORMANCE_OR_CLINICAL_CLAIM")
        self.assertEqual(payload["activation_state"], "NOT_ACTIVATED")
        self.assertEqual(
            completed.stdout,
            json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        )

    def test_cli_protected_environment_returns_stable_error(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "ml.research.demo", "--environment", "PRODUCTION"],
            check=False,
            capture_output=True,
            cwd=ROOT,
            text=True,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, '{"error":"PROTECTED_ENVIRONMENT"}\n')


if __name__ == "__main__":
    unittest.main()
