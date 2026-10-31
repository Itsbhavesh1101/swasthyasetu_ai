"""Adversarial tests for the synthetic-only P18-B pipeline mechanics."""

from __future__ import annotations

import math
import unittest
from dataclasses import FrozenInstanceError, replace

from ml.research.contracts import (
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
)
from ml.research.pipeline import (
    MissingValuePolicy,
    ScalingPolicy,
    SyntheticClass,
    SyntheticExpectedLabel,
    SyntheticFeatureRow,
    SyntheticPartition,
    SyntheticPartitionAssignment,
    SyntheticPredictedLabel,
    SyntheticPreprocessingPlan,
    SyntheticSplitConfig,
    SyntheticSplitManifest,
    build_deterministic_group_split,
    evaluate_synthetic_labels,
    fit_synthetic_preprocessor,
    synthetic_evaluation_fingerprint,
    synthetic_preprocessing_fingerprint,
    synthetic_split_fingerprint,
    transform_synthetic_partition,
    validate_synthetic_split_manifest,
)

DATASET_FINGERPRINT = "a" * 64


def feature_rows(*, groups: int = 12) -> tuple[SyntheticFeatureRow, ...]:
    return tuple(
        SyntheticFeatureRow(
            row_id=f"syn_row_{index:04d}",
            group_id=f"syn_group_{index:04d}",
            values=(float(index), None if index % 3 == 0 else float(index * 2)),
        )
        for index in range(groups)
    )


def split_config(**changes: object) -> SyntheticSplitConfig:
    values: dict[str, object] = {
        "split_version": "engineering.v1",
        "dataset_fingerprint": DATASET_FINGERPRINT,
        "seed": 17,
        "train_basis_points": 6000,
        "validation_basis_points": 2000,
        "test_basis_points": 2000,
        "authority": ResearchAuthority.ENGINEERING_ONLY,
    }
    values.update(changes)
    return SyntheticSplitConfig(**values)  # type: ignore[arg-type]


def split_manifest(
    rows: tuple[SyntheticFeatureRow, ...] | None = None,
) -> SyntheticSplitManifest:
    return build_deterministic_group_split(
        rows=rows or feature_rows(),
        config=split_config(),
        environment=ResearchEnvironment.TEST,
    )


def preprocessing_plan(split: SyntheticSplitManifest) -> SyntheticPreprocessingPlan:
    return SyntheticPreprocessingPlan(
        plan_version="engineering.v1",
        split_fingerprint=synthetic_split_fingerprint(split),
        feature_names=("syn_feature_alpha", "syn_feature_beta"),
        missing_value_policy=MissingValuePolicy.TRAIN_MEAN,
        scaling_policy=ScalingPolicy.STANDARD_SCORE,
        fit_partition=SyntheticPartition.TRAIN,
    )


class HostileRows:
    def __iter__(self) -> object:
        raise RuntimeError("private-canary")

    def __len__(self) -> int:
        raise RuntimeError("private-canary")


