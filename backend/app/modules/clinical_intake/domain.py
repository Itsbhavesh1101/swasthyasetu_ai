"""Immutable clinical-intake domain values without clinical interpretation."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from app.shared.types import OpaqueId

IntakeId = OpaqueId


def normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def bounded_text(name: str, value: str, maximum: int = 512) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or len(value) > maximum
    ):
        raise ValueError(f"{name} must be non-blank, trimmed, and bounded")
    return value


def optional_text(name: str, value: str | None, maximum: int = 512) -> str | None:
    return None if value is None else bounded_text(name, value, maximum)


def tuple_of(name: str, value: object, item_type: type[object]) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, item_type) for item in value):
        raise TypeError(f"{name} must be a tuple of {item_type.__name__}")


class ClinicalIntakeStatus(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class InvalidClinicalIntakeTransitionError(ValueError):
    """Raised when the closed intake lifecycle rejects a transition."""


@dataclass(frozen=True, slots=True)
class ChiefComplaint:
    patient_wording: str = field(repr=False)
    display_key: str
    source_answer_id: OpaqueId
    normalized_code: str | None = None
    coding_system: str | None = None

    def __post_init__(self) -> None:
        bounded_text("patient_wording", self.patient_wording, 2000)
        bounded_text("display_key", self.display_key, 128)
        optional_text("normalized_code", self.normalized_code, 128)
        optional_text("coding_system", self.coding_system, 128)
        if (self.normalized_code is None) != (self.coding_system is None):
            raise ValueError("normalized_code and coding_system must be supplied together")


@dataclass(frozen=True, slots=True)
class StructuredValue:
    value: str = field(repr=False)
    source_answer_id: OpaqueId

    def __post_init__(self) -> None:
        bounded_text("value", self.value, 2000)


@dataclass(frozen=True, slots=True)
class DurationValue:
    value: Decimal
    unit: str
    source_answer_id: OpaqueId

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal) or not self.value.is_finite() or self.value < 0:
            raise ValueError("duration value must be a finite non-negative Decimal")
        bounded_text("unit", self.unit, 32)


@dataclass(frozen=True, slots=True)
class SeverityValue:
    scale_id: str
    scale_version: str
    value: Decimal
    source_answer_id: OpaqueId

    def __post_init__(self) -> None:
        bounded_text("scale_id", self.scale_id, 128)
        bounded_text("scale_version", self.scale_version, 64)
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            raise ValueError("severity value must be a finite Decimal")


@dataclass(frozen=True, slots=True)
class HistoryOfPresentIllness:
    onset: StructuredValue | None = None
    duration: DurationValue | None = None
    location: StructuredValue | None = None
    character: StructuredValue | None = None
    severity: SeverityValue | None = None
    progression: StructuredValue | None = None
    associated_symptoms: tuple[StructuredValue, ...] = ()
    aggravating_factors: tuple[StructuredValue, ...] = ()
    relieving_factors: tuple[StructuredValue, ...] = ()

    def __post_init__(self) -> None:
        for name in ("associated_symptoms", "aggravating_factors", "relieving_factors"):
            tuple_of(name, getattr(self, name), StructuredValue)


class HistorySourceKind(StrEnum):
    ANSWER = "ANSWER"
    REUSED_HISTORY = "REUSED_HISTORY"


class ConfirmationState(StrEnum):
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DISAGREED = "DISAGREED"


@dataclass(frozen=True, slots=True)
class SourceReference:
    answer_id: OpaqueId | None = None
    fact_id: OpaqueId | None = None
    verification_state: str | None = None

    def __post_init__(self) -> None:
        if (self.answer_id is None) == (self.fact_id is None):
            raise ValueError("source reference requires exactly one answer_id or fact_id")
        if self.answer_id is not None and self.verification_state is not None:
            raise ValueError("answer source cannot carry a verification_state")
        optional_text("verification_state", self.verification_state, 64)


@dataclass(frozen=True, slots=True)
class HistoryReference:
    entry_id: OpaqueId
    display_value: str = field(repr=False)
    source_kind: HistorySourceKind
    confirmation_state: ConfirmationState
    source_answer_id: OpaqueId | None = None
    source_fact_id: OpaqueId | None = None
    verification_state: str | None = None

    def __post_init__(self) -> None:
        bounded_text("display_value", self.display_value, 2000)
        if self.source_kind is HistorySourceKind.ANSWER:
            if self.source_answer_id is None or self.source_fact_id is not None:
                raise ValueError("ANSWER history requires source_answer_id only")
            if self.verification_state is not None:
                raise ValueError("ANSWER history cannot carry verification_state")
        elif self.source_fact_id is None or self.source_answer_id is not None:
            raise ValueError("REUSED_HISTORY requires source_fact_id only")
        optional_text("verification_state", self.verification_state, 64)


class ReviewOfSystemsState(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    UNKNOWN = "UNKNOWN"
    NOT_ASKED = "NOT_ASKED"


@dataclass(frozen=True, slots=True)
class ReviewOfSystemsEntry:
    entry_id: OpaqueId
    system_key: str
    state: ReviewOfSystemsState
    source: SourceReference
    finding_key: str | None = None
    patient_wording: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        bounded_text("system_key", self.system_key, 128)
        optional_text("finding_key", self.finding_key, 128)
        optional_text("patient_wording", self.patient_wording, 2000)
        if (self.finding_key is None) == (self.patient_wording is None):
            raise ValueError("ROS entry requires exactly one finding_key or patient_wording")


@dataclass(frozen=True, slots=True)
class PriorInvestigation:
    entry_id: OpaqueId
    investigation_type: str
    source: SourceReference
    verification_state: str
    performed_at: datetime | None = None
    result_summary: str | None = field(default=None, repr=False)
    document_reference: str | None = None

    def __post_init__(self) -> None:
        bounded_text("investigation_type", self.investigation_type, 128)
        bounded_text("verification_state", self.verification_state, 64)
        optional_text("result_summary", self.result_summary, 2000)
        optional_text("document_reference", self.document_reference, 512)
        if self.performed_at is not None:
            object.__setattr__(
                self, "performed_at", normalize_utc("performed_at", self.performed_at)
            )


@dataclass(frozen=True, slots=True)
class HistorySections:
    past_medical: tuple[HistoryReference, ...] = ()
    past_surgical: tuple[HistoryReference, ...] = ()
    medications: tuple[HistoryReference, ...] = ()
    allergies: tuple[HistoryReference, ...] = ()
    family: tuple[HistoryReference, ...] = ()
    personal: tuple[HistoryReference, ...] = ()
    review_of_systems: tuple[ReviewOfSystemsEntry, ...] = ()
    prior_investigations: tuple[PriorInvestigation, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "past_medical",
            "past_surgical",
            "medications",
            "allergies",
            "family",
            "personal",
        ):
            tuple_of(name, getattr(self, name), HistoryReference)
        tuple_of("review_of_systems", self.review_of_systems, ReviewOfSystemsEntry)
        tuple_of("prior_investigations", self.prior_investigations, PriorInvestigation)


class MissingReason(StrEnum):
    REQUIRED_UNANSWERED = "REQUIRED_UNANSWERED"
    CONDITIONAL_UNANSWERED = "CONDITIONAL_UNANSWERED"
    RECONFIRMATION_REQUIRED = "RECONFIRMATION_REQUIRED"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


class Requiredness(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    CONDITIONAL = "CONDITIONAL"


class ResolutionState(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    WAIVED = "WAIVED"


@dataclass(frozen=True, slots=True)
class MissingInformation:
    missing_id: OpaqueId
    field_or_question_key: str
    reason_code: MissingReason
    requiredness: Requiredness
    source_pack_id: str
    source_pack_version: str
    source_rule_id: str
    resolution_state: ResolutionState
    resolution_answer_id: OpaqueId | None = None

    def __post_init__(self) -> None:
        for name in (
            "field_or_question_key",
            "source_pack_id",
            "source_pack_version",
            "source_rule_id",
        ):
            bounded_text(name, getattr(self, name), 128)
        if self.resolution_state is ResolutionState.RESOLVED:
            if self.resolution_answer_id is None:
                raise ValueError("resolved missing information requires resolution_answer_id")
        elif self.resolution_answer_id is not None:
            raise ValueError("resolution_answer_id is allowed only for RESOLVED")


class ContradictionStatus(StrEnum):
    OPEN = "OPEN"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True, slots=True)
class Contradiction:
    contradiction_id: OpaqueId
    field_key: str
    left_ref: SourceReference
    right_ref: SourceReference
    source_pack_id: str
    source_rule_id: str
    status: ContradictionStatus
    created_at: datetime
    resolution_ref: OpaqueId | None = None
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("field_key", "source_pack_id", "source_rule_id"):
            bounded_text(name, getattr(self, name), 128)
        created = normalize_utc("created_at", self.created_at)
        resolved = (
            None if self.resolved_at is None else normalize_utc("resolved_at", self.resolved_at)
        )
        if self.status is ContradictionStatus.RESOLVED:
            if self.resolution_ref is None or resolved is None:
                raise ValueError("resolved contradiction requires resolution_ref and resolved_at")
            if resolved < created:
                raise ValueError("resolved_at must not precede created_at")
        elif self.resolution_ref is not None or resolved is not None:
            raise ValueError("resolution fields are allowed only for RESOLVED")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "resolved_at", resolved)


@dataclass(frozen=True, slots=True)
class ClinicalIntake:
    intake_id: IntakeId
    encounter_id: OpaqueId
    status: ClinicalIntakeStatus
    started_at: datetime
    version: int
    chief_complaint: ChiefComplaint | None = None
    hpi: HistoryOfPresentIllness | None = None
    history_sections: HistorySections = field(default_factory=HistorySections)
    missing_information: tuple[MissingInformation, ...] = ()
    contradictions: tuple[Contradiction, ...] = ()
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        started = normalize_utc("started_at", self.started_at)
        completed = (
            None if self.completed_at is None else normalize_utc("completed_at", self.completed_at)
        )
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version <= 0:
            raise ValueError("version must be a positive integer")
        tuple_of("missing_information", self.missing_information, MissingInformation)
        tuple_of("contradictions", self.contradictions, Contradiction)
        if self.status is ClinicalIntakeStatus.COMPLETED:
            if completed is None:
                raise ValueError("completed_at is required for COMPLETED intake")
            if completed < started:
                raise ValueError("completed_at must not precede started_at")
        elif completed is not None:
            raise ValueError("completed_at is allowed only for COMPLETED intake")
        object.__setattr__(self, "started_at", started)
        object.__setattr__(self, "completed_at", completed)

    def transition_to(
        self, target: ClinicalIntakeStatus, *, at: datetime | None = None
    ) -> ClinicalIntake:
        if self.status is not ClinicalIntakeStatus.IN_PROGRESS or target not in {
            ClinicalIntakeStatus.COMPLETED,
            ClinicalIntakeStatus.ABANDONED,
        }:
            raise InvalidClinicalIntakeTransitionError(
                f"clinical intake cannot transition from {self.status} to {target}"
            )
        if target is ClinicalIntakeStatus.COMPLETED:
            if at is None:
                raise ValueError("completed_at is required for COMPLETED intake")
            return replace(self, status=target, completed_at=at)
        if at is not None:
            raise ValueError("a transition timestamp is accepted only for COMPLETED")
        return replace(self, status=target, completed_at=None)
