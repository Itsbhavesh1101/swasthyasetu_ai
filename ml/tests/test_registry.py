"""Immutable registry tests for the synthetic P18-A research boundary."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace

from ml.research.contracts import (
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    synthetic_dataset_fingerprint,
)
from ml.research.registry import SyntheticDatasetRegistry, SyntheticExperimentRegistry
from ml.tests.test_contracts import dataset_manifest, experiment_record


class HostileCollection:
    def __iter__(self) -> object:
        raise RuntimeError("private-canary")

    def __len__(self) -> int:
        raise RuntimeError("private-canary")


class SyntheticResearchRegistryTests(unittest.TestCase):
    def test_dataset_registry_resolves_exact_identity_and_version(self) -> None:
        alpha = dataset_manifest()
        beta = dataset_manifest(dataset_id="syn_ml_dataset_beta")
        registry = SyntheticDatasetRegistry(
            manifests=(alpha, beta), environment=ResearchEnvironment.TEST
        )

        self.assertEqual(registry.manifests, (alpha, beta))
        self.assertEqual(registry.resolve("syn_ml_dataset_alpha", "engineering.v1"), alpha)
        with self.assertRaises(FrozenInstanceError):
            registry.manifests = ()  # type: ignore[misc]

    def test_dataset_registry_has_no_latest_or_mutation_api(self) -> None:
        registry = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        self.assertFalse(hasattr(registry, "latest"))
        self.assertFalse(hasattr(registry, "register"))
        self.assertFalse(hasattr(registry, "promote"))

    def test_dataset_registry_rejects_unknown_identity_without_echo(self) -> None:
        registry = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            registry.resolve("private-canary", "engineering.v1")

        self.assertIs(error.exception.code, ResearchBoundaryCode.UNKNOWN_IDENTITY)
        self.assertNotIn("private-canary", str(error.exception))

    def test_dataset_registry_rejects_duplicate_identity_and_version(self) -> None:
        manifest = dataset_manifest()

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticDatasetRegistry(
                manifests=(manifest, manifest), environment=ResearchEnvironment.TEST
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.DUPLICATE_IDENTITY)

    def test_dataset_registry_rejects_more_than_32_entries(self) -> None:
        manifests = tuple(dataset_manifest() for _ in range(33))

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticDatasetRegistry(manifests=manifests, environment=ResearchEnvironment.TEST)

        self.assertIs(error.exception.code, ResearchBoundaryCode.CAPACITY_EXCEEDED)

    def test_dataset_registry_snapshots_records_before_caller_mutation(self) -> None:
        manifest = dataset_manifest()
        registry = SyntheticDatasetRegistry(
            manifests=(manifest,), environment=ResearchEnvironment.TEST
        )
        object.__setattr__(manifest, "dataset_version", "engineering.v2")

        resolved = registry.resolve("syn_ml_dataset_alpha", "engineering.v1")

        self.assertEqual(resolved.dataset_version, "engineering.v1")

    def test_dataset_registry_reconstructs_and_rejects_forged_records(self) -> None:
        manifest = dataset_manifest()
        object.__setattr__(manifest, "classification", "PATIENT_DATA")

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticDatasetRegistry(manifests=(manifest,), environment=ResearchEnvironment.TEST)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_protected_environment_denies_before_hostile_dataset_collection_is_read(
        self,
    ) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticDatasetRegistry(
                manifests=HostileCollection(),  # type: ignore[arg-type]
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)
        self.assertNotIn("private-canary", str(error.exception))

    def test_experiment_registry_resolves_record_bound_to_exact_dataset(self) -> None:
        manifest = dataset_manifest()
        datasets = SyntheticDatasetRegistry(
            manifests=(manifest,), environment=ResearchEnvironment.TEST
        )
        record = experiment_record(dataset_fingerprint=synthetic_dataset_fingerprint(manifest))
        registry = SyntheticExperimentRegistry(
            records=(record,), datasets=datasets, environment=ResearchEnvironment.TEST
        )

        self.assertEqual(registry.resolve("syn_ml_experiment_alpha", "engineering.v1"), record)

    def test_experiment_registry_rejects_dataset_fingerprint_drift(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=(experiment_record(dataset_fingerprint="f" * 64),),
                datasets=datasets,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_experiment_registry_rejects_unknown_dataset_version(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=(experiment_record(dataset_version="engineering.v2"),),
                datasets=datasets,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_experiment_registry_rejects_duplicate_identity_and_version(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )
        record = experiment_record()

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=(record, record),
                datasets=datasets,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.DUPLICATE_IDENTITY)

    def test_experiment_registry_rejects_more_than_32_entries(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )
        records = tuple(experiment_record() for _ in range(33))

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=records,
                datasets=datasets,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.CAPACITY_EXCEEDED)

    def test_experiment_registry_snapshots_records_before_caller_mutation(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )
        record = experiment_record()
        registry = SyntheticExperimentRegistry(
            records=(record,), datasets=datasets, environment=ResearchEnvironment.TEST
        )
        object.__setattr__(record, "seed", 99)

        self.assertEqual(registry.resolve("syn_ml_experiment_alpha", "engineering.v1").seed, 7)

    def test_experiment_registry_snapshots_dataset_registry_before_caller_mutation(
        self,
    ) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )
        registry = SyntheticExperimentRegistry(
            records=(experiment_record(),),
            datasets=datasets,
            environment=ResearchEnvironment.TEST,
        )
        object.__setattr__(datasets, "environment", ResearchEnvironment.PRODUCTION)

        self.assertIs(registry.datasets.environment, ResearchEnvironment.TEST)
        self.assertEqual(
            registry.datasets.resolve("syn_ml_dataset_alpha", "engineering.v1"),
            dataset_manifest(),
        )

    def test_experiment_registry_rejects_environment_mismatch(self) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=(experiment_record(),),
                datasets=datasets,
                environment=ResearchEnvironment.LOCAL,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environment_denies_before_hostile_experiment_collection_is_read(
        self,
    ) -> None:
        datasets = SyntheticDatasetRegistry(
            manifests=(dataset_manifest(),), environment=ResearchEnvironment.TEST
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=HostileCollection(),  # type: ignore[arg-type]
                datasets=datasets,
                environment=ResearchEnvironment.STAGING,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)
        self.assertNotIn("private-canary", str(error.exception))

    def test_replacing_bound_dataset_metadata_requires_new_fingerprint(self) -> None:
        manifest = dataset_manifest()
        datasets = SyntheticDatasetRegistry(
            manifests=(replace(manifest, schema_version="engineering.v2"),),
            environment=ResearchEnvironment.TEST,
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticExperimentRegistry(
                records=(experiment_record(),),
                datasets=datasets,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)


if __name__ == "__main__":
    unittest.main()
