"""Strict synthetic-only candidate contract tests."""

import traceback
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

import pytest

from app.modules.documents.candidates import (
    CANDIDATE_SCHEMA_VERSION,
    EVIDENCE_SCHEMA_VERSION,
    MAX_EVIDENCE_REFERENCES,
    CandidateAuthority,
    CandidateContractCode,
    CandidateContractError,
    CandidateDisposition,
    CandidateReason,
    EvidenceKind,
    StructuralEvidenceRef,
    SyntheticCandidateRef,
    SyntheticDocumentCandidate,
    snapshot_candidate,
)
from app.modules.documents.classification import DocumentType
from app.modules.documents.contracts import (
    MAX_PAGES,
    Confidence,
    ConfidenceKind,
    NormalizedBox,
    SyntheticSourceRef,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def oid(value: int) -> OpaqueId:
    return OpaqueId(UUID(int=value))


def evidence(number: int = 1, **changes: Any) -> StructuralEvidenceRef:
    values: dict[str, object] = {
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "request_id": oid(1),
        "document_id": oid(2),
        "processing_attempt_id": oid(3),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        "routing_version": "routing.v1",
        "page_number": 1,
        "kind": EvidenceKind.BLOCK,
        "block_id": f"block.{number}",
        "box": NormalizedBox(0.1, 0.2, 0.3, 0.4),
    }
    values.update(changes)
    return StructuralEvidenceRef(**values)  # type: ignore[arg-type]


def candidate(**changes: Any) -> SyntheticDocumentCandidate:
    values: dict[str, object] = {
        "candidate_ref": SyntheticCandidateRef("SYNTHETIC_CANDIDATE_A"),
        "request_id": oid(1),
        "document_id": oid(2),
        "processing_attempt_id": oid(3),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        "document_type": DocumentType.LAB_REPORT,
        "processor_id": "LabReportProcessor",
        "processor_version": "v1",
        "candidate_schema_version": CANDIDATE_SCHEMA_VERSION,
        "routing_version": "routing.v1",
        "disposition": CandidateDisposition.UNCONFIRMED,
        "authority": CandidateAuthority.ENGINEERING_ONLY,
        "evidence": (evidence(),),
        "confidence": Confidence(ConfidenceKind.UNKNOWN, None),
        "reason": CandidateReason.STRUCTURAL_REFERENCE_ONLY,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticDocumentCandidate(**values)  # type: ignore[arg-type]


def test_candidate_is_detached_immutable_utc_and_repr_safe() -> None:
    supplied = evidence()
    value = candidate(evidence=(supplied,), created_at=NOW.astimezone(timezone(timedelta(hours=5))))
    assert value.created_at.tzinfo is UTC
    assert value.evidence[0] is not supplied
    with pytest.raises(FrozenInstanceError):
        value.reason = CandidateReason.NO_EVIDENCE  # type: ignore[misc]
    rendered = repr(value)
    for secret in ("SYNTHETIC_CANDIDATE_A", "SYNTHETIC_SOURCE_ALPHA", "block.1"):
        assert secret not in rendered


@pytest.mark.parametrize(
    "changes",
    [
        {"page_number": True},
        {"page_number": 1.0},
        {"kind": "BLOCK"},
        {"evidence_schema_version": "future.v2"},
        {"block_id": "INVALID TOKEN"},
        {"kind": EvidenceKind.BLOCK, "table_id": "table.1", "cell_id": "cell.1"},
        {"kind": EvidenceKind.TABLE_CELL},
        {"request_id": oid(2)},
    ],
)
def test_evidence_rejects_hostile_values(changes: dict[str, object]) -> None:
    with pytest.raises(CandidateContractError):
        evidence(**cast(Any, changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"document_type": DocumentType.UNKNOWN},
        {"document_type": "LAB_REPORT"},
        {"processor_id": "bad.module:Processor"},
        {"processor_version": "latest"},
        {"candidate_schema_version": "candidate.v2"},
        {"disposition": "UNCONFIRMED"},
        {"authority": "CLINICIAN_CONFIRMED"},
        {"confidence": Confidence(ConfidenceKind.RECOGNIZER, 0.9)},
        {"created_at": datetime(2026, 1, 1)},
        {"evidence": [evidence()]},
        {"evidence": ()},
    ],
)
def test_candidate_rejects_invalid_or_authority_claiming_values(changes: dict[str, object]) -> None:
    with pytest.raises(CandidateContractError):
        candidate(**changes)


def test_abstention_is_closed_and_cannot_carry_evidence() -> None:
    value = candidate(
        disposition=CandidateDisposition.ABSTAINED, evidence=(), reason=CandidateReason.NO_EVIDENCE
    )
    assert value.disposition is CandidateDisposition.ABSTAINED
    with pytest.raises(CandidateContractError):
        candidate(
            disposition=CandidateDisposition.ABSTAINED, reason=CandidateReason.SOURCE_UNAVAILABLE
        )


def test_candidate_reference_cannot_claim_clinical_authority() -> None:
    with pytest.raises(CandidateContractError):
        SyntheticCandidateRef("SYNTHETIC_CLINICIAN_CONFIRMED")


def test_evidence_order_is_canonical_while_duplicates_context_and_bounds_fail_closed() -> None:
    first, second = evidence(1), evidence(2)
    canonical = candidate(evidence=(first, second))
    permuted = candidate(evidence=(second, first))
    assert permuted.evidence == canonical.evidence
    with pytest.raises(CandidateContractError):
        candidate(evidence=(first, first))
    with pytest.raises(CandidateContractError):
        candidate(evidence=(evidence(1, source=SyntheticSourceRef("SYNTHETIC_SOURCE_BETA")),))
    with pytest.raises(CandidateContractError) as raised:
        candidate(
            evidence=tuple(evidence(index + 1) for index in range(MAX_EVIDENCE_REFERENCES + 1))
        )
    assert raised.value.code is CandidateContractCode.LIMIT_EXCEEDED


def test_unexpected_fields_and_content_free_privacy_canary() -> None:
    canary = "private-canary"
    with pytest.raises(CandidateContractError) as raised:
        candidate(private_narrative=canary)
    assert raised.value.code is CandidateContractCode.UNEXPECTED_FIELD
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))
    with pytest.raises(CandidateContractError):
        evidence(extracted_value=canary)


def test_evidence_page_is_bounded_by_processing_contract() -> None:
    with pytest.raises(CandidateContractError) as raised:
        evidence(page_number=MAX_PAGES + 1)
    assert raised.value.code is CandidateContractCode.LIMIT_EXCEEDED


def test_mutation_is_rejected_at_snapshot_boundary() -> None:
    value = candidate()
    object.__setattr__(value.evidence[0], "page_number", False)
    with pytest.raises(CandidateContractError):
        snapshot_candidate(value)
    object.__setattr__(value, "authority", cast(Any, "APPROVED"))
    with pytest.raises(CandidateContractError):
        snapshot_candidate(value)
