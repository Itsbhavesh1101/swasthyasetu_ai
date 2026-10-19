"""Strict synthetic input contracts for deterministic summary projection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.modules.provenance.domain import VerificationState
from app.modules.summaries.domain import (
    CANONICAL_SECTION_ORDER,
    MAX_ASSERTIONS,
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
    SummaryValidationCode,
    SummaryValidationError,
    _machine_token,
    _opaque_id,
    _synthetic_label,
    _tuple,
    _utc,
)
from app.shared.types import OpaqueId


class SourceCoverage(StrEnum):
    UNKNOWN = "UNKNOWN"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"
    UNAVAILABLE = "UNAVAILABLE"


class CurrentSourceAvailability(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    REMOVED = "REMOVED"


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSourceProjection:
    """Previously minimized synthetic assertion supplied by a hypothetical caller."""

    assertion_id: OpaqueId = field(repr=False)
    label: str = field(repr=False)
    source: SummarySourceReference
    conflict_key: str | None = None

    def __post_init__(self) -> None:
        _opaque_id(self.assertion_id)
        _synthetic_label(self.label)
        if not isinstance(self.source, SummarySourceReference):
            raise SummaryValidationError(SummaryValidationCode.INVALID_TYPE)
        if self.conflict_key is not None:
            _machine_token(self.conflict_key)


@dataclass(frozen=True, slots=True, kw_only=True)
class SectionCoverage:
    section_id: SummarySectionId
    coverage: SourceCoverage

    def __post_init__(self) -> None:
        if not isinstance(self.section_id, SummarySectionId) or not isinstance(
            self.coverage, SourceCoverage
        ):
            raise SummaryValidationError(SummaryValidationCode.INVALID_TYPE)


@dataclass(frozen=True, slots=True, kw_only=True)
class SummaryProjectionInput:
    summary_id: OpaqueId = field(repr=False)
    encounter_id: OpaqueId = field(repr=False)
    snapshot_token: str = field(repr=False)
    generated_at: datetime
    sources: tuple[SyntheticSourceProjection, ...]
    coverage: tuple[SectionCoverage, ...] = ()

    def __post_init__(self) -> None:
        _opaque_id(self.summary_id)
        _opaque_id(self.encounter_id)
        _machine_token(self.snapshot_token)
        object.__setattr__(self, "generated_at", _utc(self.generated_at))
        _tuple(self.sources, SyntheticSourceProjection, maximum=MAX_ASSERTIONS)
        _tuple(self.coverage, SectionCoverage, maximum=len(CANONICAL_SECTION_ORDER))


@dataclass(frozen=True, slots=True, kw_only=True)
class CurrentSourceState:
    source_id: OpaqueId = field(repr=False)
    encounter_id: OpaqueId = field(repr=False)
    section_id: SummarySectionId
    source_kind: SummarySourceKind
    source_version: str = field(repr=False)
    availability: CurrentSourceAvailability
    p5_verification_state: VerificationState | None = None

    def __post_init__(self) -> None:
        _opaque_id(self.source_id)
        _opaque_id(self.encounter_id)
        if not isinstance(self.section_id, SummarySectionId) or not isinstance(
            self.source_kind, SummarySourceKind
        ):
            raise SummaryValidationError(SummaryValidationCode.INVALID_TYPE)
        _machine_token(self.source_version)
        if not isinstance(self.availability, CurrentSourceAvailability):
            raise SummaryValidationError(SummaryValidationCode.INVALID_TYPE)
        if self.source_kind is SummarySourceKind.P5_CLINICAL_FACT:
            if not isinstance(self.p5_verification_state, VerificationState):
                raise SummaryValidationError(SummaryValidationCode.INVALID_SOURCE)
        elif self.p5_verification_state is not None:
            raise SummaryValidationError(SummaryValidationCode.INVALID_SOURCE)


@dataclass(frozen=True, slots=True, kw_only=True)
class CurrentSourceSnapshot:
    """Complete relevant scoped source set supplied for synthetic comparison."""

    encounter_id: OpaqueId = field(repr=False)
    snapshot_token: str = field(repr=False)
    sources: tuple[CurrentSourceState, ...]
    conflict_sections: tuple[SummarySectionId, ...] = ()

    def __post_init__(self) -> None:
        _opaque_id(self.encounter_id)
        _machine_token(self.snapshot_token)
        _tuple(self.sources, CurrentSourceState, maximum=MAX_ASSERTIONS)
        _tuple(
            self.conflict_sections,
            SummarySectionId,
            maximum=len(CANONICAL_SECTION_ORDER),
        )
        if len(set(self.conflict_sections)) != len(self.conflict_sections):
            raise SummaryValidationError(SummaryValidationCode.DUPLICATE_IDENTITY)
        if self.conflict_sections != tuple(
            section for section in CANONICAL_SECTION_ORDER if section in self.conflict_sections
        ):
            raise SummaryValidationError(SummaryValidationCode.INVALID_VALUE)
