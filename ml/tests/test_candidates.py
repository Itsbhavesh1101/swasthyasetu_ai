"""Adversarial tests for synthetic-only P18-D candidate metadata."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

from ml.research.baselines import (
    SyntheticBaselineKind,
    SyntheticBaselineModel,
    fit_synthetic_baseline,
    predict_synthetic_baseline,
    synthetic_baseline_fingerprint,
)
from ml.research.candidates import (
    REQUIRED_SYNTHETIC_LIMITATIONS,
    SyntheticCandidateRegistry,
    SyntheticCandidateStatus,
    SyntheticCardMetric,
    SyntheticCardPurpose,
    SyntheticModelCandidate,
    SyntheticModelCard,
    build_synthetic_model_candidate,
    build_synthetic_model_card,
    synthetic_model_candidate_fingerprint,
    synthetic_model_card_fingerprint,
    validate_synthetic_model_candidate,
    validate_synthetic_model_card,
)
from ml.research.contracts import (
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
)
from ml.research.pipeline import (
    SyntheticClass,
    SyntheticEvaluationReceipt,
    SyntheticExpectedLabel,
    SyntheticPartition,
    SyntheticPreprocessingReceipt,
    SyntheticSplitManifest,
    SyntheticTransformedBatch,
    evaluate_synthetic_labels,
)
from ml.tests.test_baselines import prepared


class HostileLabels:
    def __iter__(self) -> object:
        raise RuntimeError("private-canary")


class HostileModel:
    def __getattribute__(self, name: str) -> object:
        raise RuntimeError("private-canary")

    def __len__(self) -> int:
        raise RuntimeError("private-canary")


def evaluated() -> tuple[
    SyntheticBaselineModel,
    SyntheticSplitManifest,
    SyntheticPreprocessingReceipt,
    SyntheticTransformedBatch,
    tuple[SyntheticExpectedLabel, ...],
    SyntheticEvaluationReceipt,
]:
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
    expected = tuple(
        SyntheticExpectedLabel(
            row_id=row.row_id,
            label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
        )
        for index, row in enumerate(test.rows)
    )
    predictions = predict_synthetic_baseline(
        model=model,
        split=split,
        batch=test,
        environment=ResearchEnvironment.TEST,
    )
    evaluation = evaluate_synthetic_labels(
        expected=expected,
        predicted=predictions,
        split=split,
        preprocessing=receipt,
        evaluation_version="engineering.v1",
        environment=ResearchEnvironment.TEST,
    )
    return model, split, receipt, test, expected, evaluation


def build_card(**changes: object) -> SyntheticModelCard:
    model, split, receipt, test, expected, evaluation = evaluated()
    arguments: dict[str, object] = {
        "card_id": "syn_ml_card_alpha",
        "card_version": "engineering.v1",
        "model": model,
        "split": split,
        "preprocessing": receipt,
        "test_batch": test,
        "expected": expected,
        "evaluation": evaluation,
        "generated_at": datetime(2026, 11, 1, 10, 30, tzinfo=UTC),
        "environment": ResearchEnvironment.TEST,
    }
    arguments.update(changes)
    return build_synthetic_model_card(**arguments)  # type: ignore[arg-type]


def build_candidate(**changes: object) -> SyntheticModelCandidate:
    model, _, _, _, _, _ = evaluated()
    arguments: dict[str, object] = {
        "candidate_id": "syn_ml_candidate_0001",
        "candidate_version": "engineering.v1",
        "model": model,
        "card": build_card(),
        "registered_at": datetime(2026, 11, 1, 10, 45, tzinfo=UTC),
        "environment": ResearchEnvironment.TEST,
    }
    arguments.update(changes)
    return build_synthetic_model_candidate(**arguments)  # type: ignore[arg-type]


class SyntheticModelCardTests(unittest.TestCase):
    def test_card_is_deterministic_and_bound_to_recomputed_evidence(self) -> None:
        first = build_card()
        second = build_card()
        model, _, _, _, _, evaluation = evaluated()

        self.assertEqual(first, second)
        self.assertEqual(
            synthetic_model_card_fingerprint(first),
            synthetic_model_card_fingerprint(second),
        )
        self.assertEqual(first.model_fingerprint, synthetic_baseline_fingerprint(model))
        self.assertEqual(first.dataset_fingerprint, evaluated()[1].dataset_fingerprint)
        self.assertEqual(first.evaluated_count, evaluation.evaluated_count)
        self.assertEqual(first.correct_count, evaluation.correct_count)
        self.assertEqual(first.error_count, evaluation.error_count)
        self.assertIs(first.purpose, SyntheticCardPurpose.ENGINEERING_DETERMINISM_ONLY)
        self.assertIs(first.metric, SyntheticCardMetric.EXACT_MATCH_COUNTS_ONLY)
        self.assertEqual(first.limitations, REQUIRED_SYNTHETIC_LIMITATIONS)

    def test_card_rejects_evaluation_not_reproduced_by_bound_model(self) -> None:
        _, _, _, _, _, evaluation = evaluated()
        forged = replace(evaluation, predicted_fingerprint="f" * 64)

        with self.assertRaises(ResearchBoundaryError) as error:
            build_card(evaluation=forged)

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_card_rejects_split_preprocessing_or_partition_drift(self) -> None:
        _, split, receipt, test, _, _ = evaluated()
        variants = (
            {"split": replace(split, dataset_fingerprint="f" * 64)},
            {"preprocessing": replace(receipt, split_fingerprint="f" * 64)},
            {"test_batch": replace(test, partition=SyntheticPartition.VALIDATION)},
        )

        for changes in variants:
            with (
                self.subTest(changes=changes),
                self.assertRaises(ResearchBoundaryError),
            ):
                build_card(**changes)

    def test_card_normalizes_aware_time_and_rejects_naive_time(self) -> None:
        non_utc = datetime(2026, 11, 1, 16, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
        card = build_card(generated_at=non_utc)

        self.assertEqual(card.generated_at, datetime(2026, 11, 1, 10, 30, tzinfo=UTC))
        with self.assertRaises(ResearchBoundaryError) as error:
            build_card(generated_at=datetime(2026, 11, 1, 10, 30))
        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_direct_constructor_rejects_claim_and_count_drift(self) -> None:
        card = build_card()
        variants = (
            {"correct_count": card.correct_count + 1},
            {"limitations": card.limitations[:-1]},
            {"purpose": "CLINICAL_USE"},
            {"metric": "AUROC"},
        )

        for changes in variants:
            with (
                self.subTest(changes=changes),
                self.assertRaises(ResearchBoundaryError),
            ):
                replace(card, **changes)

    def test_card_is_immutable_and_validator_rejects_forced_mutation(self) -> None:
        card = build_card()
        with self.assertRaises(FrozenInstanceError):
            card.correct_count = 0  # type: ignore[misc]
        object.__setattr__(card, "model_fingerprint", "f" * 64)

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_model_card(card)

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_errors_are_content_free(self) -> None:
        canary = "private-canary-sensitive-text"

        with self.assertRaises(ResearchBoundaryError) as error:
            build_card(card_id=canary)

        self.assertEqual(str(error.exception), ResearchBoundaryCode.INVALID_VALUE.value)
        self.assertNotIn(canary, str(error.exception))

    def test_protected_environment_rejects_before_labels_are_read(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            build_card(
                expected=HostileLabels(),
                environment=ResearchEnvironment.PRODUCTION,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticModelCandidateTests(unittest.TestCase):
    def test_candidate_deterministically_binds_exact_model_and_card(self) -> None:
        first = build_candidate()
        second = build_candidate()
        model, _, _, _, _, _ = evaluated()
        card = build_card()

        self.assertEqual(first, second)
        self.assertEqual(
            synthetic_model_candidate_fingerprint(first),
            synthetic_model_candidate_fingerprint(second),
        )
        self.assertEqual(first.model_fingerprint, synthetic_baseline_fingerprint(model))
        self.assertEqual(first.card_fingerprint, synthetic_model_card_fingerprint(card))
        self.assertIs(first.status, SyntheticCandidateStatus.TEST_ONLY_UNAPPROVED)

    def test_candidate_rejects_model_card_mismatch(self) -> None:
        split, receipt, train, _, _, labels = prepared()
        majority = fit_synthetic_baseline(
            model_id="syn_ml_model_beta",
            model_version="engineering.v1",
            kind=SyntheticBaselineKind.MAJORITY_CLASS,
            split=split,
            preprocessing=receipt,
            training_batch=train,
            labels=labels,
            tie_break_class=SyntheticClass.CLASS_ALPHA,
            environment=ResearchEnvironment.TEST,
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            build_candidate(model=majority)

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_candidate_normalizes_aware_time_and_rejects_naive_time(self) -> None:
        non_utc = datetime(2026, 11, 1, 16, 15, tzinfo=timezone(timedelta(hours=5, minutes=30)))
        candidate = build_candidate(registered_at=non_utc)

        self.assertEqual(candidate.registered_at, datetime(2026, 11, 1, 10, 45, tzinfo=UTC))
        with self.assertRaises(ResearchBoundaryError) as error:
            build_candidate(registered_at=datetime(2026, 11, 1, 10, 45))
        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_TYPE)

    def test_candidate_registration_cannot_predate_card_generation(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            build_candidate(registered_at=datetime(2026, 11, 1, 10, 0, tzinfo=UTC))

        self.assertIs(error.exception.code, ResearchBoundaryCode.INVALID_VALUE)

    def test_candidate_is_immutable_and_validator_rejects_forced_mutation(self) -> None:
        candidate = build_candidate()
        with self.assertRaises(FrozenInstanceError):
            candidate.status = SyntheticCandidateStatus.TEST_ONLY_UNAPPROVED  # type: ignore[misc]
        object.__setattr__(candidate, "card_fingerprint", "f" * 64)

        with self.assertRaises(ResearchBoundaryError) as error:
            validate_synthetic_model_candidate(candidate)

        self.assertIs(error.exception.code, ResearchBoundaryCode.IDENTITY_MISMATCH)

    def test_protected_environment_rejects_before_model_is_read(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            build_candidate(
                model=HostileModel(),
                environment=ResearchEnvironment.PILOT,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.PROTECTED_ENVIRONMENT)


class SyntheticCandidateRegistryTests(unittest.TestCase):
    def test_registry_resolves_exact_candidate_and_snapshots_inputs(self) -> None:
        model, _, _, _, _, _ = evaluated()
        card = build_card()
        candidate = build_candidate(model=model, card=card)
        registry = SyntheticCandidateRegistry(
            candidates=(candidate,),
            cards=(card,),
            models=(model,),
            environment=ResearchEnvironment.TEST,
        )
        expected = registry.resolve("syn_ml_candidate_0001", "engineering.v1")
        object.__setattr__(candidate, "candidate_id", "mutated")

        self.assertEqual(
            registry.resolve("syn_ml_candidate_0001", "engineering.v1"),
            expected,
        )
        with self.assertRaises(AttributeError):
            object.__getattribute__(registry, "models")

    def test_registry_rejects_unknown_or_duplicate_identity(self) -> None:
        model, _, _, _, _, _ = evaluated()
        card = build_card()
        candidate = build_candidate(model=model, card=card)
        registry = SyntheticCandidateRegistry(
            candidates=(candidate,),
            cards=(card,),
            models=(model,),
            environment=ResearchEnvironment.TEST,
        )
        with self.assertRaises(ResearchBoundaryError) as unknown:
            registry.resolve("syn_ml_candidate_9999", "engineering.v1")
        self.assertIs(unknown.exception.code, ResearchBoundaryCode.UNKNOWN_IDENTITY)

        with self.assertRaises(ResearchBoundaryError) as duplicate:
            SyntheticCandidateRegistry(
                candidates=(candidate, candidate),
                cards=(card,),
                models=(model,),
                environment=ResearchEnvironment.TEST,
            )
        self.assertIs(duplicate.exception.code, ResearchBoundaryCode.DUPLICATE_IDENTITY)

    def test_registry_rejects_aliases_for_same_model_or_card(self) -> None:
        model, _, _, _, _, _ = evaluated()
        card = build_card()
        first = build_candidate(model=model, card=card)
        second = build_candidate(
            candidate_id="syn_ml_candidate_0002",
            model=model,
            card=card,
        )

        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticCandidateRegistry(
                candidates=(first, second),
                cards=(card,),
                models=(model,),
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.DUPLICATE_IDENTITY)

    def test_registry_rejects_capacity_before_reading_entries(self) -> None:
        with self.assertRaises(ResearchBoundaryError) as error:
            SyntheticCandidateRegistry(
                candidates=(HostileModel(),) * 33,  # type: ignore[arg-type]
                cards=(),
                models=(),
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, ResearchBoundaryCode.CAPACITY_EXCEEDED)

    def test_registry_and_candidate_expose_no_lifecycle_or_serialization_surface(
        self,
    ) -> None:
        model, _, _, _, _, _ = evaluated()
        card = build_card()
        candidate = build_candidate(model=model, card=card)
        registry = SyntheticCandidateRegistry(
            candidates=(candidate,),
            cards=(card,),
            models=(model,),
            environment=ResearchEnvironment.TEST,
        )

        for target in (candidate, registry):
            for name in (
                "approve",
                "promote",
                "activate",
                "register",
                "latest",
                "save",
                "load",
            ):
                with self.subTest(target=type(target).__name__, name=name):
                    self.assertFalse(hasattr(target, name))


if __name__ == "__main__":
    unittest.main()
