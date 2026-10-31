"""Closed synthetic-only candidate metadata and model-card mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from ml.research.baselines import (
    SyntheticBaselineKind,
    SyntheticBaselineModel,
    predict_synthetic_baseline,
    synthetic_baseline_fingerprint,
    validate_synthetic_baseline_model,
)
from ml.research.contracts import (
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    SyntheticDataClassification,
    validate_research_environment,
)
from ml.research.pipeline import (
    SyntheticEvaluationReceipt,
    SyntheticExpectedLabel,
    SyntheticPartition,
    SyntheticPreprocessingReceipt,
    SyntheticSplitManifest,
    SyntheticTransformedBatch,
    evaluate_synthetic_labels,
    synthetic_evaluation_fingerprint,
    synthetic_preprocessing_fingerprint,
    synthetic_split_fingerprint,
    validate_synthetic_evaluation_receipt,
    validate_synthetic_preprocessing_receipt,
    validate_synthetic_split_manifest,
    validate_synthetic_transformed_batch,
)

_CARD_ID = re.compile(r"^syn_ml_card_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


def _error(code: ResearchBoundaryCode) -> ResearchBoundaryError:
    return ResearchBoundaryError(code)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)


def _non_negative_int(value: object) -> int:
    if type(value) is not int:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if value < 0:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class SyntheticCardPurpose(StrEnum):
    ENGINEERING_DETERMINISM_ONLY = "ENGINEERING_DETERMINISM_ONLY"


class SyntheticCardMetric(StrEnum):
    EXACT_MATCH_COUNTS_ONLY = "EXACT_MATCH_COUNTS_ONLY"


class SyntheticCardLimitation(StrEnum):
    SYNTHETIC_NON_MEDICAL_ONLY = "SYNTHETIC_NON_MEDICAL_ONLY"
    NO_REAL_DATASET_EVIDENCE = "NO_REAL_DATASET_EVIDENCE"
    NO_CLINICAL_VALIDITY = "NO_CLINICAL_VALIDITY"
    NO_PATIENT_FACING_USE = "NO_PATIENT_FACING_USE"
    NO_PROMOTION_AUTHORITY = "NO_PROMOTION_AUTHORITY"


class SyntheticCardState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


REQUIRED_SYNTHETIC_LIMITATIONS = tuple(SyntheticCardLimitation)


def _card_evidence_fingerprint(
    *,
    card_id: str,
    card_version: str,
    model_id: str,
    model_version: str,
    model_fingerprint: str,
    model_kind: SyntheticBaselineKind,
    split_fingerprint: str,
    preprocessing_fingerprint: str,
    evaluation_fingerprint: str,
    evaluation_version: str,
    evaluated_count: int,
    correct_count: int,
    error_count: int,
    purpose: SyntheticCardPurpose,
    metric: SyntheticCardMetric,
    limitations: tuple[SyntheticCardLimitation, ...],
    generated_at: datetime,
    state: SyntheticCardState,
    authority: ResearchAuthority,
) -> str:
    return _canonical_hash(
        (
            card_id,
            card_version,
            model_id,
            model_version,
            model_fingerprint,
            model_kind.value,
            split_fingerprint,
            preprocessing_fingerprint,
            evaluation_fingerprint,
            evaluation_version,
            str(evaluated_count),
            str(correct_count),
            str(error_count),
            purpose.value,
            metric.value,
            *(item.value for item in limitations),
            generated_at.isoformat(),
            state.value,
            authority.value,
        )
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticModelCard:
    card_id: str
    card_version: str
    model_id: str
    model_version: str
    model_fingerprint: str
    model_kind: SyntheticBaselineKind
    data_classification: SyntheticDataClassification
    split_fingerprint: str
    preprocessing_fingerprint: str
    evaluation_fingerprint: str
    evaluation_version: str
    evaluated_count: int
    correct_count: int
    error_count: int
    purpose: SyntheticCardPurpose
    metric: SyntheticCardMetric
    limitations: tuple[SyntheticCardLimitation, ...]
    generated_at: datetime
    evidence_fingerprint: str
    state: SyntheticCardState = SyntheticCardState.TEST_ONLY_UNAPPROVED
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.card_id, _CARD_ID)
        _machine_string(self.card_version, _VERSION)
        # Model identity is fully reconstructed by the builder/validator fingerprint.
        if type(self.model_id) is not str or type(self.model_version) is not str:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        _machine_string(self.model_fingerprint, _SHA256)
        _strict_enum(self.model_kind, SyntheticBaselineKind)
        _strict_enum(self.data_classification, SyntheticDataClassification)
        if self.data_classification is not SyntheticDataClassification.SYNTHETIC_NON_MEDICAL:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        _machine_string(self.evaluation_fingerprint, _SHA256)
        _machine_string(self.evaluation_version, _VERSION)
        evaluated = _non_negative_int(self.evaluated_count)
        correct = _non_negative_int(self.correct_count)
        errors = _non_negative_int(self.error_count)
        if evaluated == 0 or correct + errors != evaluated:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        _strict_enum(self.purpose, SyntheticCardPurpose)
        _strict_enum(self.metric, SyntheticCardMetric)
        if type(self.limitations) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        for limitation in self.limitations:
            _strict_enum(limitation, SyntheticCardLimitation)
        if self.limitations != REQUIRED_SYNTHETIC_LIMITATIONS:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        generated_at = _utc(self.generated_at)
        _strict_enum(self.state, SyntheticCardState)
        _strict_enum(self.authority, ResearchAuthority)
        _machine_string(self.evidence_fingerprint, _SHA256)
        expected_evidence = _card_evidence_fingerprint(
            card_id=self.card_id,
            card_version=self.card_version,
            model_id=self.model_id,
            model_version=self.model_version,
            model_fingerprint=self.model_fingerprint,
            model_kind=self.model_kind,
            split_fingerprint=self.split_fingerprint,
            preprocessing_fingerprint=self.preprocessing_fingerprint,
            evaluation_fingerprint=self.evaluation_fingerprint,
            evaluation_version=self.evaluation_version,
            evaluated_count=evaluated,
            correct_count=correct,
            error_count=errors,
            purpose=self.purpose,
            metric=self.metric,
            limitations=self.limitations,
            generated_at=generated_at,
            state=self.state,
            authority=self.authority,
        )
        if self.evidence_fingerprint != expected_evidence:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        object.__setattr__(self, "generated_at", generated_at)


def validate_synthetic_model_card(value: object) -> SyntheticModelCard:
    if type(value) is not SyntheticModelCard:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticModelCard(
            card_id=value.card_id,
            card_version=value.card_version,
            model_id=value.model_id,
            model_version=value.model_version,
            model_fingerprint=value.model_fingerprint,
            model_kind=value.model_kind,
            data_classification=value.data_classification,
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            evaluation_fingerprint=value.evaluation_fingerprint,
            evaluation_version=value.evaluation_version,
            evaluated_count=value.evaluated_count,
            correct_count=value.correct_count,
            error_count=value.error_count,
            purpose=value.purpose,
            metric=value.metric,
            limitations=value.limitations,
            generated_at=value.generated_at,
            evidence_fingerprint=value.evidence_fingerprint,
            state=value.state,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_model_card_fingerprint(value: SyntheticModelCard) -> str:
    card = validate_synthetic_model_card(value)
    return _canonical_hash((card.evidence_fingerprint, card.data_classification.value))


def build_synthetic_model_card(
    *,
    card_id: str,
    card_version: str,
    model: SyntheticBaselineModel,
    split: SyntheticSplitManifest,
    preprocessing: SyntheticPreprocessingReceipt,
    test_batch: SyntheticTransformedBatch,
    expected: tuple[SyntheticExpectedLabel, ...],
    evaluation: SyntheticEvaluationReceipt,
    generated_at: datetime,
    environment: ResearchEnvironment,
) -> SyntheticModelCard:
    validate_research_environment(environment)
    safe_model = validate_synthetic_baseline_model(model)
    safe_split = validate_synthetic_split_manifest(split)
    safe_preprocessing = validate_synthetic_preprocessing_receipt(preprocessing)
    safe_batch = validate_synthetic_transformed_batch(test_batch)
    safe_evaluation = validate_synthetic_evaluation_receipt(evaluation)
    _machine_string(card_id, _CARD_ID)
    _machine_string(card_version, _VERSION)
    normalized_time = _utc(generated_at)
    split_fingerprint = synthetic_split_fingerprint(safe_split)
    preprocessing_fingerprint = synthetic_preprocessing_fingerprint(safe_preprocessing)
    if (
        safe_batch.partition is not SyntheticPartition.TEST
        or safe_model.split_fingerprint != split_fingerprint
        or safe_model.preprocessing_fingerprint != preprocessing_fingerprint
        or safe_preprocessing.split_fingerprint != split_fingerprint
        or safe_batch.split_fingerprint != split_fingerprint
        or safe_batch.preprocessing_fingerprint != preprocessing_fingerprint
    ):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    predictions = predict_synthetic_baseline(
        model=safe_model,
        split=safe_split,
        batch=safe_batch,
        environment=environment,
    )
    reproduced = evaluate_synthetic_labels(
        expected=expected,
        predicted=predictions,
        split=safe_split,
        preprocessing=safe_preprocessing,
        evaluation_version=safe_evaluation.evaluation_version,
        environment=environment,
    )
    if synthetic_evaluation_fingerprint(reproduced) != synthetic_evaluation_fingerprint(
        safe_evaluation
    ):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    model_fingerprint = synthetic_baseline_fingerprint(safe_model)
    purpose = SyntheticCardPurpose.ENGINEERING_DETERMINISM_ONLY
    metric = SyntheticCardMetric.EXACT_MATCH_COUNTS_ONLY
    state = SyntheticCardState.TEST_ONLY_UNAPPROVED
    authority = ResearchAuthority.ENGINEERING_ONLY
    evidence_fingerprint = _card_evidence_fingerprint(
        card_id=card_id,
        card_version=card_version,
        model_id=safe_model.model_id,
        model_version=safe_model.model_version,
        model_fingerprint=model_fingerprint,
        model_kind=safe_model.kind,
        split_fingerprint=split_fingerprint,
        preprocessing_fingerprint=preprocessing_fingerprint,
        evaluation_fingerprint=synthetic_evaluation_fingerprint(reproduced),
        evaluation_version=reproduced.evaluation_version,
        evaluated_count=reproduced.evaluated_count,
        correct_count=reproduced.correct_count,
        error_count=reproduced.error_count,
        purpose=purpose,
        metric=metric,
        limitations=REQUIRED_SYNTHETIC_LIMITATIONS,
        generated_at=normalized_time,
        state=state,
        authority=authority,
    )
    return SyntheticModelCard(
        card_id=card_id,
        card_version=card_version,
        model_id=safe_model.model_id,
        model_version=safe_model.model_version,
        model_fingerprint=model_fingerprint,
        model_kind=safe_model.kind,
        data_classification=SyntheticDataClassification.SYNTHETIC_NON_MEDICAL,
        split_fingerprint=split_fingerprint,
        preprocessing_fingerprint=preprocessing_fingerprint,
        evaluation_fingerprint=synthetic_evaluation_fingerprint(reproduced),
        evaluation_version=reproduced.evaluation_version,
        evaluated_count=reproduced.evaluated_count,
        correct_count=reproduced.correct_count,
        error_count=reproduced.error_count,
        purpose=purpose,
        metric=metric,
        limitations=REQUIRED_SYNTHETIC_LIMITATIONS,
        generated_at=normalized_time,
        evidence_fingerprint=evidence_fingerprint,
        state=state,
        authority=authority,
    )


__all__ = [
    "REQUIRED_SYNTHETIC_LIMITATIONS",
    "SyntheticCardLimitation",
    "SyntheticCardMetric",
    "SyntheticCardPurpose",
    "SyntheticCardState",
    "SyntheticModelCard",
    "build_synthetic_model_card",
    "synthetic_model_card_fingerprint",
    "validate_synthetic_model_card",
]
