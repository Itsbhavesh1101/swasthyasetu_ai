"""Immutable, engineering-only clinical-summary domain values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.shared.types import OpaqueId

MAX_ASSERTIONS = 64
MAX_ASSERTIONS_PER_SECTION = 16
MAX_LABEL_LENGTH = 256
MAX_MACHINE_TOKEN_LENGTH = 128

_MACHINE_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_SYNTHETIC_LABEL = re.compile(r"^SYNTHETIC_[A-Z0-9]+(?:_[A-Z0-9]+)*$")
_FORBIDDEN_AUTHORITY_MARKERS = (
    "APPROVED",
    "CONFIRMED",
    "SIGNED",
    "MEDICALLY_CLEARED",
    "SELF_CARE",
    "AI_EXTRACTED",
    "OVERRIDE",
    "EMERGENCY",
    "TRIAGE",
)
_BLOCKED_P9_SYNTHETIC_TOKENS = frozenset(
    {
        "SYNTHETIC_COMPLETE_A",
        "SYNTHETIC_OVERRIDE_A",
        "SYNTHETIC_OVERRIDE_B",
        "SYNTHETIC_MISSING_A",
        "SYNTHETIC_AMBIGUOUS_A",
        "SYNTHETIC_EXCLUDE_A",
        "SYNTHETIC_PRIORITY_A",
        "SYNTHETIC_ROUTINE_A",
        "SYNTHETIC_SELF_CARE_A",
    }
)


class SummaryValidationCode(StrEnum):
    """Content-free closed failure codes for the pure summary boundary."""

    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_SCOPE = "INVALID_SCOPE"
    INVALID_SOURCE = "INVALID_SOURCE"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    INVALID_CONFLICT = "INVALID_CONFLICT"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"


class SummaryValidationError(ValueError):
    """Fail closed without echoing source content or opaque identifiers."""

    def __init__(self, code: SummaryValidationCode) -> None:
        self.code = code
        super().__init__(code.value)


class SummarySectionId(StrEnum):
    CHIEF_COMPLAINT = "CHIEF_COMPLAINT"
    HPI = "HPI"
    PAST_MEDICAL_HISTORY = "PAST_MEDICAL_HISTORY"
    PAST_SURGICAL_HISTORY = "PAST_SURGICAL_HISTORY"
    MEDICATIONS = "MEDICATIONS"
    ALLERGIES = "ALLERGIES"
    FAMILY_HISTORY = "FAMILY_HISTORY"
    PERSONAL_HISTORY = "PERSONAL_HISTORY"
    REVIEW_OF_SYSTEMS = "REVIEW_OF_SYSTEMS"
    PRIOR_INVESTIGATIONS = "PRIOR_INVESTIGATIONS"


CANONICAL_SECTION_ORDER = tuple(SummarySectionId)


class SummaryStatus(StrEnum):
    DRAFT = "DRAFT"
    CLINICIAN_EDITED = "CLINICIAN_EDITED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class SummaryClassification(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SummarySourceKind(StrEnum):
    P5_CLINICAL_FACT = "P5_CLINICAL_FACT"
    P7_PATIENT_REPORTED = "P7_PATIENT_REPORTED"


class PatientReportedMarker(StrEnum):
    PATIENT_REPORTED = "PATIENT_REPORTED"


class SectionReadiness(StrEnum):
    UNKNOWN = "UNKNOWN"
    NOT_RECORDED = "NOT_RECORDED"
    UNVERIFIED = "UNVERIFIED"
    RECORDED = "RECORDED"
    UNAVAILABLE = "UNAVAILABLE"


class AssertionConflictState(StrEnum):
    NONE = "NONE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SummaryFreshness(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SourceDriftReason(StrEnum):
    SNAPSHOT_CHANGED = "SNAPSHOT_CHANGED"
    SOURCE_CHANGED = "SOURCE_CHANGED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    TERMINAL_SOURCE = "TERMINAL_SOURCE"
    NEW_CONFLICT = "NEW_CONFLICT"


def _fail(code: SummaryValidationCode) -> SummaryValidationError:
    return SummaryValidationError(code)


def _opaque_id(value: object) -> None:
    if not isinstance(value, OpaqueId) or not isinstance(value.value, UUID):
        raise _fail(SummaryValidationCode.INVALID_TYPE)


def _enum(value: object, enum_type: type[StrEnum]) -> None:
    if not isinstance(value, enum_type):
        raise _fail(SummaryValidationCode.INVALID_TYPE)


def _tuple(value: object, item_type: type[object], *, maximum: int) -> None:
    if not isinstance(value, tuple):
        raise _fail(SummaryValidationCode.INVALID_TYPE)
    if len(value) > maximum:
        raise _fail(SummaryValidationCode.LIMIT_EXCEEDED)
    if any(not isinstance(item, item_type) for item in value):
        raise _fail(SummaryValidationCode.INVALID_TYPE)


def _machine_token(value: object) -> None:
    if (
        not isinstance(value, str)
        or len(value) > MAX_MACHINE_TOKEN_LENGTH
        or _MACHINE_TOKEN.fullmatch(value) is None
    ):
        raise _fail(SummaryValidationCode.INVALID_VALUE)


def _optional_machine_token(value: object) -> None:
    if value is not None:
        _machine_token(value)


def _synthetic_label(value: object) -> None:
    if (
        not isinstance(value, str)
        or len(value) > MAX_LABEL_LENGTH
        or _SYNTHETIC_LABEL.fullmatch(value) is None
        or any(marker in value for marker in _FORBIDDEN_AUTHORITY_MARKERS)
        or value in _BLOCKED_P9_SYNTHETIC_TOKENS
    ):
        raise _fail(SummaryValidationCode.INVALID_VALUE)


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise _fail(SummaryValidationCode.INVALID_TYPE)
    if value.tzinfo is None or value.utcoffset() is None:
        raise _fail(SummaryValidationCode.INVALID_VALUE)
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class SummarySourceReference:
    """Supplied source linkage; never an authorization or source-view grant."""

    source_id: OpaqueId = field(repr=False)
    encounter_id: OpaqueId = field(repr=False)
    section_id: SummarySectionId
    source_kind: SummarySourceKind
    source_version: str = field(repr=False)
    p5_verification_state: VerificationState | None = None
    p5_source_type: ProvenanceSourceType | None = None
    p7_marker: PatientReportedMarker | None = None

    def __post_init__(self) -> None:
        _opaque_id(self.source_id)
        _opaque_id(self.encounter_id)
        _enum(self.section_id, SummarySectionId)
        _enum(self.source_kind, SummarySourceKind)
        _machine_token(self.source_version)
        if self.source_kind is SummarySourceKind.P5_CLINICAL_FACT:
            if not isinstance(self.p5_verification_state, VerificationState) or not isinstance(
                self.p5_source_type, ProvenanceSourceType
            ):
                raise _fail(SummaryValidationCode.INVALID_SOURCE)
            if self.p7_marker is not None or self.p5_verification_state in {
                VerificationState.REJECTED,
                VerificationState.SUPERSEDED,
            }:
                raise _fail(SummaryValidationCode.INVALID_SOURCE)
        elif (
            self.p7_marker is not PatientReportedMarker.PATIENT_REPORTED
            or self.p5_verification_state is not None
            or self.p5_source_type is not None
        ):
            raise _fail(SummaryValidationCode.INVALID_SOURCE)


@dataclass(frozen=True, slots=True, kw_only=True)
class SummaryAssertion:
    assertion_id: OpaqueId = field(repr=False)
    label: str = field(repr=False)
    source: SummarySourceReference
    conflict_state: AssertionConflictState
    conflict_key: str | None = None

    def __post_init__(self) -> None:
        _opaque_id(self.assertion_id)
        _synthetic_label(self.label)
        if not isinstance(self.source, SummarySourceReference):
            raise _fail(SummaryValidationCode.INVALID_TYPE)
        _enum(self.conflict_state, AssertionConflictState)
        _optional_machine_token(self.conflict_key)
        if (self.conflict_key is None) != (self.conflict_state is AssertionConflictState.NONE):
            raise _fail(SummaryValidationCode.INVALID_CONFLICT)


@dataclass(frozen=True, slots=True, kw_only=True)
class SummarySection:
    section_id: SummarySectionId
    readiness: SectionReadiness
    assertions: tuple[SummaryAssertion, ...]
    review_required: bool

    def __post_init__(self) -> None:
        _enum(self.section_id, SummarySectionId)
        _enum(self.readiness, SectionReadiness)
        _tuple(self.assertions, SummaryAssertion, maximum=MAX_ASSERTIONS_PER_SECTION)
        if type(self.review_required) is not bool:
            raise _fail(SummaryValidationCode.INVALID_TYPE)
        if any(item.source.section_id is not self.section_id for item in self.assertions):
            raise _fail(SummaryValidationCode.INVALID_SOURCE)
        if self.review_required != any(
            item.conflict_state is AssertionConflictState.REVIEW_REQUIRED
            for item in self.assertions
        ):
            raise _fail(SummaryValidationCode.INVALID_CONFLICT)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClinicalSummaryDraft:
    summary_id: OpaqueId = field(repr=False)
    encounter_id: OpaqueId = field(repr=False)
    snapshot_token: str = field(repr=False)
    created_at: datetime
    sections: tuple[SummarySection, ...]
    source_references: tuple[SummarySourceReference, ...]
    status: SummaryStatus = SummaryStatus.DRAFT
    classification: SummaryClassification = SummaryClassification.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        _opaque_id(self.summary_id)
        _opaque_id(self.encounter_id)
        _machine_token(self.snapshot_token)
        object.__setattr__(self, "created_at", _utc(self.created_at))
        _tuple(self.sections, SummarySection, maximum=len(CANONICAL_SECTION_ORDER))
        _tuple(self.source_references, SummarySourceReference, maximum=MAX_ASSERTIONS)
        if tuple(section.section_id for section in self.sections) != CANONICAL_SECTION_ORDER:
            raise _fail(SummaryValidationCode.INVALID_VALUE)
        if self.status is not SummaryStatus.DRAFT:
            raise _fail(SummaryValidationCode.INVALID_VALUE)
        if self.classification is not SummaryClassification.ENGINEERING_ONLY:
            raise _fail(SummaryValidationCode.INVALID_VALUE)
        if any(source.encounter_id != self.encounter_id for source in self.source_references):
            raise _fail(SummaryValidationCode.INVALID_SCOPE)
        expected = tuple(
            assertion.source for section in self.sections for assertion in section.assertions
        )
        if self.source_references != expected:
            raise _fail(SummaryValidationCode.INVALID_SOURCE)


@dataclass(frozen=True, slots=True, kw_only=True)
class SummaryFreshnessResult:
    freshness: SummaryFreshness
    affected_sections: tuple[SummarySectionId, ...]
    reasons: tuple[SourceDriftReason, ...]

    def __post_init__(self) -> None:
        _enum(self.freshness, SummaryFreshness)
        _tuple(
            self.affected_sections,
            SummarySectionId,
            maximum=len(CANONICAL_SECTION_ORDER),
        )
        _tuple(self.reasons, SourceDriftReason, maximum=len(SourceDriftReason))
        if self.affected_sections != tuple(
            section for section in CANONICAL_SECTION_ORDER if section in self.affected_sections
        ):
            raise _fail(SummaryValidationCode.INVALID_VALUE)
        if self.reasons != tuple(sorted(set(self.reasons), key=lambda item: item.value)):
            raise _fail(SummaryValidationCode.INVALID_VALUE)
        if (self.freshness is SummaryFreshness.CURRENT) != (
            not self.affected_sections and not self.reasons
        ):
            raise _fail(SummaryValidationCode.INVALID_VALUE)
