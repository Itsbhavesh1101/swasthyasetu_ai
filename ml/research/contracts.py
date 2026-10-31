"""Strict content-free contracts for the isolated P18-A research boundary."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

_DATASET_ID = re.compile(r"^syn_ml_dataset_(?:alpha|beta|gamma|delta)$")
_EXPERIMENT_ID = re.compile(r"^syn_ml_experiment_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")


class ResearchBoundaryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    UNKNOWN_IDENTITY = "UNKNOWN_IDENTITY"
    CAPACITY_EXCEEDED = "CAPACITY_EXCEEDED"
    LEAKAGE_DETECTED = "LEAKAGE_DETECTED"
    PARTITION_MISMATCH = "PARTITION_MISMATCH"
    INCOMPLETE_PARTITION = "INCOMPLETE_PARTITION"
    INCOMPLETE_INPUT = "INCOMPLETE_INPUT"
    DEGENERATE_EVALUATION = "DEGENERATE_EVALUATION"


class ResearchBoundaryError(ValueError):
    """Stable content-free failure at the synthetic research boundary."""

    def __init__(self, code: ResearchBoundaryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: ResearchBoundaryCode) -> ResearchBoundaryError:
    return ResearchBoundaryError(code)


class ResearchEnvironment(StrEnum):
    LOCAL = "LOCAL"
    TEST = "TEST"
    STAGING = "STAGING"
    PILOT = "PILOT"
    PRODUCTION = "PRODUCTION"


class ResearchAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticDatasetSource(StrEnum):
    SYNTHETIC_GENERATED = "SYNTHETIC_GENERATED"


class SyntheticDataClassification(StrEnum):
    SYNTHETIC_NON_MEDICAL = "SYNTHETIC_NON_MEDICAL"


class SyntheticLicense(StrEnum):
    ENGINEERING_FIXTURE_ONLY = "ENGINEERING_FIXTURE_ONLY"


class DatasetAdmissionState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


class ExperimentExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class ExperimentApprovalState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ResearchBoundaryCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    return value.astimezone(UTC)


def validate_research_environment(environment: object) -> ResearchEnvironment:
    _strict_enum(environment, ResearchEnvironment)
    assert isinstance(environment, ResearchEnvironment)
    if environment not in {ResearchEnvironment.LOCAL, ResearchEnvironment.TEST}:
        raise _error(ResearchBoundaryCode.PROTECTED_ENVIRONMENT)
    return environment


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticDatasetManifest:
    dataset_id: str
    dataset_version: str
    source: SyntheticDatasetSource
    classification: SyntheticDataClassification
    license: SyntheticLicense
    admission_state: DatasetAdmissionState
    content_hash: str
    schema_hash: str
    schema_version: str
    created_at: datetime
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.dataset_id, _DATASET_ID)
        _machine_string(self.dataset_version, _VERSION)
        _strict_enum(self.source, SyntheticDatasetSource)
        _strict_enum(self.classification, SyntheticDataClassification)
        _strict_enum(self.license, SyntheticLicense)
        _strict_enum(self.admission_state, DatasetAdmissionState)
        _machine_string(self.content_hash, _SHA256)
        _machine_string(self.schema_hash, _SHA256)
        _machine_string(self.schema_version, _VERSION)
        created_at = _utc(self.created_at)
        _strict_enum(self.authority, ResearchAuthority)
        object.__setattr__(self, "created_at", created_at)


def validate_synthetic_dataset_manifest(value: object) -> SyntheticDatasetManifest:
    if type(value) is not SyntheticDatasetManifest:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticDatasetManifest(
            dataset_id=value.dataset_id,
            dataset_version=value.dataset_version,
            source=value.source,
            classification=value.classification,
            license=value.license,
            admission_state=value.admission_state,
            content_hash=value.content_hash,
            schema_hash=value.schema_hash,
            schema_version=value.schema_version,
            created_at=value.created_at,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_dataset_fingerprint(value: SyntheticDatasetManifest) -> str:
    manifest = validate_synthetic_dataset_manifest(value)
    fields = (
        manifest.dataset_id,
        manifest.dataset_version,
        manifest.source.value,
        manifest.classification.value,
        manifest.license.value,
        manifest.admission_state.value,
        manifest.content_hash,
        manifest.schema_hash,
        manifest.schema_version,
        manifest.created_at.isoformat(),
        manifest.authority.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExperimentRecord:
    experiment_id: str
    experiment_version: str
    dataset_id: str
    dataset_version: str
    dataset_fingerprint: str
    code_commit: str
    dependency_lock_hash: str
    configuration_hash: str
    seed: int
    created_at: datetime
    execution_state: ExperimentExecutionState
    approval_state: ExperimentApprovalState
    authority: ResearchAuthority = ResearchAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _machine_string(self.experiment_id, _EXPERIMENT_ID)
        _machine_string(self.experiment_version, _VERSION)
        _machine_string(self.dataset_id, _DATASET_ID)
        _machine_string(self.dataset_version, _VERSION)
        _machine_string(self.dataset_fingerprint, _SHA256)
        _machine_string(self.code_commit, _GIT_SHA)
        _machine_string(self.dependency_lock_hash, _SHA256)
        _machine_string(self.configuration_hash, _SHA256)
        if type(self.seed) is not int:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if not 0 <= self.seed < 2**32:
            raise _error(ResearchBoundaryCode.INVALID_VALUE)
        created_at = _utc(self.created_at)
        _strict_enum(self.execution_state, ExperimentExecutionState)
        _strict_enum(self.approval_state, ExperimentApprovalState)
        _strict_enum(self.authority, ResearchAuthority)
        object.__setattr__(self, "created_at", created_at)


def validate_synthetic_experiment_record(value: object) -> SyntheticExperimentRecord:
    if type(value) is not SyntheticExperimentRecord:
        raise _error(ResearchBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticExperimentRecord(
            experiment_id=value.experiment_id,
            experiment_version=value.experiment_version,
            dataset_id=value.dataset_id,
            dataset_version=value.dataset_version,
            dataset_fingerprint=value.dataset_fingerprint,
            code_commit=value.code_commit,
            dependency_lock_hash=value.dependency_lock_hash,
            configuration_hash=value.configuration_hash,
            seed=value.seed,
            created_at=value.created_at,
            execution_state=value.execution_state,
            approval_state=value.approval_state,
            authority=value.authority,
        )
    except ResearchBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ResearchBoundaryCode.INVALID_TYPE) from None


def synthetic_experiment_fingerprint(value: SyntheticExperimentRecord) -> str:
    record = validate_synthetic_experiment_record(value)
    fields = (
        record.experiment_id,
        record.experiment_version,
        record.dataset_id,
        record.dataset_version,
        record.dataset_fingerprint,
        record.code_commit,
        record.dependency_lock_hash,
        record.configuration_hash,
        str(record.seed),
        record.created_at.isoformat(),
        record.execution_state.value,
        record.approval_state.value,
        record.authority.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


__all__ = [
    "DatasetAdmissionState",
    "ExperimentApprovalState",
    "ExperimentExecutionState",
    "ResearchAuthority",
    "ResearchBoundaryCode",
    "ResearchBoundaryError",
    "ResearchEnvironment",
    "SyntheticDataClassification",
    "SyntheticDatasetManifest",
    "SyntheticDatasetSource",
    "SyntheticExperimentRecord",
    "SyntheticLicense",
    "synthetic_dataset_fingerprint",
    "synthetic_experiment_fingerprint",
    "validate_research_environment",
    "validate_synthetic_dataset_manifest",
    "validate_synthetic_experiment_record",
]
