"""Strict contract tests for the synthetic P18-A research boundary."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

from ml.research.contracts import (
    DatasetAdmissionState,
    ExperimentApprovalState,
    ExperimentExecutionState,
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    SyntheticDataClassification,
    SyntheticDatasetManifest,
    SyntheticDatasetSource,
    SyntheticExperimentRecord,
    SyntheticLicense,
    synthetic_dataset_fingerprint,
    synthetic_experiment_fingerprint,
    validate_synthetic_dataset_manifest,
    validate_synthetic_experiment_record,
)

NOW = datetime(2026, 10, 31, 8, tzinfo=UTC)
DATASET_FINGERPRINT = "7386b66db62cf308c68f5d599c8350ee09365f494e2cef389eb593c0b7cbeb98"
EXPERIMENT_FINGERPRINT = "134a58d24d521e7b5e2243e6f84291b10527f218a56795445ac1409383770ff7"


def dataset_manifest(**changes: object) -> SyntheticDatasetManifest:
    values: dict[str, object] = {
        "dataset_id": "syn_ml_dataset_alpha",
        "dataset_version": "engineering.v1",
        "source": SyntheticDatasetSource.SYNTHETIC_GENERATED,
        "classification": SyntheticDataClassification.SYNTHETIC_NON_MEDICAL,
        "license": SyntheticLicense.ENGINEERING_FIXTURE_ONLY,
        "admission_state": DatasetAdmissionState.TEST_ONLY_UNAPPROVED,
        "content_hash": "a" * 64,
        "schema_hash": "b" * 64,
        "schema_version": "engineering.v1",
        "created_at": NOW,
        "authority": ResearchAuthority.ENGINEERING_ONLY,
    }
    values.update(changes)
    return SyntheticDatasetManifest(**values)  # type: ignore[arg-type]


def experiment_record(**changes: object) -> SyntheticExperimentRecord:
    values: dict[str, object] = {
        "experiment_id": "syn_ml_experiment_alpha",
        "experiment_version": "engineering.v1",
        "dataset_id": "syn_ml_dataset_alpha",
        "dataset_version": "engineering.v1",
        "dataset_fingerprint": DATASET_FINGERPRINT,
        "code_commit": "c" * 40,
        "dependency_lock_hash": "d" * 64,
        "configuration_hash": "e" * 64,
        "seed": 7,
        "created_at": NOW,
        "execution_state": ExperimentExecutionState.NOT_EXECUTED,
        "approval_state": ExperimentApprovalState.TEST_ONLY_UNAPPROVED,
        "authority": ResearchAuthority.ENGINEERING_ONLY,
    }
    values.update(changes)
    return SyntheticExperimentRecord(**values)  # type: ignore[arg-type]


class SyntheticResearchContractTests(unittest.TestCase):
    def test_dataset_manifest_is_immutable_and_has_canonical_fingerprint(self) -> None:
        manifest = dataset_manifest()

        self.assertEqual(synthetic_dataset_fingerprint(manifest), DATASET_FINGERPRINT)
        with self.assertRaises(FrozenInstanceError):
            manifest.dataset_id = "syn_ml_dataset_beta"  # type: ignore[misc]

    def test_experiment_record_is_immutable_and_has_canonical_fingerprint(self) -> None:
        record = experiment_record()

        self.assertEqual(synthetic_experiment_fingerprint(record), EXPERIMENT_FINGERPRINT)
        with self.assertRaises(FrozenInstanceError):
            record.seed = 8  # type: ignore[misc]

    def test_aware_non_utc_times_are_normalized(self) -> None:
        india = timezone(timedelta(hours=5, minutes=30))
        local_time = datetime(2026, 10, 31, 13, 30, tzinfo=india)

        self.assertEqual(dataset_manifest(created_at=local_time).created_at, NOW)
        self.assertEqual(experiment_record(created_at=local_time).created_at, NOW)

    def test_naive_time_is_rejected(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            dataset_manifest(created_at=datetime(2026, 10, 31, 8))

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_free_text_identity_is_unrepresentable(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            dataset_manifest(dataset_id="unapproved_dataset")

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)
        self.assertNotIn("unapproved", str(error.exception))

    def test_uppercase_or_wrong_length_hash_is_rejected(self) -> None:
        for invalid_hash in ("A" * 64, "a" * 63):
            with self.subTest(invalid_hash=invalid_hash):
                with self.assertRaises(ResearchBoundaryError) as error:
                    dataset_manifest(content_hash=invalid_hash)
                self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_bool_seed_is_rejected_even_though_bool_is_an_int(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            experiment_record(seed=True)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_seed_outside_uint32_range_is_rejected(self) -> None:
        for invalid_seed in (-1, 2**32):
            with self.subTest(invalid_seed=invalid_seed):
                with self.assertRaises(ResearchBoundaryError) as error:
                    experiment_record(seed=invalid_seed)
                self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_wrong_enum_type_is_rejected(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            dataset_manifest(source="SYNTHETIC_GENERATED")

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_dataset_validator_reconstructs_and_rejects_forced_mutation(self) -> None:
        manifest = dataset_manifest()
        object.__setattr__(manifest, "dataset_id", "unapproved_hidden")

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_dataset_manifest(manifest)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_experiment_validator_reconstructs_and_rejects_forced_mutation(
        self,
    ) -> None:
        record = experiment_record()
        object.__setattr__(record, "execution_state", "COMPLETED")

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_experiment_record(record)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_fingerprint_changes_when_bound_metadata_changes(self) -> None:
        manifest = dataset_manifest()
        changed = replace(manifest, dataset_version="engineering.v2")

        self.assertNotEqual(
            synthetic_dataset_fingerprint(manifest),
            synthetic_dataset_fingerprint(changed),
        )

    def test_errors_are_stable_and_do_not_echo_hostile_values(self) -> None:
        canary = "private-canary-sensitive-text"

        with self.assertRaises(ResearchBoundaryError) as error:
            experiment_record(experiment_id=canary)

        self.assertEqual(str(error.exception), ResearchBoundaryCode.INVALID_VALUE.value)
        self.assertNotIn(canary, str(error.exception))


if __name__ == "__main__":
    unittest.main()
