"""Deterministic synthetic-only split, preprocessing, and evaluation mechanics."""

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

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_ROW_ID = re.compile(r"^syn_row_[0-9]{4}$")
_GROUP_ID = re.compile(r"^syn_group_[0-9]{4}$")
_FEATURE_NAME = re.compile(r"^syn_feature_(?:alpha|beta|gamma|delta)$")
_MAX_ROWS = 256
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


def _uint32(value: object) -> int:
    if type(value) is not int:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if not 0 <= value < 2**32:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _positive_int(value: object) -> int:
    if type(value) is not int:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if value <= 0:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _finite_float(value: object, *, positive: bool = False) -> float:
    if type(value) is not float:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if not math.isfinite(value) or (positive and value <= 0.0):
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _canonical_hash(fields: tuple[str, ...]) -> str:
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


class SyntheticPartition(StrEnum):
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    TEST = "TEST"


class MissingValuePolicy(StrEnum):
    TRAIN_MEAN = "TRAIN_MEAN"


class ScalingPolicy(StrEnum):
    STANDARD_SCORE = "STANDARD_SCORE"


class SyntheticClass(StrEnum):
    CLASS_ALPHA = "CLASS_ALPHA"
    CLASS_BETA = "CLASS_BETA"


class SyntheticEvaluationState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFeatureRow:
    row_id: str
    group_id: str
    values: tuple[float | None, ...]

    def __post_init__(self) -> None:
        _machine_string(self.row_id, _ROW_ID)
        _machine_string(self.group_id, _GROUP_ID)
        if type(self.values) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not 1 <= len(self.values) <= _MAX_FEATURES:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        for value in self.values:
            if value is not None:
                _finite_float(value)


def _validate_feature_row(value: object) -> SyntheticFeatureRow:
    if type(value) is not SyntheticFeatureRow:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticFeatureRow(
            row_id=value.row_id,
            group_id=value.group_id,
            values=value.values,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSplitConfig:
    split_version: str
    dataset_fingerprint: str
    seed: int
    train_basis_points: int
    validation_basis_points: int
    test_basis_points: int
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.split_version, _VERSION)
        _machine_string(self.dataset_fingerprint, _SHA256)
        _uint32(self.seed)
        ratios = (
            _positive_int(self.train_basis_points),
            _positive_int(self.validation_basis_points),
            _positive_int(self.test_basis_points),
        )
        if sum(ratios) != 10_000:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        _strict_enum(self.authority, ResearchAuthority)


