"""Framework-independent clinical provenance values."""

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from app.shared.types import OpaqueId

_MAX_METADATA_LENGTH = 128
_MAX_SOURCE_REF_LENGTH = 512


class VerificationState(StrEnum):
    """Canonical trust and review states for clinical information."""

    EXTRACTED = "EXTRACTED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    PATIENT_CONFIRMED = "PATIENT_CONFIRMED"
    CLINICIAN_CONFIRMED = "CLINICIAN_CONFIRMED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class ProvenanceSourceType(StrEnum):
    """Canonical provider-neutral sources for clinical information."""

    PATIENT_REPORT = "PATIENT_REPORT"
    CAREGIVER_REPORT = "CAREGIVER_REPORT"
    CLINICIAN = "CLINICIAN"
    OCR = "OCR"
    DOCUMENT_AI = "DOCUMENT_AI"
    FHIR_IMPORT = "FHIR_IMPORT"
    ABDM_IMPORT = "ABDM_IMPORT"
    HIS_IMPORT = "HIS_IMPORT"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


def _normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _validate_optional_text(name: str, value: str | None, maximum: int) -> None:
    if value is None:
        return
    if not value.strip() or value != value.strip() or len(value) > maximum:
        raise ValueError(f"{name} must be non-blank, trimmed, and at most {maximum} characters")


@dataclass(frozen=True, slots=True, kw_only=True)
class FactProvenance:
    """Bounded source references and machine metadata for a clinical fact."""

    source_type: ProvenanceSourceType
    created_at: datetime
    source_id: OpaqueId | None = None
    source_ref: str | None = None
    extractor_type: str | None = None
    provider: str | None = None
    model_id: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    schema_version: str | None = None
    confidence: Decimal | None = None
    created_by: OpaqueId | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _normalize_utc("created_at", self.created_at))
        _validate_optional_text("source_ref", self.source_ref, _MAX_SOURCE_REF_LENGTH)
        for name in (
            "extractor_type",
            "provider",
            "model_id",
            "model_version",
            "prompt_version",
            "schema_version",
        ):
            _validate_optional_text(name, getattr(self, name), _MAX_METADATA_LENGTH)
        if self.confidence is not None and (
            not self.confidence.is_finite()
            or self.confidence < Decimal(0)
            or self.confidence > Decimal(1)
        ):
            raise ValueError("confidence must be finite and between 0 and 1")
