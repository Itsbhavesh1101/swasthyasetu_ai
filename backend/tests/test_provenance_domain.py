"""P5-A provenance domain tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.modules.provenance.public import (
    FactProvenance,
    ProvenanceSourceType,
    VerificationState,
)
from app.shared.types import OpaqueId


def test_provenance_and_verification_enums_are_canonical() -> None:
    assert {value.value for value in ProvenanceSourceType} == {
        "PATIENT_REPORT",
        "CAREGIVER_REPORT",
        "CLINICIAN",
        "OCR",
        "DOCUMENT_AI",
        "FHIR_IMPORT",
        "ABDM_IMPORT",
        "HIS_IMPORT",
        "MODEL_INFERENCE",
        "ADMIN",
        "SYSTEM",
    }
    assert {value.value for value in VerificationState} == {
        "EXTRACTED",
        "LOW_CONFIDENCE",
        "NEEDS_CONFIRMATION",
        "PATIENT_CONFIRMED",
        "CLINICIAN_CONFIRMED",
        "REJECTED",
        "SUPERSEDED",
    }


@pytest.mark.parametrize("confidence", [Decimal("0"), Decimal("0.5"), Decimal("1")])
def test_provenance_accepts_finite_confidence_bounds(confidence: Decimal) -> None:
    provenance = FactProvenance(
        source_type=ProvenanceSourceType.OCR,
        source_id=OpaqueId.new(),
        source_ref="document/object-reference",
        extractor_type="prescription",
        provider="synthetic-provider",
        model_id="synthetic-model",
        model_version="v1",
        prompt_version="p1",
        schema_version="s1",
        confidence=confidence,
        created_at=datetime(2026, 10, 12, 8, tzinfo=UTC),
        created_by=None,
    )

    assert provenance.confidence == confidence
    with pytest.raises(FrozenInstanceError):
        provenance.confidence = Decimal("0.2")  # type: ignore[misc]


@pytest.mark.parametrize(
    "confidence",
    [Decimal("-0.0001"), Decimal("1.0001"), Decimal("NaN"), Decimal("Infinity")],
)
def test_provenance_rejects_invalid_confidence(confidence: Decimal) -> None:
    with pytest.raises(ValueError, match="confidence"):
        FactProvenance(
            source_type=ProvenanceSourceType.DOCUMENT_AI,
            created_at=datetime(2026, 10, 12, 8, tzinfo=UTC),
            confidence=confidence,
        )


def test_provenance_rejects_naive_time_and_normalizes_offset_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        FactProvenance(
            source_type=ProvenanceSourceType.PATIENT_REPORT,
            created_at=datetime(2026, 10, 12, 8),
        )

    offset = timezone(timedelta(hours=5, minutes=30))
    provenance = FactProvenance(
        source_type=ProvenanceSourceType.CLINICIAN,
        created_at=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
    )
    assert provenance.created_at == datetime(2026, 10, 12, 8, tzinfo=UTC)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_ref", " "),
        ("extractor_type", "x" * 129),
        ("provider", "x" * 129),
        ("model_id", "x" * 129),
        ("model_version", "x" * 129),
        ("prompt_version", "x" * 129),
        ("schema_version", "x" * 129),
    ],
)
def test_provenance_rejects_blank_or_unbounded_machine_metadata(field: str, value: str) -> None:
    values: dict[str, object] = {
        "source_type": ProvenanceSourceType.SYSTEM,
        "created_at": datetime(2026, 10, 12, 8, tzinfo=UTC),
        field: value,
    }
    with pytest.raises(ValueError, match=field):
        FactProvenance(**values)  # type: ignore[arg-type]


def test_provenance_repr_contains_references_but_no_raw_content_bucket() -> None:
    marker = "synthetic-reference-not-content"
    provenance = FactProvenance(
        source_type=ProvenanceSourceType.SYSTEM,
        source_ref=marker,
        created_at=datetime(2026, 10, 12, 8, tzinfo=UTC),
    )

    assert marker in repr(provenance)
    assert not hasattr(provenance, "raw_content")
    assert not hasattr(provenance, "chain_of_thought")
