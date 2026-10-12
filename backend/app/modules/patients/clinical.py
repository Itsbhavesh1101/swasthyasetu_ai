"""Typed clinical values, facts, and explicit correction history."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from app.modules.provenance.public import FactProvenance, VerificationState
from app.shared.types import OpaqueId

ClinicalFactId = OpaqueId
type ClinicalTime = date | datetime


class FactType(StrEnum):
    """Canonical clinical fact categories."""

    SYMPTOM = "SYMPTOM"
    PROBLEM = "PROBLEM"
    MEDICATION = "MEDICATION"
    ALLERGY = "ALLERGY"
    PROCEDURE = "PROCEDURE"
    OBSERVATION = "OBSERVATION"
    INVESTIGATION = "INVESTIGATION"
    FAMILY_HISTORY = "FAMILY_HISTORY"
    PERSONAL_HISTORY = "PERSONAL_HISTORY"
    REVIEW_OF_SYSTEMS = "REVIEW_OF_SYSTEMS"


class ProblemStatus(StrEnum):
    ACTIVE = "ACTIVE"
    HISTORICAL = "HISTORICAL"
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"


class MedicationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    HISTORICAL = "HISTORICAL"
    STOPPED = "STOPPED"
    UNKNOWN = "UNKNOWN"


class InvalidFactSupersessionError(ValueError):
    """Raised when correction history would violate scope or trust rules."""


def _normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _normalize_optional_time(name: str, value: datetime | None) -> datetime | None:
    return None if value is None else _normalize_utc(name, value)


def _normalize_clinical_time(name: str, value: ClinicalTime | None) -> ClinicalTime | None:
    if value is None or type(value) is date:
        return value
    if isinstance(value, datetime):
        return _normalize_utc(name, value)
    raise TypeError(f"{name} must be a date or datetime")


def _validate_text(name: str, value: str, maximum: int = 256) -> None:
    if not value.strip() or value != value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be non-blank, trimmed, and at most {maximum} characters")


def _validate_optional_text(name: str, value: str | None, maximum: int = 256) -> None:
    if value is not None:
        _validate_text(name, value, maximum)


def _validate_decimal(name: str, value: Decimal, *, non_negative: bool = False) -> None:
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")
    if non_negative and value < Decimal(0):
        raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True, slots=True, kw_only=True)
class Problem:
    label: str
    status: ProblemStatus
    verification_state: VerificationState
    normalized_code: str | None = None
    onset: ClinicalTime | None = None
    resolution: ClinicalTime | None = None

    def __post_init__(self) -> None:
        _validate_text("label", self.label)
        _validate_optional_text("normalized_code", self.normalized_code, 128)
        onset = _normalize_clinical_time("onset", self.onset)
        resolution = _normalize_clinical_time("resolution", self.resolution)
        if onset is not None and resolution is not None:
            both_dates = type(onset) is date and type(resolution) is date
            both_instants = isinstance(onset, datetime) and isinstance(resolution, datetime)
            if (both_dates or both_instants) and resolution < onset:
                raise ValueError("resolution must not precede onset")
        object.__setattr__(self, "onset", onset)
        object.__setattr__(self, "resolution", resolution)


@dataclass(frozen=True, slots=True, kw_only=True)
class MedicationRecord:
    name: str
    status: MedicationStatus
    verification_state: VerificationState
    normalized_code: str | None = None
    dose: Decimal | None = None
    dose_unit: str | None = None
    route: str | None = None
    frequency: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    indication: str | None = None

    def __post_init__(self) -> None:
        _validate_text("name", self.name)
        for name in ("normalized_code", "dose_unit", "route", "frequency"):
            _validate_optional_text(name, getattr(self, name), 128)
        _validate_optional_text("indication", self.indication, 512)
        if self.dose is not None:
            _validate_decimal("dose", self.dose, non_negative=True)
        if self.start_date is not None and type(self.start_date) is not date:
            raise TypeError("start_date must be a date")
        if self.end_date is not None and type(self.end_date) is not date:
            raise TypeError("end_date must be a date")
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("end_date must not precede start_date")


@dataclass(frozen=True, slots=True, kw_only=True)
class AllergyRecord:
    substance: str
    status: str
    verification_state: VerificationState
    normalized_code: str | None = None
    reaction: str | None = None
    severity: str | None = None

    def __post_init__(self) -> None:
        _validate_text("substance", self.substance)
        _validate_text("status", self.status, 64)
        _validate_optional_text("normalized_code", self.normalized_code, 128)
        _validate_optional_text("reaction", self.reaction, 512)
        _validate_optional_text("severity", self.severity, 128)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcedureRecord:
    name: str
    verification_state: VerificationState
    normalized_code: str | None = None
    performed_at: datetime | None = None
    facility: str | None = None
    notes: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        _validate_text("name", self.name)
        _validate_optional_text("normalized_code", self.normalized_code, 128)
        _validate_optional_text("facility", self.facility, 256)
        _validate_optional_text("notes", self.notes, 2000)
        object.__setattr__(
            self, "performed_at", _normalize_optional_time("performed_at", self.performed_at)
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceRange:
    low: Decimal | None = None
    high: Decimal | None = None
    text: str | None = None

    def __post_init__(self) -> None:
        if self.low is not None:
            _validate_decimal("reference range low", self.low)
        if self.high is not None:
            _validate_decimal("reference range high", self.high)
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError("reference range low must not exceed high")
        _validate_optional_text("reference range text", self.text, 512)


@dataclass(frozen=True, slots=True, kw_only=True)
class Observation:
    observation_type: str
    value: Decimal | str
    verification_state: VerificationState
    unit: str | None = None
    reference_range: ReferenceRange | None = None
    effective_at: datetime | None = None
    normalized_value: Decimal | None = None
    normalized_unit: str | None = None
    abnormal_flag: str | None = None

    def __post_init__(self) -> None:
        _validate_text("observation_type", self.observation_type)
        if isinstance(self.value, Decimal):
            _validate_decimal("observation value", self.value)
        elif isinstance(self.value, str):
            _validate_text("observation value", self.value, 2000)
        else:
            raise TypeError("observation value must be Decimal or text")
        if self.normalized_value is not None:
            _validate_decimal("normalized_value", self.normalized_value)
        for name in ("unit", "normalized_unit", "abnormal_flag"):
            _validate_optional_text(name, getattr(self, name), 128)
        object.__setattr__(
            self, "effective_at", _normalize_optional_time("effective_at", self.effective_at)
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class InvestigationRecord:
    investigation_type: str
    status: str
    verification_state: VerificationState
    performed_at: datetime | None = None
    result_summary: str | None = field(default=None, repr=False)
    document_id: OpaqueId | None = None

    def __post_init__(self) -> None:
        _validate_text("investigation_type", self.investigation_type)
        _validate_text("status", self.status, 64)
        _validate_optional_text("result_summary", self.result_summary, 2000)
        object.__setattr__(
            self, "performed_at", _normalize_optional_time("performed_at", self.performed_at)
        )


type ClinicalValue = (
    Problem | MedicationRecord | AllergyRecord | ProcedureRecord | Observation | InvestigationRecord
)

_FACT_TYPE_BY_VALUE: tuple[tuple[type[object], FactType], ...] = (
    (Problem, FactType.PROBLEM),
    (MedicationRecord, FactType.MEDICATION),
    (AllergyRecord, FactType.ALLERGY),
    (ProcedureRecord, FactType.PROCEDURE),
    (Observation, FactType.OBSERVATION),
    (InvestigationRecord, FactType.INVESTIGATION),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClinicalFact:
    """Immutable typed fact whose provenance and trust state are mandatory."""

    fact_id: ClinicalFactId
    patient_id: OpaqueId | None
    encounter_id: OpaqueId | None
    fact_type: FactType
    value: ClinicalValue
    recorded_at: datetime
    verification_state: VerificationState
    provenance: FactProvenance
    normalized_code: str | None = None
    coding_system: str | None = None
    effective_time: datetime | None = None
    superseded_by_fact_id: ClinicalFactId | None = None

    def __post_init__(self) -> None:
        expected_type = next(
            (
                fact_type
                for value_type, fact_type in _FACT_TYPE_BY_VALUE
                if isinstance(self.value, value_type)
            ),
            None,
        )
        if expected_type is not self.fact_type:
            raise ValueError("fact_type must match the typed clinical value")
        if self.value.verification_state is not self.verification_state:
            raise ValueError("ClinicalFact and value verification_state must match")
        if self.superseded_by_fact_id == self.fact_id:
            raise ValueError("a clinical fact cannot supersede itself")
        if self.verification_state is VerificationState.SUPERSEDED:
            if self.superseded_by_fact_id is None:
                raise ValueError("SUPERSEDED fact requires superseded_by_fact_id")
        elif self.superseded_by_fact_id is not None:
            raise ValueError("superseded_by_fact_id is valid only for SUPERSEDED fact")
        _validate_optional_text("normalized_code", self.normalized_code, 128)
        _validate_optional_text("coding_system", self.coding_system, 128)
        object.__setattr__(self, "recorded_at", _normalize_utc("recorded_at", self.recorded_at))
        object.__setattr__(
            self, "effective_time", _normalize_optional_time("effective_time", self.effective_time)
        )


@dataclass(frozen=True, slots=True)
class FactSupersession:
    """The historical superseded fact and its independently retained replacement."""

    superseded: ClinicalFact
    replacement: ClinicalFact


_LOWER_THAN_CLINICIAN = frozenset(
    {
        VerificationState.EXTRACTED,
        VerificationState.LOW_CONFIDENCE,
        VerificationState.NEEDS_CONFIRMATION,
        VerificationState.PATIENT_CONFIRMED,
    }
)
_TERMINAL_FACT_STATES = frozenset({VerificationState.REJECTED, VerificationState.SUPERSEDED})


def supersede_fact(existing: ClinicalFact, replacement: ClinicalFact) -> FactSupersession:
    """Explicitly supersede a fact while preserving history and trust boundaries."""
    if existing.fact_id == replacement.fact_id:
        raise InvalidFactSupersessionError("existing and replacement IDs must be distinct")
    if existing.fact_type is not replacement.fact_type:
        raise InvalidFactSupersessionError("replacement must have the same fact type")
    if (
        existing.patient_id != replacement.patient_id
        or existing.encounter_id != replacement.encounter_id
    ):
        raise InvalidFactSupersessionError(
            "replacement must retain the same patient/encounter scope"
        )
    if existing.verification_state in _TERMINAL_FACT_STATES:
        raise InvalidFactSupersessionError(
            "rejected or superseded facts cannot be superseded again"
        )
    if replacement.verification_state in _TERMINAL_FACT_STATES:
        raise InvalidFactSupersessionError("replacement must be an active fact")
    if (
        existing.verification_state is VerificationState.CLINICIAN_CONFIRMED
        and replacement.verification_state in _LOWER_THAN_CLINICIAN
    ):
        raise InvalidFactSupersessionError(
            "clinician-confirmed fact cannot be superseded by lower-trust replacement"
        )
    superseded_value = replace(existing.value, verification_state=VerificationState.SUPERSEDED)
    superseded = replace(
        existing,
        value=superseded_value,
        verification_state=VerificationState.SUPERSEDED,
        superseded_by_fact_id=replacement.fact_id,
    )
    return FactSupersession(superseded=superseded, replacement=replacement)
