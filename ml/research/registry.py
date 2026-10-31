"""Immutable in-memory registries for synthetic P18-A research metadata."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ml.research.contracts import (
    ResearchBoundaryCode,
    ResearchBoundaryError,
    ResearchEnvironment,
    SyntheticDatasetManifest,
    SyntheticExperimentRecord,
    synthetic_dataset_fingerprint,
    validate_research_environment,
    validate_synthetic_dataset_manifest,
    validate_synthetic_experiment_record,
)

_MAX_ENTRIES = 32
type _Identity = tuple[str, str]


def _error(code: ResearchBoundaryCode) -> ResearchBoundaryError:
    return ResearchBoundaryError(code)


def _identity(identifier: object, version: object) -> _Identity:
    if type(identifier) is not str or type(version) is not str:
        raise _error(ResearchBoundaryCode.UNKNOWN_IDENTITY)
    return identifier, version


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticDatasetRegistry:
    manifests: tuple[SyntheticDatasetManifest, ...]
    environment: ResearchEnvironment
    _by_identity: Mapping[_Identity, SyntheticDatasetManifest] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        environment = validate_research_environment(self.environment)
        if type(self.manifests) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if len(self.manifests) > _MAX_ENTRIES:
            raise _error(ResearchBoundaryCode.CAPACITY_EXCEEDED)

        snapshots: list[SyntheticDatasetManifest] = []
        by_identity: dict[_Identity, SyntheticDatasetManifest] = {}
        for value in self.manifests:
            manifest = validate_synthetic_dataset_manifest(value)
            identity = (manifest.dataset_id, manifest.dataset_version)
            if identity in by_identity:
                raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
            snapshots.append(manifest)
            by_identity[identity] = manifest

        object.__setattr__(self, "manifests", tuple(snapshots))
        object.__setattr__(self, "environment", environment)
        object.__setattr__(self, "_by_identity", MappingProxyType(by_identity))

    def resolve(self, dataset_id: object, dataset_version: object) -> SyntheticDatasetManifest:
        try:
            return self._by_identity[_identity(dataset_id, dataset_version)]
        except KeyError:
            raise _error(ResearchBoundaryCode.UNKNOWN_IDENTITY) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExperimentRegistry:
    records: tuple[SyntheticExperimentRecord, ...]
    datasets: SyntheticDatasetRegistry
    environment: ResearchEnvironment
    _by_identity: Mapping[_Identity, SyntheticExperimentRecord] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        environment = validate_research_environment(self.environment)
        if type(self.datasets) is not SyntheticDatasetRegistry:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        datasets = SyntheticDatasetRegistry(
            manifests=self.datasets.manifests,
            environment=self.datasets.environment,
        )
        if datasets.environment is not environment:
            raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
        if type(self.records) is not tuple:
            raise _error(ResearchBoundaryCode.INVALID_TYPE)
        if len(self.records) > _MAX_ENTRIES:
            raise _error(ResearchBoundaryCode.CAPACITY_EXCEEDED)

        snapshots: list[SyntheticExperimentRecord] = []
        by_identity: dict[_Identity, SyntheticExperimentRecord] = {}
        for value in self.records:
            record = validate_synthetic_experiment_record(value)
            identity = (record.experiment_id, record.experiment_version)
            if identity in by_identity:
                raise _error(ResearchBoundaryCode.DUPLICATE_IDENTITY)
            try:
                manifest = datasets.resolve(record.dataset_id, record.dataset_version)
            except ResearchBoundaryError:
                raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH) from None
            if synthetic_dataset_fingerprint(manifest) != record.dataset_fingerprint:
                raise _error(ResearchBoundaryCode.IDENTITY_MISMATCH)
            snapshots.append(record)
            by_identity[identity] = record

        object.__setattr__(self, "records", tuple(snapshots))
        object.__setattr__(self, "datasets", datasets)
        object.__setattr__(self, "environment", environment)
        object.__setattr__(self, "_by_identity", MappingProxyType(by_identity))

    def resolve(
        self, experiment_id: object, experiment_version: object
    ) -> SyntheticExperimentRecord:
        try:
            return self._by_identity[_identity(experiment_id, experiment_version)]
        except KeyError:
            raise _error(ResearchBoundaryCode.UNKNOWN_IDENTITY) from None


__all__ = ["SyntheticDatasetRegistry", "SyntheticExperimentRegistry"]
