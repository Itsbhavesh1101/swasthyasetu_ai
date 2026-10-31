"""Adversarial tests for deterministic synthetic-only P18-C baselines."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace

from ml.research.baselines import (
    SyntheticBaselineKind,
    SyntheticBaselineModel,
    SyntheticBaselineState,
    fit_synthetic_baseline,
    predict_synthetic_baseline,
    synthetic_baseline_fingerprint,
    validate_synthetic_baseline_model,
)
from ml.research.contracts import (
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
)
from ml.research.pipeline import (
    SyntheticClass,
    SyntheticExpectedLabel,
    SyntheticPartition,
    SyntheticPreprocessingReceipt,
    SyntheticSplitManifest,
    SyntheticTransformedBatch,
    SyntheticTransformedRow,
    evaluate_synthetic_labels,
    fit_synthetic_preprocessor,
    synthetic_evaluation_fingerprint,
    transform_synthetic_partition,
)
from ml.tests.test_pipeline import feature_rows, preprocessing_plan, split_manifest


class HostileLabels:
    def __iter__(self) -> object:
        raise RuntimeError("private-canary")

    def __len__(self) -> int:
        raise RuntimeError("private-canary")


def prepared() -> tuple[
    SyntheticSplitManifest,
    SyntheticPreprocessingReceipt,
    SyntheticTransformedBatch,
    SyntheticTransformedBatch,
    SyntheticTransformedBatch,
    tuple[SyntheticExpectedLabel, ...],
]:
    rows = feature_rows()
    split = split_manifest(rows)
    receipt = fit_synthetic_preprocessor(
        rows=rows,
        split=split,
        plan=preprocessing_plan(split),
        environment=ResearchEnvironment.TEST,
    )
    batches = tuple(
        transform_synthetic_partition(
            rows=rows,
            split=split,
            receipt=receipt,
            partition=partition,
            environment=ResearchEnvironment.TEST,
        )
        for partition in SyntheticPartition
    )
    train, validation, test = batches
    labels = tuple(
        SyntheticExpectedLabel(
            row_id=row.row_id,
            label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
        )
        for index, row in enumerate(train.rows)
    )
    return split, receipt, train, validation, test, labels


class SyntheticBaselineFitTests(unittest.TestCase):
    def test_both_baselines_fit_deterministically(self) -> None:
        split, receipt, train, _, _, labels = prepared()

        for kind in SyntheticBaselineKind:
            with self.subTest(kind=kind):
                first = fit_synthetic_baseline(
                    model_id="syn_ml_model_alpha",
                    model_version="engineering.v1",
                    kind=kind,
                    split=split,
                    preprocessing=receipt,
                    training_batch=train,
                    labels=labels,
                    tie_break_class=SyntheticClass.CLASS_ALPHA,
                    environment=ResearchEnvironment.TEST,
                )
                second = fit_synthetic_baseline(
                    model_id="syn_ml_model_alpha",
                    model_version="engineering.v1",
                    kind=kind,
                    split=split,
                    preprocessing=receipt,
                    training_batch=train,
                    labels=tuple(reversed(labels)),
                    tie_break_class=SyntheticClass.CLASS_ALPHA,
                    environment=ResearchEnvironment.TEST,
                )

                self.assertEqual(first, second)
                self.assertEqual(
                    synthetic_baseline_fingerprint(first),
                    synthetic_baseline_fingerprint(second),
                )

    def test_fit_requires_exact_training_membership(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        variants = (
            labels[:-1],
            labels + (labels[0],),
            labels + (replace(labels[0], row_id="syn_row_0099"),),
        )

        for changed in variants:
            with self.subTest(size=len(changed)), self.assertRaises(ResearchBoundaryError):
                fit_synthetic_baseline(
                    model_id="syn_ml_model_alpha",
                    model_version="engineering.v1",
                    kind=SyntheticBaselineKind.NEAREST_CENTROID,
                    split=split,
                    preprocessing=receipt,
                    training_batch=train,
                    labels=changed,
                    tie_break_class=SyntheticClass.CLASS_ALPHA,
                    environment=ResearchEnvironment.TEST,
                )

    def test_fit_rejects_non_training_partition(self) -> None:
        split, receipt, _, validation, _, labels = prepared()

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_baseline(
                model_id="syn_ml_model_alpha",
                model_version="engineering.v1",
                kind=SyntheticBaselineKind.MAJORITY_CLASS,
                split=split,
                preprocessing=receipt,
                training_batch=validation,
                labels=labels,
                tie_break_class=SyntheticClass.CLASS_ALPHA,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.LEAKAGE_DETECTED)

    def test_fit_rejects_degenerate_training_labels(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        degenerate = tuple(replace(label, label=SyntheticClass.CLASS_ALPHA) for label in labels)

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_baseline(
                model_id="syn_ml_model_alpha",
                model_version="engineering.v1",
                kind=SyntheticBaselineKind.NEAREST_CENTROID,
                split=split,
                preprocessing=receipt,
                training_batch=train,
                labels=degenerate,
                tie_break_class=SyntheticClass.CLASS_ALPHA,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.DEGENERATE_EVALUATION)

    def test_fit_rejects_split_or_preprocessing_drift(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        forged = replace(train, split_fingerprint="f" * 64)

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_baseline(
                model_id="syn_ml_model_alpha",
                model_version="engineering.v1",
                kind=SyntheticBaselineKind.MAJORITY_CLASS,
                split=split,
                preprocessing=receipt,
                training_batch=forged,
                labels=labels,
                tie_break_class=SyntheticClass.CLASS_ALPHA,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_fit_fails_closed_on_centroid_overflow(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        oversized = replace(
            train,
            rows=tuple(replace(row, values=(1e308, 1e308)) for row in train.rows),
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_baseline(
                model_id="syn_ml_model_alpha",
                model_version="engineering.v1",
                kind=SyntheticBaselineKind.NEAREST_CENTROID,
                split=split,
                preprocessing=receipt,
                training_batch=oversized,
                labels=labels,
                tie_break_class=SyntheticClass.CLASS_ALPHA,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_model_is_immutable_and_validator_rejects_forced_mutation(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        model = fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.NEAREST_CENTROID,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )
        with self.assertRaises(FrozenInstanceError):
            model.feature_count = 0  # type: ignore[misc]
        object.__setattr__(model, "kind", "UNAPPROVED_MODEL")

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_baseline_model(model)

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_direct_constructor_rejects_kind_parameter_mismatch(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        model = fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.NEAREST_CENTROID,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            replace(model, kind=SyntheticBaselineKind.MAJORITY_CLASS)

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_model_has_no_registration_promotion_or_serialization_api(self) -> None:
        model = self._fitted_majority()

        for name in ("register", "promote", "save", "load", "activate"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(model, name))

    def test_unapproved_state_and_content_free_errors_are_enforced(self) -> None:
        model = self._fitted_majority()
        self.assertIs(model.state, SyntheticBaselineState.TEST_ONLY_UNAPPROVED)
        canary = "private-canary-sensitive-text"

        with self.assertRaises(ResearchBoundaryError) as error:
            replace(model, model_id=canary)

        self.assertEqual(str(error.exception), ResearchBoundaryCode.INVALID_VALUE.value)
        self.assertNotIn(canary, str(error.exception))

    def _fitted_majority(self) -> SyntheticBaselineModel:
        split, receipt, train, _, _, labels = prepared()
        return fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.MAJORITY_CLASS,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )

    def test_protected_environment_denies_before_labels_are_read(self) -> None:
        split, receipt, train, _, _, _ = prepared()

        with self.assertRaises(ResearchBoundaryError) as error:
            fit_synthetic_baseline(
                model_id="syn_ml_model_alpha",
                model_version="engineering.v1",
                kind=SyntheticBaselineKind.MAJORITY_CLASS,
                split=split,
                preprocessing=receipt,
                training_batch=train,
                labels=HostileLabels(),  # type: ignore[arg-type]
                tie_break_class=SyntheticClass.CLASS_ALPHA,
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticBaselinePredictionTests(unittest.TestCase):
    def _model(
        self, kind: SyntheticBaselineKind = SyntheticBaselineKind.NEAREST_CENTROID
    ) -> SyntheticBaselineModel:
        split, receipt, train, _, _, labels = prepared()
        return fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=kind,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )

    def test_both_baselines_predict_validation_and_test_deterministically(self) -> None:
        split, _, _, validation, test, _ = prepared()

        for kind in SyntheticBaselineKind:
            model = self._model(kind)
            for batch in (validation, test):
                with self.subTest(kind=kind, partition=batch.partition):
                    first = predict_synthetic_baseline(
                        model=model,
                        split=split,
                        batch=batch,
                        environment=ResearchEnvironment.TEST,
                    )
                    second = predict_synthetic_baseline(
                        model=model,
                        split=split,
                        batch=batch,
                        environment=ResearchEnvironment.TEST,
                    )
                    self.assertEqual(first, second)
                    self.assertEqual(
                        tuple(item.row_id for item in first),
                        tuple(row.row_id for row in batch.rows),
                    )

    def test_end_to_end_synthetic_evaluation_is_reproducible(self) -> None:
        split, receipt, train, _, test, labels = prepared()
        model = fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.NEAREST_CENTROID,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )
        predicted = predict_synthetic_baseline(
            model=model,
            split=split,
            batch=test,
            environment=ResearchEnvironment.TEST,
        )
        expected = tuple(
            SyntheticExpectedLabel(
                row_id=row.row_id,
                label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
            )
            for index, row in enumerate(test.rows)
        )

        first = evaluate_synthetic_labels(
            expected=expected,
            predicted=predicted,
            split=split,
            preprocessing=receipt,
            evaluation_version="engineering.v1",
            environment=ResearchEnvironment.TEST,
        )
        second = evaluate_synthetic_labels(
            expected=expected,
            predicted=predicted,
            split=split,
            preprocessing=receipt,
            evaluation_version="engineering.v1",
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(first, second)
        self.assertEqual(
            synthetic_evaluation_fingerprint(first),
            synthetic_evaluation_fingerprint(second),
        )

    def test_prediction_rejects_training_partition(self) -> None:
        split, _, train, _, _, _ = prepared()

        with self.assertRaises(ResearchBoundaryError) as error:
            predict_synthetic_baseline(
                model=self._model(),
                split=split,
                batch=train,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.LEAKAGE_DETECTED)

    def test_prediction_rejects_preprocessing_or_feature_drift(self) -> None:
        split, _, _, validation, _, _ = prepared()
        model = self._model()
        variants = (
            replace(validation, preprocessing_fingerprint="f" * 64),
            SyntheticTransformedBatch(
                split_fingerprint=validation.split_fingerprint,
                preprocessing_fingerprint=validation.preprocessing_fingerprint,
                partition=validation.partition,
                rows=tuple(
                    SyntheticTransformedRow(row_id=row.row_id, values=(row.values[0],))
                    for row in validation.rows
                ),
            ),
        )

        for batch in variants:
            with self.subTest(batch=batch), self.assertRaises(ResearchBoundaryError) as error:
                predict_synthetic_baseline(
                    model=model,
                    split=split,
                    batch=batch,
                    environment=ResearchEnvironment.TEST,
                )
            self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_prediction_fails_closed_on_distance_overflow(self) -> None:
        split, _, _, validation, _, _ = prepared()
        oversized = replace(
            validation,
            rows=tuple(replace(row, values=(1e308, 1e308)) for row in validation.rows),
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            predict_synthetic_baseline(
                model=self._model(),
                split=split,
                batch=oversized,
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_centroid_distance_tie_uses_explicit_tie_break(self) -> None:
        split, receipt, train, validation, _, labels = prepared()
        model = fit_synthetic_baseline(
            model_id="syn_ml_model_alpha",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.NEAREST_CENTROID,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_BETA,
            environment=ResearchEnvironment.TEST,
        )
        midpoint = tuple(
            (alpha + beta) / 2.0
            for alpha, beta in zip(
                model.class_alpha_centroid,
                model.class_beta_centroid,
                strict=True,
            )
        )
        tied_batch = replace(
            validation,
            rows=tuple(replace(row, values=midpoint) for row in validation.rows),
        )

        predictions = predict_synthetic_baseline(
            model=model,
            split=split,
            batch=tied_batch,
            environment=ResearchEnvironment.TEST,
        )

        self.assertTrue(all(item.label is SyntheticClass.CLASS_BETA for item in predictions))

    def test_protected_environment_denies_prediction(self) -> None:
        split, _, _, validation, _, _ = prepared()

        with self.assertRaises(ResearchBoundaryError) as error:
            predict_synthetic_baseline(
                model=self._model(),
                split=split,
                batch=validation,
                environment=ResearchEnvironment.PILOT,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


if __name__ == "__main__":
    unittest.main()