def _validate_split_config(value: object) -> SyntheticSplitConfig:
    if type(value) is not SyntheticSplitConfig:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticSplitConfig(
            split_version=value.split_version,
            dataset_fingerprint=value.dataset_fingerprint,
            seed=value.seed,
            train_basis_points=value.train_basis_points,
            validation_basis_points=value.validation_basis_points,
            test_basis_points=value.test_basis_points,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPartitionAssignment:
    row_id: str
    group_id: str
    partition: SyntheticPartition

    def __post_init__(self) -> None:
        _machine_string(self.row_id, _ROW_ID)
        _machine_string(self.group_id, _GROUP_ID)
        _strict_enum(self.partition, SyntheticPartition)


def _validate_assignment(value: object) -> SyntheticPartitionAssignment:
    if type(value) is not SyntheticPartitionAssignment:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticPartitionAssignment(
            row_id=value.row_id,
            group_id=value.group_id,
            partition=value.partition,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSplitManifest:
    split_version: str
    dataset_fingerprint: str
    seed: int
    train_basis_points: int
    validation_basis_points: int
    test_basis_points: int
    assignments: tuple[SyntheticPartitionAssignment, ...]
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.split_version, _VERSION)
        _machine_string(self.dataset_fingerprint, _SHA256)
        _uint32(self.seed)
        ratios = (
            _positive_int(self.train_basis_points),
            _positive_int(self.validation_basis_points),
            _positive_int(self.test_basis_points),
        )
        if sum(ratios) != 10_000:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        if type(self.assignments) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not 3 <= len(self.assignments) <= _MAX_ROWS:
            raise _error(ResearchBoundaryCode.INCOMPLETE_PARTITION)
        snapshots = tuple(_validate_assignment(item) for item in self.assignments)
        if tuple(sorted(snapshots, key=lambda item: item.row_id)) != snapshots:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        row_ids: set[str] = set()
        group_partitions: dict[str, SyntheticPartition] = {}
        present: set[SyntheticPartition] = set()
        for item in snapshots:
            if item.row_id in row_ids:
                raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
            row_ids.add(item.row_id)
            existing = group_partitions.setdefault(item.group_id, item.partition)
            if existing is not item.partition:
                raise _error(ResearchBoundaryCode.LEAKAGE_DETECTED)
            present.add(item.partition)
        if present != set(SyntheticPartition):
            raise _error(ResearchBoundaryCode.INCOMPLETE_PARTITION)
        _strict_enum(self.authority, ResearchAuthority)
        object.__setattr__(self, "assignments", snapshots)


def validate_synthetic_split_manifest(value: object) -> SyntheticSplitManifest:
    if type(value) is not SyntheticSplitManifest:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticSplitManifest(
            split_version=value.split_version,
            dataset_fingerprint=value.dataset_fingerprint,
            seed=value.seed,
            train_basis_points=value.train_basis_points,
            validation_basis_points=value.validation_basis_points,
            test_basis_points=value.test_basis_points,
            assignments=value.assignments,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_split_fingerprint(value: SyntheticSplitManifest) -> str:
    manifest = validate_synthetic_split_manifest(value)
    fields = [
        manifest.split_version,
        manifest.dataset_fingerprint,
        str(manifest.seed),
        str(manifest.train_basis_points),
        str(manifest.validation_basis_points),
        str(manifest.test_basis_points),
        manifest.authority.value,
    ]
    fields.extend(
        f"{item.row_id}:{item.group_id}:{item.partition.value}" for item in manifest.assignments
    )
    return _canonical_hash(tuple(fields))


def _snapshot_rows(value: object) -> tuple[SyntheticFeatureRow, ...]:
    if type(value) is not tuple:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if not 3 <= len(value) <= _MAX_ROWS:
        raise _error(ResearchBoundaryCode.INCOMPLETE_INPUT)
    rows = tuple(_validate_feature_row(item) for item in value)
    widths = {len(row.values) for row in rows}
    if len(widths) != 1:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    if len({row.row_id for row in rows}) != len(rows):
        raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
    return rows


def build_deterministic_group_split(
    *,
    rows: tuple[SyntheticFeatureRow, ...],
    config: SyntheticSplitConfig,
    environment: ResearchEnvironment,
) -> SyntheticSplitManifest:
    validate_research_environment(environment)
    split_config = _validate_split_config(config)
    snapshots = _snapshot_rows(rows)
    groups = sorted({row.group_id for row in snapshots})
    if len(groups) < 3:
        raise _error(ResearchBoundaryCode.INCOMPLETE_PARTITION)
    ranked = sorted(
        groups,
        key=lambda group_id: _canonical_hash((str(split_config.seed), group_id)),
    )
    ratios = (
        split_config.train_basis_points,
        split_config.validation_basis_points,
        split_config.test_basis_points,
    )
    numerators = tuple(len(ranked) * ratio for ratio in ratios)
    counts = [max(1, numerator // 10_000) for numerator in numerators]
    deficit = len(ranked) - sum(counts)
    remainder_order = sorted(range(3), key=lambda item: (-(numerators[item] % 10_000), item))
    if deficit > len(remainder_order):
        raise _error(ResearchBoundaryCode.INCOMPLETE_PARTITION)
    for index in remainder_order[: max(0, deficit)]:
        counts[index] += 1
    while sum(counts) > len(ranked):
        candidates = tuple(index for index, count in enumerate(counts) if count > 1)
        if not candidates:
            raise _error(ResearchBoundaryCode.INCOMPLETE_PARTITION)
        index = max(candidates, key=lambda item: (counts[item], -ratios[item], -item))
        counts[index] -= 1
    train_count, validation_count, _ = counts
    partition_by_group = {
        group_id: (
            SyntheticPartition.TRAIN
            if index < train_count
            else SyntheticPartition.VALIDATION
            if index < train_count + validation_count
            else SyntheticPartition.TEST
        )
        for index, group_id in enumerate(ranked)
    }
    assignments = tuple(
        SyntheticPartitionAssignment(
            row_id=row.row_id,
            group_id=row.group_id,
            partition=partition_by_group[row.group_id],
        )
        for row in sorted(snapshots, key=lambda item: item.row_id)
    )
    return SyntheticSplitManifest(
        split_version=split_config.split_version,
        dataset_fingerprint=split_config.dataset_fingerprint,
        seed=split_config.seed,
        train_basis_points=split_config.train_basis_points,
        validation_basis_points=split_config.validation_basis_points,
        test_basis_points=split_config.test_basis_points,
        assignments=assignments,
        authority=split_config.authority,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPreprocessingPlan:
    plan_version: str
    split_fingerprint: str
    feature_names: tuple[str, ...]
    missing_value_policy: MissingValuePolicy
    scaling_policy: ScalingPolicy
    fit_partition: SyntheticPartition
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.split_fingerprint, _SHA256)
        if type(self.feature_names) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not 1 <= len(self.feature_names) <= _MAX_FEATURES:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        for name in self.feature_names:
            _machine_string(name, _FEATURE_NAME)
        if len(set(self.feature_names)) != len(self.feature_names):
            raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
        _strict_enum(self.missing_value_policy, MissingValuePolicy)
        _strict_enum(self.scaling_policy, ScalingPolicy)
        _strict_enum(self.fit_partition, SyntheticPartition)
        if self.fit_partition is not SyntheticPartition.TRAIN:
            raise _error(ResearchBoundaryCode.LEAKAGE_DETECTED)
        _strict_enum(self.authority, ResearchAuthority)


def _validate_plan(value: object) -> SyntheticPreprocessingPlan:
    if type(value) is not SyntheticPreprocessingPlan:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticPreprocessingPlan(
            plan_version=value.plan_version,
            split_fingerprint=value.split_fingerprint,
            feature_names=value.feature_names,
            missing_value_policy=value.missing_value_policy,
            scaling_policy=value.scaling_policy,
            fit_partition=value.fit_partition,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFeatureStatistics:
    feature_name: str
    mean: float
    scale: float
    observed_count: int
    missing_count: int

    def __post_init__(self) -> None:
        _machine_string(self.feature_name, _FEATURE_NAME)
        _finite_float(self.mean)
        _finite_float(self.scale, positive=True)
        _positive_int(self.observed_count)
        if type(self.missing_count) is not int:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if self.missing_count < 0:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)


def _validate_statistics(value: object) -> SyntheticFeatureStatistics:
    if type(value) is not SyntheticFeatureStatistics:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticFeatureStatistics(
            feature_name=value.feature_name,
            mean=value.mean,
            scale=value.scale,
            observed_count=value.observed_count,
            missing_count=value.missing_count,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPreprocessingReceipt:
    plan_version: str
    split_fingerprint: str
    feature_names: tuple[str, ...]
    missing_value_policy: MissingValuePolicy
    scaling_policy: ScalingPolicy
    fit_partition: SyntheticPartition
    fit_membership_hash: str
    fit_row_count: int
    statistics: tuple[SyntheticFeatureStatistics, ...]
    state: SyntheticEvaluationState = SyntheticEvaluationState.TEST_ONLY_UNAPPROVED
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        plan = SyntheticPreprocessingPlan(
            plan_version=self.plan_version,
            split_fingerprint=self.split_fingerprint,
            feature_names=self.feature_names,
            missing_value_policy=self.missing_value_policy,
            scaling_policy=self.scaling_policy,
            fit_partition=self.fit_partition,
            authority=self.authority,
        )
        _machine_string(self.fit_membership_hash, _SHA256)
        _positive_int(self.fit_row_count)
        if type(self.statistics) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        statistics = tuple(_validate_statistics(item) for item in self.statistics)
        if tuple(item.feature_name for item in statistics) != plan.feature_names:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        for item in statistics:
            if item.observed_count + item.missing_count != self.fit_row_count:
                raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        _strict_enum(self.state, SyntheticEvaluationState)
        object.__setattr__(self, "statistics", statistics)


def _validate_preprocessing_receipt(value: object) -> SyntheticPreprocessingReceipt:
    if type(value) is not SyntheticPreprocessingReceipt:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticPreprocessingReceipt(
            plan_version=value.plan_version,
            split_fingerprint=value.split_fingerprint,
            feature_names=value.feature_names,
            missing_value_policy=value.missing_value_policy,
            scaling_policy=value.scaling_policy,
            fit_partition=value.fit_partition,
            fit_membership_hash=value.fit_membership_hash,
            fit_row_count=value.fit_row_count,
            statistics=value.statistics,
            state=value.state,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def validate_synthetic_preprocessing_receipt(value: object) -> SyntheticPreprocessingReceipt:
    return _validate_preprocessing_receipt(value)


def synthetic_preprocessing_fingerprint(value: SyntheticPreprocessingReceipt) -> str:
    receipt = _validate_preprocessing_receipt(value)
    fields = [
        receipt.plan_version,
        receipt.split_fingerprint,
        *receipt.feature_names,
        receipt.missing_value_policy.value,
        receipt.scaling_policy.value,
        receipt.fit_partition.value,
        receipt.fit_membership_hash,
        str(receipt.fit_row_count),
        receipt.state.value,
        receipt.authority.value,
    ]
    fields.extend(
        f"{item.feature_name}:{item.mean!r}:{item.scale!r}:{item.observed_count}:{item.missing_count}"
        for item in receipt.statistics
    )
    return _canonical_hash(tuple(fields))


def _rows_by_id_for_split(
    rows: object, split: SyntheticSplitManifest
) -> dict[str, SyntheticFeatureRow]:
    snapshots = _snapshot_rows(rows)
    by_id = {row.row_id: row for row in snapshots}
    assignment_ids = {item.row_id for item in split.assignments}
    if set(by_id) != assignment_ids:
        raise _error(ResearchBoundaryCode.PARTITION_MISMATCH)
    for item in split.assignments:
        if by_id[item.row_id].group_id != item.group_id:
            raise _error(ResearchBoundaryCode.PARTITION_MISMATCH)
    return by_id


def fit_synthetic_preprocessor(
    *,
    rows: tuple[SyntheticFeatureRow, ...],
    split: SyntheticSplitManifest,
    plan: SyntheticPreprocessingPlan,
    environment: ResearchEnvironment,
) -> SyntheticPreprocessingReceipt:
    validate_research_environment(environment)
    safe_split = validate_synthetic_split_manifest(split)
    safe_plan = _validate_plan(plan)
    if safe_plan.split_fingerprint != synthetic_split_fingerprint(safe_split):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    by_id = _rows_by_id_for_split(rows, safe_split)
    if len(next(iter(by_id.values())).values) != len(safe_plan.feature_names):
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    train_ids = tuple(
        item.row_id for item in safe_split.assignments if item.partition is SyntheticPartition.TRAIN
    )
    statistics: list[SyntheticFeatureStatistics] = []
    for index, name in enumerate(safe_plan.feature_names):
        observed = tuple(
            value for row_id in train_ids if (value := by_id[row_id].values[index]) is not None
        )
        if not observed:
            raise _error(ResearchBoundaryCode.INCOMPLETE_INPUT)
        mean = math.fsum(observed) / len(observed)
        variance = math.fsum((value - mean) ** 2 for value in observed) / len(observed)
        scale = math.sqrt(variance) or 1.0
        statistics.append(
            SyntheticFeatureStatistics(
                feature_name=name,
                mean=float(mean),
                scale=float(scale),
                observed_count=len(observed),
                missing_count=len(train_ids) - len(observed),
            )
        )
    return SyntheticPreprocessingReceipt(
        plan_version=safe_plan.plan_version,
        split_fingerprint=safe_plan.split_fingerprint,
        feature_names=safe_plan.feature_names,
        missing_value_policy=safe_plan.missing_value_policy,
        scaling_policy=safe_plan.scaling_policy,
        fit_partition=safe_plan.fit_partition,
        fit_membership_hash=_canonical_hash(tuple(sorted(train_ids))),
        fit_row_count=len(train_ids),
        statistics=tuple(statistics),
        authority=safe_plan.authority,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticTransformedRow:
    row_id: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        _machine_string(self.row_id, _ROW_ID)
        if type(self.values) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not 1 <= len(self.values) <= _MAX_FEATURES:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        for value in self.values:
            _finite_float(value)


def _validate_transformed_row(value: object) -> SyntheticTransformedRow:
    if type(value) is not SyntheticTransformedRow:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticTransformedRow(row_id=value.row_id, values=value.values)
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticTransformedBatch:
    split_fingerprint: str
    preprocessing_fingerprint: str
    partition: SyntheticPartition
    rows: tuple[SyntheticTransformedRow, ...]

    def __post_init__(self) -> None:
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        _strict_enum(self.partition, SyntheticPartition)
        if type(self.rows) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not self.rows:
            raise _error(ResearchBoundaryCode.INCOMPLETE_INPUT)
        rows = tuple(_validate_transformed_row(item) for item in self.rows)
        if tuple(sorted(rows, key=lambda item: item.row_id)) != rows:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        if len({row.row_id for row in rows}) != len(rows):
            raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
        if len({len(row.values) for row in rows}) != 1:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        object.__setattr__(self, "rows", rows)


def validate_synthetic_transformed_batch(value: object) -> SyntheticTransformedBatch:
    if type(value) is not SyntheticTransformedBatch:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticTransformedBatch(
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            partition=value.partition,
            rows=value.rows,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def transform_synthetic_partition(
    *,
    rows: tuple[SyntheticFeatureRow, ...],
    split: SyntheticSplitManifest,
    receipt: SyntheticPreprocessingReceipt,
    partition: SyntheticPartition,
    environment: ResearchEnvironment,
) -> SyntheticTransformedBatch:
    validate_research_environment(environment)
    safe_split = validate_synthetic_split_manifest(split)
    safe_receipt = _validate_preprocessing_receipt(receipt)
    _strict_enum(partition, SyntheticPartition)
    split_fingerprint = synthetic_split_fingerprint(safe_split)
    if safe_receipt.split_fingerprint != split_fingerprint:
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    by_id = _rows_by_id_for_split(rows, safe_split)
    selected_ids = tuple(
        item.row_id for item in safe_split.assignments if item.partition is partition
    )
    transformed: list[SyntheticTransformedRow] = []
    for row_id in selected_ids:
        row = by_id[row_id]
        if len(row.values) != len(safe_receipt.statistics):
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        values = tuple(
            ((value if value is not None else statistic.mean) - statistic.mean) / statistic.scale
            for value, statistic in zip(row.values, safe_receipt.statistics, strict=True)
        )
        transformed.append(SyntheticTransformedRow(row_id=row_id, values=values))
    return SyntheticTransformedBatch(
        split_fingerprint=split_fingerprint,
        preprocessing_fingerprint=synthetic_preprocessing_fingerprint(safe_receipt),
        partition=partition,
        rows=tuple(transformed),
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExpectedLabel:
    row_id: str
    label: SyntheticClass

    def __post_init__(self) -> None:
        _machine_string(self.row_id, _ROW_ID)
        _strict_enum(self.label, SyntheticClass)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPredictedLabel:
    row_id: str
    label: SyntheticClass

    def __post_init__(self) -> None:
        _machine_string(self.row_id, _ROW_ID)
        _strict_enum(self.label, SyntheticClass)


def _label_map(
    values: object,
    expected_type: type[SyntheticExpectedLabel | SyntheticPredictedLabel],
) -> dict[str, SyntheticClass]:
    if type(values) is not tuple:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    result: dict[str, SyntheticClass] = {}
    for value in values:
        if type(value) is not expected_type:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        try:
            snapshot = expected_type(row_id=value.row_id, label=value.label)
        except ResearchBoundaryError:
            raise
        except (AttributeError, TypeError, ValueError):
            raise _error(ResearchBoundaryCode.INVALID_TYPE) from None
        if snapshot.row_id in result:
            raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
        result[snapshot.row_id] = snapshot.label
    return result


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEvaluationReceipt:
    evaluation_version: str
    split_fingerprint: str
    preprocessing_fingerprint: str
    expected_fingerprint: str
    predicted_fingerprint: str
    partition: SyntheticPartition
    evaluated_count: int
    class_alpha_count: int
    class_beta_count: int
    correct_count: int
    error_count: int
    state: SyntheticEvaluationState = SyntheticEvaluationState.TEST_ONLY_UNAPPROVED
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.evaluation_version, _VERSION)
        _machine_string(self.split_fingerprint, _SHA256)
        _machine_string(self.preprocessing_fingerprint, _SHA256)
        _machine_string(self.expected_fingerprint, _SHA256)
        _machine_string(self.predicted_fingerprint, _SHA256)
        _strict_enum(self.partition, SyntheticPartition)
        if self.partition is not SyntheticPartition.TEST:
            raise _error(ResearchBoundaryCode.LEAKAGE_DETECTED)
        counts = (
            self.evaluated_count,
            self.class_alpha_count,
            self.class_beta_count,
            self.correct_count,
            self.error_count,
        )
        if any(type(value) is not int or value < 0 for value in counts):
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if self.class_alpha_count == 0 or self.class_beta_count == 0:
            raise _error(ResearchBoundaryCode.DEGENERATE_EVALUATION)
        if self.class_alpha_count + self.class_beta_count != self.evaluated_count:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        if self.correct_count + self.error_count != self.evaluated_count:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        _strict_enum(self.state, SyntheticEvaluationState)
        _strict_enum(self.authority, ResearchAuthority)


def validate_synthetic_evaluation_receipt(value: object) -> SyntheticEvaluationReceipt:
    if type(value) is not SyntheticEvaluationReceipt:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticEvaluationReceipt(
            evaluation_version=value.evaluation_version,
            split_fingerprint=value.split_fingerprint,
            preprocessing_fingerprint=value.preprocessing_fingerprint,
            expected_fingerprint=value.expected_fingerprint,
            predicted_fingerprint=value.predicted_fingerprint,
            partition=value.partition,
            evaluated_count=value.evaluated_count,
            class_alpha_count=value.class_alpha_count,
            class_beta_count=value.class_beta_count,
            correct_count=value.correct_count,
            error_count=value.error_count,
            state=value.state,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_evaluation_fingerprint(value: SyntheticEvaluationReceipt) -> str:
    receipt = validate_synthetic_evaluation_receipt(value)
    return _canonical_hash(
        (
            receipt.evaluation_version,
            receipt.split_fingerprint,
            receipt.preprocessing_fingerprint,
            receipt.expected_fingerprint,
            receipt.predicted_fingerprint,
            receipt.partition.value,
            str(receipt.evaluated_count),
            str(receipt.class_alpha_count),
            str(receipt.class_beta_count),
            str(receipt.correct_count),
            str(receipt.error_count),
            receipt.state.value,
            receipt.authority.value,
        )
    )


def evaluate_synthetic_labels(
    *,
    expected: tuple[SyntheticExpectedLabel, ...],
    predicted: tuple[SyntheticPredictedLabel, ...],
    split: SyntheticSplitManifest,
    preprocessing: SyntheticPreprocessingReceipt,
    evaluation_version: str,
    environment: ResearchEnvironment,
) -> SyntheticEvaluationReceipt:
    validate_research_environment(environment)
    safe_split = validate_synthetic_split_manifest(split)
    safe_preprocessing = _validate_preprocessing_receipt(preprocessing)
    _machine_string(evaluation_version, _VERSION)
    split_fingerprint = synthetic_split_fingerprint(safe_split)
    if safe_preprocessing.split_fingerprint != split_fingerprint:
        raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
    expected_by_id = _label_map(expected, SyntheticExpectedLabel)
    predicted_by_id = _label_map(predicted, SyntheticPredictedLabel)
    test_ids = {
        item.row_id for item in safe_split.assignments if item.partition is SyntheticPartition.TEST
    }
    if set(expected_by_id) != test_ids or set(predicted_by_id) != test_ids:
        raise _error(ResearchBoundaryCode.PARTITION_MISMATCH)
    alpha_count = sum(label is SyntheticClass.CLASS_ALPHA for label in expected_by_id.values())
    beta_count = len(expected_by_id) - alpha_count
    if alpha_count == 0 or beta_count == 0:
        raise _error(ResearchBoundaryCode.DEGENERATE_EVALUATION)
    correct = sum(expected_by_id[row_id] is predicted_by_id[row_id] for row_id in test_ids)
    return SyntheticEvaluationReceipt(
        evaluation_version=evaluation_version,
        split_fingerprint=split_fingerprint,
        preprocessing_fingerprint=synthetic_preprocessing_fingerprint(safe_preprocessing),
        expected_fingerprint=_canonical_hash(
            tuple(f"{row_id}:{expected_by_id[row_id].value}" for row_id in sorted(test_ids))
        ),
        predicted_fingerprint=_canonical_hash(
            tuple(f"{row_id}:{predicted_by_id[row_id].value}" for row_id in sorted(test_ids))
        ),
        partition=SyntheticPartition.TEST,
        evaluated_count=len(test_ids),
        class_alpha_count=alpha_count,
        class_beta_count=beta_count,
        correct_count=correct,
        error_count=len(test_ids) - correct,
    )


__all__ = [
    "MissingValuePolicy",
    "ScalingPolicy",
    "SyntheticClass",
    "SyntheticEvaluationReceipt",
    "SyntheticEvaluationState",
    "SyntheticExpectedLabel",
    "SyntheticFeatureRow",
    "SyntheticFeatureStatistics",
    "SyntheticPartition",
    "SyntheticPartitionAssignment",
    "SyntheticPredictedLabel",
    "SyntheticPreprocessingPlan",
    "SyntheticPreprocessingReceipt",
    "SyntheticSplitConfig",
    "SyntheticSplitManifest",
    "SyntheticTransformedBatch",
    "SyntheticTransformedRow",
    "build_deterministic_group_split",
    "evaluate_synthetic_labels",
    "fit_synthetic_preprocessor",
    "synthetic_evaluation_fingerprint",
    "synthetic_preprocessing_fingerprint",
    "synthetic_split_fingerprint",
    "transform_synthetic_partition",
    "validate_synthetic_evaluation_receipt",
    "validate_synthetic_preprocessing_receipt",
    "validate_synthetic_split_manifest",
    "validate_synthetic_transformed_batch",
]
