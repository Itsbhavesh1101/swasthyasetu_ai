"""Framework-independent patient profile domain values."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum

from app.shared.types import OpaqueId

PatientId = OpaqueId


class PatientStatus(StrEnum):
    """Canonical patient lifecycle states."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MERGED = "MERGED"
    DELETED_PENDING = "DELETED_PENDING"


def _normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _validate_text(name: str, value: str, maximum: int) -> None:
    if not value.strip() or value != value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be non-blank, trimmed, and at most {maximum} characters")


def _validate_optional_text(name: str, value: str | None, maximum: int) -> None:
    if value is not None:
        _validate_text(name, value, maximum)


@dataclass(frozen=True, slots=True, kw_only=True)
class PatientIdentifier:
    """Namespaced patient identifier with a privacy-safe representation."""

    identifier_id: OpaqueId
    patient_id: PatientId
    system: str
    value: str = field(repr=False)
    verified: bool
    source: str
    use: str | None = None

    def __post_init__(self) -> None:
        _validate_text("system", self.system, 128)
        _validate_text("value", self.value, 512)
        _validate_optional_text("use", self.use, 64)
        _validate_text("source", self.source, 128)
        if not isinstance(self.verified, bool):
            raise TypeError("verified must be a boolean")


@dataclass(frozen=True, slots=True)
class PatientDemographics:
    """Minimal optional demographics without inferred relationships."""

    date_of_birth: date | None = None
    age_years: int | None = None
    administrative_sex: str | None = None
    gender_identity: str | None = None
    pregnancy_status: str | None = None
    location_context: str | None = None

    def __post_init__(self) -> None:
        if self.date_of_birth is not None and type(self.date_of_birth) is not date:
            raise TypeError("date_of_birth must be a date")
        if self.age_years is not None and (
            isinstance(self.age_years, bool)
            or not isinstance(self.age_years, int)
            or self.age_years < 0
        ):
            raise ValueError("age_years must be a non-negative integer")
        for name in (
            "administrative_sex",
            "gender_identity",
            "pregnancy_status",
            "location_context",
        ):
            _validate_optional_text(name, getattr(self, name), 256)


@dataclass(frozen=True, slots=True)
class Patient:
    """Authoritative patient profile without identity, consent, or history buckets."""

    patient_id: PatientId
    status: PatientStatus
    created_at: datetime
    updated_at: datetime
    preferred_language: str | None = None
    demographics: PatientDemographics | None = None
    identifiers: tuple[PatientIdentifier, ...] = ()

    def __post_init__(self) -> None:
        created_at = _normalize_utc("created_at", self.created_at)
        updated_at = _normalize_utc("updated_at", self.updated_at)
        if updated_at < created_at:
            raise ValueError("updated_at must not precede created_at")
        _validate_optional_text("preferred_language", self.preferred_language, 64)
        if not isinstance(self.identifiers, tuple):
            raise TypeError("identifiers must be a tuple")
        if any(identifier.patient_id != self.patient_id for identifier in self.identifiers):
            raise ValueError("identifiers must belong to the same patient")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)