class SyntheticSplitTests(unittest.TestCase):
    def test_split_is_deterministic_and_input_order_independent(self) -> None:
        rows = feature_rows()

        first = split_manifest(rows)
        second = split_manifest(tuple(reversed(rows)))

        self.assertEqual(first, second)
        self.assertEqual(synthetic_split_fingerprint(first), synthetic_split_fingerprint(second))
        self.assertEqual({item.partition for item in first.assignments}, set(SyntheticPartition))

    def test_split_fingerprint_binds_requested_ratios(self) -> None:
        manifest = split_manifest()
        changed = replace(
            manifest,
            train_basis_points=5000,
            validation_basis_points=3000,
            test_basis_points=2000,
        )

        self.assertNotEqual(
            synthetic_split_fingerprint(manifest), synthetic_split_fingerprint(changed)
        )

    def test_largest_remainder_apportionment_is_stable(self) -> None:
        manifest = build_deterministic_group_split(
            rows=feature_rows(groups=5),
            config=split_config(
                train_basis_points=3334,
                validation_basis_points=3333,
                test_basis_points=3333,
            ),
            environment=ResearchEnvironment.TEST,
        )
        counts = {
            partition: sum(item.partition is partition for item in manifest.assignments)
            for partition in SyntheticPartition
        }

        self.assertEqual(counts[SyntheticPartition.TRAIN], 2)
        self.assertEqual(counts[SyntheticPartition.VALIDATION], 2)
        self.assertEqual(counts[SyntheticPartition.TEST], 1)

    def test_groups_never_cross_partitions(self) -> None:
        rows = feature_rows(groups=6)
        rows = rows + (
            SyntheticFeatureRow(
                row_id="syn_row_0099",
                group_id=rows[0].group_id,
                values=(99.0, 198.0),
            ),
        )

        manifest = split_manifest(rows)
        group_partitions = {
            item.partition for item in manifest.assignments if item.group_id == rows[0].group_id
        }

        self.assertEqual(len(group_partitions), 1)

    def test_duplicate_row_identity_fails_closed(self) -> None:
        rows = feature_rows(groups=3)

        with self.assertRaises(ResearchBoundaryError) as error:
            split_manifest(rows + (rows[0],))

        self.assertIs(error.exception.code, ResearchBoundaryCode.DUPLICATE_IDENTITY)

    def test_split_requires_three_distinct_groups(self) -> None:
        rows = (
            SyntheticFeatureRow(
                row_id="syn_row_0001", group_id="syn_group_0001", values=(1.0, 2.0)
            ),
            SyntheticFeatureRow(
                row_id="syn_row_0002", group_id="syn_group_0001", values=(2.0, 3.0)
            ),
            SyntheticFeatureRow(
                row_id="syn_row_0003", group_id="syn_group_0002", values=(3.0, 4.0)
            ),
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            split_manifest(rows)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INCOMPLETE_PARTITION)

    def test_direct_constructor_rejects_group_leakage(self) -> None:
        assignments = (
            SyntheticPartitionAssignment(
                row_id="syn_row_0001",
                group_id="syn_group_0001",
                partition=SyntheticPartition.TRAIN,
            ),
            SyntheticPartitionAssignment(
                row_id="syn_row_0002",
                group_id="syn_group_0001",
                partition=SyntheticPartition.TEST,
            ),
            SyntheticPartitionAssignment(
                row_id="syn_row_0003",
                group_id="syn_group_0003",
                partition=SyntheticPartition.VALIDATION,
            ),
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticSplitManifest(
                split_version="engineering.v1",
                dataset_fingerprint=DATASET_FINGERPRINT,
                seed=17,
                train_basis_points=6000,
                validation_basis_points=2000,
                test_basis_points=2000,
                assignments=assignments,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.LEAKAGE_DETECTED)

    def test_validator_rejects_forced_partition_mutation(self) -> None:
        manifest = split_manifest()
        object.__setattr__(manifest.assignments[0], "partition", "TEST")

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_split_manifest(manifest)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_invalid_ratios_and_bool_seed_are_rejected(self) -> None:
        for changes in (
            {"seed": True},
            {"train_basis_points": 7000},
            {"test_basis_points": 0, "validation_basis_points": 3000},
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(ResearchBoundaryError),
            ):
                split_config(**changes)

    def test_protected_environment_denies_before_rows_are_read(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            build_deterministic_group_split(
                rows=HostileRows(),  # type: ignore[arg-type]
                config=split_config(),
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticPreprocessingTests(unittest.TestCase):
    def test_fit_uses_train_partition_only(self) -> None:
        rows = feature_rows()
        split = split_manifest(rows)
        plan = preprocessing_plan(split)
        changed = tuple(
            replace(row, values=(9999.0, -9999.0))
            if next(item for item in split.assignments if item.row_id == row.row_id).partition
            is SyntheticPartition.TEST
            else row
            for row in rows
        )

        original_receipt = fit_synthetic_preprocessor(
            rows=rows, split=split, plan=plan, environment=ResearchEnvironment.TEST
        )
        changed_receipt = fit_synthetic_preprocessor(
            rows=changed, split=split, plan=plan, environment=ResearchEnvironment.TEST
        )

        self.assertEqual(original_receipt, changed_receipt)

    def test_train_mean_imputation_and_standard_scaling_are_deterministic(self) -> None:
        rows = feature_rows()
        split = split_manifest(rows)
        receipt = fit_synthetic_preprocessor(
            rows=rows,
            split=split,
            plan=preprocessing_plan(split),
            environment=ResearchEnvironment.TEST,
        )

        first = transform_synthetic_partition(
            rows=rows,
            split=split,
            receipt=receipt,
            partition=SyntheticPartition.TEST,
            environment=ResearchEnvironment.TEST,
        )
        second = transform_synthetic_partition(
            rows=tuple(reversed(rows)),
            split=split,
            receipt=receipt,
            partition=SyntheticPartition.TEST,
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(first, second)
        self.assertTrue(all(math.isfinite(value) for row in first.rows for value in row.values))

    def test_zero_variance_feature_uses_unit_scale(self) -> None:
        rows = tuple(replace(row, values=(1.0, row.values[1])) for row in feature_rows())
        split = split_manifest(rows)

        receipt = fit_synthetic_preprocessor(
            rows=rows,
            split=split,
            plan=preprocessing_plan(split),
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(receipt.statistics[0].scale, 1.0)

    def test_missing_or_extra_rows_fail_exact_membership_check(self) -> None:
        rows = feature_rows()
        split = split_manifest(rows)
        plan = preprocessing_plan(split)

        for changed in (rows[:-1], rows + (replace(rows[0], row_id="syn_row_0099"),)):
            with self.subTest(size=len(changed)):
                with self.assertRaises(ResearchBoundaryError) as error:
                    fit_synthetic_preprocessor(
                        rows=changed,
                        split=split,
                        plan=plan,
                        environment=ResearchEnvironment.TEST,
                    )
                self.assertIs(error.exception.code, ResearchBoundaryCode.PARTITION_MISMATCH)

    def test_non_finite_feature_is_rejected(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticFeatureRow(
                row_id="syn_row_0001",
                group_id="syn_group_0001",
                values=(float("nan"),),
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_plan_cannot_fit_validation_or_test(self) -> None:
        split = split_manifest()
        for partition in (SyntheticPartition.VALIDATION, SyntheticPartition.TEST):
            with self.subTest(partition=partition):
                with self.assertRaises(ResearchBoundaryError) as error:
                    replace(preprocessing_plan(split), fit_partition=partition)
                self.assertIs(error.exception.code, ResearchBoundaryCode.LEAKAGE_DETECTED)

    def test_preprocessing_receipt_is_immutable_and_fingerprinted(self) -> None:
        rows = feature_rows()
        split = split_manifest(rows)
        receipt = fit_synthetic_preprocessor(
            rows=rows,
            split=split,
            plan=preprocessing_plan(split),
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(len(synthetic_preprocessing_fingerprint(receipt)), 64)
        with self.assertRaises(FrozenInstanceError):
            receipt.fit_row_count = 0  # type: ignore[misc]

    def test_protected_environment_denies_before_preprocessing_rows_are_read(
        self,
    ) -> None:
        split = split_manifest()

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_preprocessor(
                rows=HostileRows(),  # type: ignore[arg-type]
                split=split,
                plan=preprocessing_plan(split),
                environment=ResearchEnvironment.PILOT,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticEvaluationTests(unittest.TestCase):
    def _prepared(
        self,
    ) -> tuple[tuple[SyntheticFeatureRow, ...], SyntheticSplitManifest, object]:
        rows = feature_rows()
        split = split_manifest(rows)
        receipt = fit_synthetic_preprocessor(
            rows=rows,
            split=split,
            plan=preprocessing_plan(split),
            environment=ResearchEnvironment.TEST,
        )
        return rows, split, receipt

    def test_exact_test_membership_produces_content_free_counts(self) -> None:
        _, split, receipt = self._prepared()
        test_ids = tuple(
            item.row_id for item in split.assignments if item.partition is SyntheticPartition.TEST
        )
        expected = tuple(
            SyntheticExpectedLabel(
                row_id=row_id,
                label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
            )
            for index, row_id in enumerate(test_ids)
        )
        predicted = tuple(
            SyntheticPredictedLabel(row_id=item.row_id, label=item.label) for item in expected
        )

        result = evaluate_synthetic_labels(
            expected=expected,
            predicted=predicted,
            split=split,
            preprocessing=receipt,  # type: ignore[arg-type]
            evaluation_version="engineering.v1",
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(result.correct_count, len(test_ids))
        self.assertEqual(result.error_count, 0)
        self.assertEqual(len(synthetic_evaluation_fingerprint(result)), 64)

    def test_missing_extra_or_duplicate_prediction_fails_closed(self) -> None:
        _, split, receipt = self._prepared()
        test_ids = tuple(
            item.row_id for item in split.assignments if item.partition is SyntheticPartition.TEST
        )
        expected = tuple(
            SyntheticExpectedLabel(
                row_id=row_id,
                label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
            )
            for index, row_id in enumerate(test_ids)
        )
        valid = tuple(
            SyntheticPredictedLabel(row_id=item.row_id, label=item.label) for item in expected
        )

        variants = (
            valid[:-1],
            valid + (valid[0],),
            valid + (replace(valid[0], row_id="syn_row_0099"),),
        )
        for predicted in variants:
            with (
                self.subTest(size=len(predicted)),
                self.assertRaises(ResearchBoundaryError),
            ):
                evaluate_synthetic_labels(
                    expected=expected,
                    predicted=predicted,
                    split=split,
                    preprocessing=receipt,  # type: ignore[arg-type]
                    evaluation_version="engineering.v1",
                    environment=ResearchEnvironment.TEST,
                )

    def test_degenerate_expected_class_fails_closed(self) -> None:
        _, split, receipt = self._prepared()
        test_ids = tuple(
            item.row_id for item in split.assignments if item.partition is SyntheticPartition.TEST
        )
        expected = tuple(
            SyntheticExpectedLabel(row_id=row_id, label=SyntheticClass.CLASS_ALPHA)
            for row_id in test_ids
        )
        predicted = tuple(
            SyntheticPredictedLabel(row_id=row_id, label=SyntheticClass.CLASS_ALPHA)
            for row_id in test_ids
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            evaluate_synthetic_labels(
                expected=expected,
                predicted=predicted,
                split=split,
                preprocessing=receipt,  # type: ignore[arg-type]
                evaluation_version="engineering.v1",
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.DEGENERATE_EVALUATION)

    def test_evaluation_requires_matching_preprocessing_receipt(self) -> None:
        rows, split, receipt = self._prepared()
        other_split = split_manifest(tuple(reversed(rows)))
        object.__setattr__(
            receipt,
            "split_fingerprint",
            synthetic_split_fingerprint(other_split)[:-1] + "0",
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            evaluate_synthetic_labels(
                expected=(),
                predicted=(),
                split=split,
                preprocessing=receipt,  # type: ignore[arg-type]
                evaluation_version="engineering.v1",
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environment_denies_before_label_collections_are_read(
        self,
    ) -> None:
        _, split, receipt = self._prepared()

        with self.assertRaises(ResearchBoundaryError) as error:
            evaluate_synthetic_labels(
                expected=HostileRows(),  # type: ignore[arg-type]
                predicted=HostileRows(),  # type: ignore[arg-type]
                split=split,
                preprocessing=receipt,  # type: ignore[arg-type]
                evaluation_version="engineering.v1",
                environment=ResearchEnvironment.STAGING,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


if __name__ == "__main__":
    unittest.main()
