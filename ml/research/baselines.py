"""Transparent deterministic baseline mechanics for synthetic P18-C fixtures only."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from ml.research.contracts import (
    ResearchAuthority,
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    validate_research_environment,
)
from ml.research.pipeline import (
    SyntheticClass,
    SyntheticExpectedLabel,
    SyntheticPartition,
    SyntheticPredictedLabel,
    SyntheticPreprocessingReceipt,
    SyntheticSplitManifest,
    SyntheticTransformedBatch,
    synthetic_preprocessing_fingerprint,
    synthetic_split_fingerprint,
    validate_synthetic_preprocessing_receipt,
    validate_synthetic_split_manifest,
    validate_synthetic_transformed_batch,
)

_MODEL_ID = re.compile(r"^syn_ml_model_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_MAX_FEATURES = 4


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


def _positive_int(value: object) -> int:
    if type(value) is not int:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if value <= 0:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _finite_tuple(value: object, *, expected_size: int) -> tuple[float, ...]:
    if type(value) is not tuple:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if len(value) != expected_size:
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    for item in value:
        if type(item) is not float:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not math.isfinite(item):
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class SyntheticBaselineKind(StrEnum):
    MAJORITY_CLASS = "MAJORITY_CLASS"
    NEAREST_CENTROID = "NEAREST_CENTROID"


class SyntheticBaselineState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticBaselineModel:
    model_id: str
    model_version: str
    kind: SyntheticBaselineKind
    split_fingerprint: str
    preprocessing_fingerprint: str
    feature_count: int
    training_row_count: int
    training_membership_hash: str
    training_label_fingerprint: str
    class_alpha_count: int
    class_beta_count: int
    tie_break_class: SyntheticClass
    majority_class: SyntheticClass
    class_alpha_centroid: tuple[float, ...]
    class_beta_centroid: tuple[float, ...]
    state: SyntheticBaselineState = SyntheticBaselineState.TEST_ONLY_UNAPPROVED
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.model_id, _MODEL_ID)
        _machine_string(self.model_version, _VERSION)
        _strict_enum(self.kind, SyntheticBaselineKind)
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        feature_count = _positive_int(self.feature_count)
        if feature_count > _MAX_FEATURES:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        training_row_count = _positive_int(self.training_row_count)
        _machine_string(self.training_membership_hash, _SHA256)
        _machine_string(self.training_label_fingerprint, _SHA256)
        alpha_count = _positive_int(self.class_alpha_count)
        beta_count = _positive_int(self.class_beta_count)
        if alpha_count + beta_count != training_row_count:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        _strict_enum(self.tie_break_class, SyntheticClass)
        _strict_enum(self.majority_class, SyntheticClass)
        expected_majority = (
            SyntheticClass.CLASS_ALPHA
            if alpha_count > beta_count
            else SyntheticClass.CLASS_BETA
            if beta_count > alpha_count
            else self.tie_break_class
        )
        if self.majority_class is not expected_majority:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        if self.kind is SyntheticBaselineKind.MAJORITY_CLASS:
            alpha_centroid = _finite_tuple(self.class_alpha_centroid, expected_size=0)
            beta_centroid = _finite_tuple(self.class_beta_centroid, expected_size=0)
        else:
            alpha_centroid = _finite_tuple(self.class_alpha_centroid, expected_size=feature_count)
            beta_centroid = _finite_tuple(self.class_beta_centroid, expected_size=feature_count)
        _strict_enum(self.state, SyntheticBaselineState)
        _strict_enum(self.authority, ResearchAuthority)
        object.__setattr__(self, "class_alpha_centroid", alpha_centroid)
        object.__setattr__(self, "class_beta_centroid", beta_centroid)


def validate_synthetic_baseline_model(value: object) -> SyntheticBaselineModel:
    if type(value) is not SyntheticBaselineModel:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticBaselineModel(
            model_id=value.model_id,
            model_version=value.model_version,
            kind=value.kind,
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            feature_count=value.feature_count,
            training_row_count=value.training_row_count,
            training_membership_hash=value.training_membership_hash,
            training_label_fingerprint=value.training_label_fingerprint,
            class_alpha_count=value.class_alpha_count,
            class_beta_count=value.class_beta_count,
            tie_break_class=value.tie_break_class,
            majority_class=value.majority_class,
            class_alpha_centroid=value.class_alpha_centroid,
            class_beta_centroid=value.class_beta_centroid,
            state=value.state,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_baseline_fingerprint(value: SyntheticBaselineModel) -> str:
    model = validate_synthetic_baseline_model(value)
    fields = (
        model.model_id,
        model.model_version,
        model.kind.value,
        model.split_fingerprint,
        model.preprocessing_fingerprint,
        str(model.feature_count),
        str(model.training_row_count),
        model.training_membership_hash,
        model.training_label_fingerprint,
        str(model.class_alpha_count),
        str(model.class_beta_count),
        model.tie_break_class.value,
        model.majority_class.value,
        *(repr(value) for value in model.class_alpha_centroid),
        *(repr(value) for value in model.class_beta_centroid),
        model.state.value,
        model.authority.value,
    )
    return _canonical_hash(fields)


def _training_labels(value: object) -> dict[str, SyntheticClass]:
    if type(value) is not tuple:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    labels: dict[str, SyntheticClass] = {}
    for item in value:
        if type(item) is not SyntheticExpectedLabel:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        try:
            snapshot = SyntheticExpectedLabel(row_id=item.row_id, label=item.label)
        except ResearchBoundaryError:
            raise
        except (AttributeError, TypeError, ValueError):
            raise _error(ResearchBoundaryCode.INVALID_TYPE) from None
        if snapshot.row_id in labels:
            raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
        labels[snapshot.row_id] = snapshot.label
    return labels


def _verify_batch_membership(
    batch: SyntheticTransformedBatch, split: SyntheticSplitManifest
) -> None:
    expected_ids = tuple(
        item.row_id for item in split.assignments if item.partition is batch.partition
    )
    if tuple(row.row_id for row in batch.rows) != expected_ids:
        raise _error(ResearchBoundaryCode.PARTITION_MISMATCH)


def _centroid(rows: tuple[tuple[float, ...], ...], *, feature_count: int) -> tuple[float, ...]:
    if not rows:
        raise _error(ResearchBoundaryCode.DEGENERATE_EVALUATION)
    try:
        centroid = tuple(
            float(math.fsum(row[index] for row in rows) / len(rows))
            for index in range(feature_count)
        )
    except OverflowError:
        raise _error(ResearchBoundaryCode.INVALID_VALUE) from None
    if not all(math.isfinite(value) for value in centroid):
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return centroid


def fit_synthetic_baseline(
    *,
    model_id: str,
    model_version: str,
    kind: SyntheticBaselineKind,
    split: SyntheticSplitManifest,
    preprocessing: SyntheticPreprocessingReceipt,
    training_batch: SyntheticTransformedBatch,
    labels: tuple[SyntheticExpectedLabel, ...],
    tie_break_class: SyntheticClass,
    environment: ResearchEnvironment,
) -> SyntheticBaselineModel:
    validate_research_environment(environment)
    safe_split = validate_synthetic_split_manifest(split)
    safe_preprocessing = validate_synthetic_preprocessing_receipt(preprocessing)
    safe_batch = validate_synthetic_transformed_batch(training_batch)
    _strict_enum(kind, SyntheticBaselineKind)
    _strict_enum(tie_break_class, SyntheticClass)
    _machine_string(model_id, _MODEL_ID)
    _machine_string(model_version, _VERSION)
    if safe_batch.partition is not SyntheticPartition.TRAIN:
        raise _error(ResearchBoundaryCode.LEAKAGE_DETECTED)
    split_fingerprint = synthetic_split_fingerprint(safe_split)
    if (
        safe_preprocessing.split_fingerprint != split_fingerprint
        or safe_batch.split_fingerprint != split_fingerprint
        or safe_batch.preprocessing_fingerprint
        != synthetic_preprocessing_fingerprint(safe_preprocessing)
    ):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    _verify_batch_membership(safe_batch, safe_split)
    labels_by_id = _training_labels(labels)
    training_ids = tuple(row.row_id for row in safe_batch.rows)
    if set(labels_by_id) != set(training_ids):
        raise _error(ResearchBoundaryCode.PARTITION_MISMATCH)
    alpha_ids = tuple(
        row_id for row_id in training_ids if labels_by_id[row_id] is SyntheticClass.CLASS_ALPHA
    )
    beta_ids = tuple(
        row_id for row_id in training_ids if labels_by_id[row_id] is SyntheticClass.CLASS_BETA
    )
    if not alpha_ids or not beta_ids:
        raise _error(ResearchBoundaryCode.DEGENERATE_EVALUATION)
    rows_by_id = {row.row_id: row.values for row in safe_batch.rows}
    feature_count = len(safe_batch.rows[0].values)
    majority_class = (
        SyntheticClass.CLASS_ALPHA
        if len(alpha_ids) > len(beta_ids)
        else SyntheticClass.CLASS_BETA
        if len(beta_ids) > len(alpha_ids)
        else tie_break_class
    )
    if kind is SyntheticBaselineKind.NEAREST_CENTROID:
        alpha_centroid = _centroid(
            tuple(rows_by_id[row_id] for row_id in alpha_ids),
            feature_count=feature_count,
        )
        beta_centroid = _centroid(
            tuple(rows_by_id[row_id] for row_id in beta_ids),
            feature_count=feature_count,
        )
    else:
        alpha_centroid = ()
        beta_centroid = ()
    return SyntheticBaselineModel(
        model_id=model_id,
        model_version=model_version,
        kind=kind,
        split_fingerprint=split_fingerprint,
        preprocessing_fingerprint=safe_batch.preprocessing_fingerprint,
        feature_count=feature_count,
        training_row_count=len(training_ids),
        training_membership_hash=_canonical_hash(tuple(sorted(training_ids))),
        training_label_fingerprint=_canonical_hash(
            tuple(f"{row_id}:{labels_by_id[row_id].value}" for row_id in sorted(training_ids))
        ),
        class_alpha_count=len(alpha_ids),
        class_beta_count=len(beta_ids),
        tie_break_class=tie_break_class,
        majority_class=majority_class,
        class_alpha_centroid=alpha_centroid,
        class_beta_centroid=beta_centroid,
    )


def _squared_distance(values: tuple[float, ...], centroid: tuple[float, ...]) -> float:
    try:
        distance = math.fsum(
            (value - center) ** 2 for value, center in zip(values, centroid, strict=True)
        )
    except OverflowError:
        raise _error(ResearchBoundaryCode.INVALID_VALUE) from None
    if not math.isfinite(distance):
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return distance


def predict_synthetic_baseline(
    *,
    model: SyntheticBaselineModel,
    split: SyntheticSplitManifest,
    batch: SyntheticTransformedBatch,
    environment: ResearchEnvironment,
) -> tuple[SyntheticPredictedLabel, ...]:
    validate_research_environment(environment)
    safe_model = validate_synthetic_baseline_model(model)
    safe_split = validate_synthetic_split_manifest(split)
    safe_batch = validate_synthetic_transformed_batch(batch)
    if safe_batch.partition is SyntheticPartition.TRAIN:
        raise _error(ResearchBoundaryCode.LEAKAGE_DETECTED)
    split_fingerprint = synthetic_split_fingerprint(safe_split)
    if (
        safe_model.split_fingerprint != split_fingerprint
        or safe_batch.split_fingerprint != split_fingerprint
        or safe_batch.preprocessing_fingerprint != safe_model.preprocessing_fingerprint
    ):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    _verify_batch_membership(safe_batch, safe_split)
    if any(len(row.values) != safe_model.feature_count for row in safe_batch.rows):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    predictions: list[SyntheticPredictedLabel] = []
    for row in safe_batch.rows:
        if safe_model.kind is SyntheticBaselineKind.MAJORITY_CLASS:
            label = safe_model.majority_class
        else:
            alpha_distance = _squared_distance(row.values, safe_model.class_alpha_centroid)
            beta_distance = _squared_distance(row.values, safe_model.class_beta_centroid)
            label = (
                SyntheticClass.CLASS_ALPHA
                if alpha_distance < beta_distance
                else SyntheticClass.CLASS_BETA
                if beta_distance < alpha_distance
                else safe_model.tie_break_class
            )
        predictions.append(SyntheticPredictedLabel(row_id=row.row_id, label=label))
    return tuple(predictions)


__all__ = [
    "SyntheticBaselineKind",
    "SyntheticBaselineModel",
    "SyntheticBaselineState",
    "fit_synthetic_baseline",
    "predict_synthetic_baseline",
    "synthetic_baseline_fingerprint",
    "validate_synthetic_baseline_model",
]
