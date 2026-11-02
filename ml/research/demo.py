"""Offline deterministic demonstration of the synthetic P18 research mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from ml.research.baselines import (
    SyntheticBaselineKind,
    fit_synthetic_baseline,
    predict_synthetic_baseline,
    synthetic_baseline_fingerprint,
)
from ml.research.candidates import (
    SyntheticCandidateRegistry,
    SyntheticCandidateStatus,
    SyntheticCardMetric,
    SyntheticCardPurpose,
    SyntheticCardState,
    build_synthetic_model_candidate,
    build_synthetic_model_card,
    synthetic_model_candidate_fingerprint,
    synthetic_model_card_fingerprint,
)
from ml.research.contracts import (
    DatasetAdmissionState,
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    SyntheticDataClassification,
    SyntheticDatasetManifest,
    SyntheticDatasetSource,
    SyntheticLicense,
    synthetic_dataset_fingerprint,
    validate_research_environment,
)
from ml.research.pipeline import (
    MissingValuePolicy,
    ScalingPolicy,
    SyntheticClass,
    SyntheticEvaluationState,
    SyntheticExpectedLabel,
    SyntheticFeatureRow,
    SyntheticPartition,
    SyntheticPreprocessingPlan,
    SyntheticSplitConfig,
    SyntheticTransformedRow,
    build_deterministic_group_split,
    evaluate_synthetic_labels,
    fit_synthetic_preprocessor,
    synthetic_evaluation_fingerprint,
    synthetic_preprocessing_fingerprint,
    synthetic_split_fingerprint,
    transform_synthetic_partition,
)
from ml.research.registry import SyntheticDatasetRegistry

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_CANDIDATE_ID = re.compile(r"^syn_ml_candidate_[0-9]{4}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_FIXTURE_SIZE = 12
_GENERATED_AT = datetime(2026, 11, 3, 10, 0, tzinfo=UTC)
_REGISTERED_AT = datetime(2026, 11, 3, 10, 1, tzinfo=UTC)


def _error(code: ResearchBoundaryCode) -> ResearchBoundaryError:
    return ResearchBoundaryError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _count(value: object, *, positive: bool = False) -> int:
    if type(value) is not int:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if value < 0 or (positive and value == 0):
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class SyntheticDemoClaimState(StrEnum):
    NO_PERFORMANCE_OR_CLINICAL_CLAIM = "NO_PERFORMANCE_OR_CLINICAL_CLAIM"


class SyntheticDemoRuntimeState(StrEnum):
    OFFLINE_NO_EGRESS = "OFFLINE_NO_EGRESS"


class SyntheticDemoActivationState(StrEnum):
    NOT_ACTIVATED = "NOT_ACTIVATED"


def _receipt_evidence_fingerprint(
    *,
    demo_version: str,
    environment: ResearchEnvironment,
    authority: ResearchAuthority,
    data_classification: SyntheticDataClassification,
    dataset_admission_state: DatasetAdmissionState,
    missing_value_policy: MissingValuePolicy,
    scaling_policy: ScalingPolicy,
    baseline_kind: SyntheticBaselineKind,
    evaluation_state: SyntheticEvaluationState,
    card_state: SyntheticCardState,
    candidate_status: SyntheticCandidateStatus,
    card_purpose: SyntheticCardPurpose,
    card_metric: SyntheticCardMetric,
    claim_state: SyntheticDemoClaimState,
    runtime_state: SyntheticDemoRuntimeState,
    activation_state: SyntheticDemoActivationState,
    train_count: int,
    validation_count: int,
    test_count: int,
    evaluated_count: int,
    correct_count: int,
    error_count: int,
    candidate_id: str,
    candidate_version: str,
    dataset_fingerprint: str,
    split_fingerprint: str,
    preprocessing_fingerprint: str,
    model_fingerprint: str,
    evaluation_fingerprint: str,
    card_fingerprint: str,
    candidate_fingerprint: str,
) -> str:
    return _canonical_hash(
        (
            demo_version,
            environment.value,
            authority.value,
            data_classification.value,
            dataset_admission_state.value,
            missing_value_policy.value,
            scaling_policy.value,
            baseline_kind.value,
            evaluation_state.value,
            card_state.value,
            candidate_status.value,
            card_purpose.value,
            card_metric.value,
            claim_state.value,
            runtime_state.value,
            activation_state.value,
            str(train_count),
            str(validation_count),
            str(test_count),
            str(evaluated_count),
            str(correct_count),
            str(error_count),
            candidate_id,
            candidate_version,
            dataset_fingerprint,
            split_fingerprint,
            preprocessing_fingerprint,
            model_fingerprint,
            evaluation_fingerprint,
            card_fingerprint,
            candidate_fingerprint,
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticClassicalDemoReceipt:
    demo_version: str
    environment: ResearchEnvironment
    authority: ResearchAuthority
    data_classification: SyntheticDataClassification
    dataset_admission_state: DatasetAdmissionState
    missing_value_policy: MissingValuePolicy
    scaling_policy: ScalingPolicy
    baseline_kind: SyntheticBaselineKind
    evaluation_state: SyntheticEvaluationState
    card_state: SyntheticCardState
    candidate_status: SyntheticCandidateStatus
    card_purpose: SyntheticCardPurpose
    card_metric: SyntheticCardMetric
    claim_state: SyntheticDemoClaimState
    runtime_state: SyntheticDemoRuntimeState
    activation_state: SyntheticDemoActivationState
    train_count: int
    validation_count: int
    test_count: int
    evaluated_count: int
    correct_count: int
    error_count: int
    candidate_id: str
    candidate_version: str
    dataset_fingerprint: str
    split_fingerprint: str
    preprocessing_fingerprint: str
    model_fingerprint: str
    evaluation_fingerprint: str
    card_fingerprint: str
    candidate_fingerprint: str
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        _machine_string(self.demo_version, _VERSION)
        for value, expected in (
            (self.environment, ResearchEnvironment),
            (self.authority, ResearchAuthority),
            (self.data_classification, SyntheticDataClassification),
            (self.dataset_admission_state, DatasetAdmissionState),
            (self.missing_value_policy, MissingValuePolicy),
            (self.scaling_policy, ScalingPolicy),
            (self.baseline_kind, SyntheticBaselineKind),
            (self.evaluation_state, SyntheticEvaluationState),
            (self.card_state, SyntheticCardState),
            (self.candidate_status, SyntheticCandidateStatus),
            (self.card_purpose, SyntheticCardPurpose),
            (self.card_metric, SyntheticCardMetric),
            (self.claim_state, SyntheticDemoClaimState),
            (self.runtime_state, SyntheticDemoRuntimeState),
            (self.activation_state, SyntheticDemoActivationState),
        ):
            _strict_enum(value, expected)
        validate_research_environment(self.environment)
        train_count = _count(self.train_count, positive=True)
        validation_count = _count(self.validation_count, positive=True)
        test_count = _count(self.test_count, positive=True)
        evaluated_count = _count(self.evaluated_count, positive=True)
        correct_count = _count(self.correct_count)
        error_count = _count(self.error_count)
        if (
            train_count + validation_count + test_count != _FIXTURE_SIZE
            or evaluated_count != test_count
            or correct_count + error_count != evaluated_count
        ):
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        _machine_string(self.candidate_id, _CANDIDATE_ID)
        _machine_string(self.candidate_version, _VERSION)
        for fingerprint in (
            self.dataset_fingerprint,
            self.split_fingerprint,
            self.preprocessing_fingerprint,
            self.model_fingerprint,
            self.evaluation_fingerprint,
            self.card_fingerprint,
            self.candidate_fingerprint,
            self.evidence_fingerprint,
        ):
            _machine_string(fingerprint, _SHA256)
        expected_evidence = _receipt_evidence_fingerprint(
            **{
                field: getattr(self, field)
                for field in self.__dataclass_fields__
                if field != "evidence_fingerprint"
            }
        )
        if self.evidence_fingerprint != expected_evidence:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)


def validate_synthetic_classical_demo_receipt(
    value: object,
) -> SyntheticClassicalDemoReceipt:
    if type(value) is not SyntheticClassicalDemoReceipt:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticClassicalDemoReceipt(
            **{field: getattr(value, field) for field in value.__dataclass_fields__}
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def _fixture_rows() -> tuple[SyntheticFeatureRow, ...]:
    return tuple(
        SyntheticFeatureRow(
            row_id=f"syn_row_{index:04d}",
            group_id=f"syn_group_{index:04d}",
            values=(float(index), None if index % 3 == 0 else float(index * 2)),
        )
        for index in range(_FIXTURE_SIZE)
    )


def _fixture_content_hash(rows: tuple[SyntheticFeatureRow, ...]) -> str:
    fields = tuple(
        f"{row.row_id}:{row.group_id}:"
        + ",".join("missing" if value is None else value.hex() for value in row.values)
        for row in rows
    )
    return _canonical_hash(fields)


def _labels_for_rows(
    rows: tuple[SyntheticTransformedRow, ...],
) -> tuple[SyntheticExpectedLabel, ...]:
    return tuple(
        SyntheticExpectedLabel(
            row_id=row.row_id,
            label=SyntheticClass.CLASS_ALPHA if index % 2 == 0 else SyntheticClass.CLASS_BETA,
        )
        for index, row in enumerate(rows)
    )


def run_synthetic_classical_demo(
    environment: ResearchEnvironment,
) -> SyntheticClassicalDemoReceipt:
    """Replay fixed non-medical mechanics without product or clinical authority."""

    safe_environment = validate_research_environment(environment)
    rows = _fixture_rows()
    manifest = SyntheticDatasetManifest(
        dataset_id="syn_ml_dataset_alpha",
        dataset_version="engineering.v1",
        source=SyntheticDatasetSource.SYNTHETIC_GENERATED,
        classification=SyntheticDataClassification.SYNTHETIC_NON_MEDICAL,
        license=SyntheticLicense.ENGINEERING_FIXTURE_ONLY,
        admission_state=DatasetAdmissionState.TEST_ONLY_UNAPPROVED,
        content_hash=_fixture_content_hash(rows),
        schema_hash=sha256(b"synthetic-non-medical-two-float-features-v1").hexdigest(),
        schema_version="engineering.v1",
        created_at=_GENERATED_AT,
    )
    dataset_registry = SyntheticDatasetRegistry(
        manifests=(manifest,),
        environment=safe_environment,
    )
    dataset = dataset_registry.resolve(manifest.dataset_id, manifest.dataset_version)
    dataset_fingerprint = synthetic_dataset_fingerprint(dataset)
    split = build_deterministic_group_split(
        rows=rows,
        config=SyntheticSplitConfig(
            split_version="engineering.v1",
            dataset_fingerprint=dataset_fingerprint,
            seed=17,
            train_basis_points=6000,
            validation_basis_points=2000,
            test_basis_points=2000,
        ),
        environment=safe_environment,
    )
    split_fingerprint = synthetic_split_fingerprint(split)
    preprocessing = fit_synthetic_preprocessor(
        rows=rows,
        split=split,
        plan=SyntheticPreprocessingPlan(
            plan_version="engineering.v1",
            split_fingerprint=split_fingerprint,
            feature_names=("syn_feature_alpha", "syn_feature_beta"),
            missing_value_policy=MissingValuePolicy.TRAIN_MEAN,
            scaling_policy=ScalingPolicy.STANDARD_SCORE,
            fit_partition=SyntheticPartition.TRAIN,
        ),
        environment=safe_environment,
    )
    batches = {
        partition: transform_synthetic_partition(
            rows=rows,
            split=split,
            receipt=preprocessing,
            partition=partition,
            environment=safe_environment,
        )
        for partition in SyntheticPartition
    }
    training_labels = _labels_for_rows(batches[SyntheticPartition.TRAIN].rows)
    model = fit_synthetic_baseline(
        model_id="syn_ml_model_alpha",
        model_version="engineering.v1",
        kind=SyntheticBaselineKind.NEAREST_CENTROID,
        split=split,
        preprocessing=preprocessing,
        training_batch=batches[SyntheticPartition.TRAIN],
        labels=training_labels,
        tie_break_class=SyntheticClass.CLASS_ALPHA,
        environment=safe_environment,
    )
    expected = _labels_for_rows(batches[SyntheticPartition.TEST].rows)
    predicted = predict_synthetic_baseline(
        model=model,
        split=split,
        batch=batches[SyntheticPartition.TEST],
        environment=safe_environment,
    )
    evaluation = evaluate_synthetic_labels(
        expected=expected,
        predicted=predicted,
        split=split,
        preprocessing=preprocessing,
        evaluation_version="engineering.v1",
        environment=safe_environment,
    )
    card = build_synthetic_model_card(
        card_id="syn_ml_card_alpha",
        card_version="engineering.v1",
        model=model,
        split=split,
        preprocessing=preprocessing,
        test_batch=batches[SyntheticPartition.TEST],
        expected=expected,
        evaluation=evaluation,
        generated_at=_GENERATED_AT,
        environment=safe_environment,
    )
    candidate = build_synthetic_model_candidate(
        candidate_id="syn_ml_candidate_0001",
        candidate_version="engineering.v1",
        model=model,
        card=card,
        registered_at=_REGISTERED_AT,
        environment=safe_environment,
    )
    candidate_registry = SyntheticCandidateRegistry(
        candidates=(candidate,),
        cards=(card,),
        models=(model,),
        environment=safe_environment,
    )
    resolved_candidate = candidate_registry.resolve(
        candidate.candidate_id,
        candidate.candidate_version,
    )
    partition_counts = {partition: len(batches[partition].rows) for partition in SyntheticPartition}
    receipt_fields: dict[str, object] = {
        "demo_version": "engineering.v1",
        "environment": safe_environment,
        "authority": ResearchAuthority.ENGINEERING_ONLY,
        "data_classification": dataset.classification,
        "dataset_admission_state": dataset.admission_state,
        "missing_value_policy": preprocessing.missing_value_policy,
        "scaling_policy": preprocessing.scaling_policy,
        "baseline_kind": model.kind,
        "evaluation_state": evaluation.state,
        "card_state": card.state,
        "candidate_status": resolved_candidate.status,
        "card_purpose": card.purpose,
        "card_metric": card.metric,
        "claim_state": SyntheticDemoClaimState.NO_PERFORMANCE_OR_CLINICAL_CLAIM,
        "runtime_state": SyntheticDemoRuntimeState.OFFLINE_NO_EGRESS,
        "activation_state": SyntheticDemoActivationState.NOT_ACTIVATED,
        "train_count": partition_counts[SyntheticPartition.TRAIN],
        "validation_count": partition_counts[SyntheticPartition.VALIDATION],
        "test_count": partition_counts[SyntheticPartition.TEST],
        "evaluated_count": evaluation.evaluated_count,
        "correct_count": evaluation.correct_count,
        "error_count": evaluation.error_count,
        "candidate_id": resolved_candidate.candidate_id,
        "candidate_version": resolved_candidate.candidate_version,
        "dataset_fingerprint": dataset_fingerprint,
        "split_fingerprint": split_fingerprint,
        "preprocessing_fingerprint": synthetic_preprocessing_fingerprint(preprocessing),
        "model_fingerprint": synthetic_baseline_fingerprint(model),
        "evaluation_fingerprint": synthetic_evaluation_fingerprint(evaluation),
        "card_fingerprint": synthetic_model_card_fingerprint(card),
        "candidate_fingerprint": synthetic_model_candidate_fingerprint(resolved_candidate),
    }
    return SyntheticClassicalDemoReceipt(
        **receipt_fields,  # type: ignore[arg-type]
        evidence_fingerprint=_receipt_evidence_fingerprint(
            **receipt_fields,  # type: ignore[arg-type]
        ),
    )


__all__ = [
    "SyntheticClassicalDemoReceipt",
    "SyntheticDemoActivationState",
    "SyntheticDemoClaimState",
    "SyntheticDemoRuntimeState",
    "run_synthetic_classical_demo",
    "validate_synthetic_classical_demo_receipt",
]
