"""Full-context, text-blind structural candidate matching tests."""

from typing import Any
from uuid import UUID

import pytest
from test_document_candidate_contracts import candidate, evidence, oid
from test_document_classification import candidate as classification_candidate
from test_document_classification import request as classification_request

from app.modules.documents.candidates import (
    CandidateContractError,
    CandidateDisposition,
    CandidateReason,
    EvidenceKind,
)
from app.modules.documents.classification import DocumentType, classify_synthetic
from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    BlockKind,
    Confidence,
    ConfidenceKind,
    DocumentProcessingResult,
    NormalizedBox,
    PageResult,
    PageSelection,
    PageStatus,
    ProviderProvenance,
    ResourceUsage,
    ResultErrorCode,
    ResultStatus,
    SyntheticSourceRef,
    TableCell,
    TableResult,
    TextBlock,
)
from app.modules.documents.evidence import (
    SourceAccessStatus,
    StructuralMatchOutcome,
    StructuralMatchStatus,
    verify_structural_evidence,
)
from app.modules.documents.registry import build_synthetic_processor_registry
from app.shared.types import OpaqueId


class ExplodingText:
    def __str__(self) -> str:
        raise AssertionError("text accessed")

    def __repr__(self) -> str:
        raise AssertionError("text formatted")

    def __hash__(self) -> int:
        raise AssertionError("text hashed")


class HostileNestedObject:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError("hostile nested object traversed")


def result(
    *,
    status: ResultStatus = ResultStatus.SUCCEEDED,
    failed_second: bool = False,
    cell_box: NormalizedBox | None = None,
) -> DocumentProcessingResult:
    box = NormalizedBox(0.1, 0.2, 0.3, 0.4)
    actual_cell_box = cell_box or box
    blocks = (
        TextBlock(
            "block.1",
            BlockKind.TEXT,
            "SYNTHETIC_TOKEN_A",
            0,
            box,
            Confidence(ConfidenceKind.UNKNOWN, None),
        ),
        TextBlock(
            "block.cell",
            BlockKind.TABLE_CELL,
            "SYNTHETIC_TOKEN_B",
            1,
            box,
            Confidence(ConfidenceKind.UNKNOWN, None),
        ),
    )
    first = PageResult(
        page_number=1,
        status=PageStatus.SUCCEEDED,
        width=100,
        height=100,
        rotation_degrees=0,
        languages=(),
        blocks=blocks,
        tables=(
            TableResult(
                "table.1",
                (TableCell("cell.1", "block.cell", 0, 0, 1, 1, actual_cell_box),),
            ),
        ),
        error_code=None,
    )
    second = PageResult(
        page_number=2,
        status=PageStatus.FAILED if failed_second else PageStatus.SUCCEEDED,
        width=100,
        height=100,
        rotation_degrees=0,
        languages=(),
        blocks=() if failed_second else (),
        tables=(),
        error_code=ResultErrorCode.PAGE_FAILED if failed_second else None,
    )
    actual_status = ResultStatus.PARTIAL if failed_second else status
    return DocumentProcessingResult(
        result_contract_version=RESULT_CONTRACT_VERSION,
        request_contract_version=OCR_REQUEST_CONTRACT_VERSION,
        request_id=oid(1),
        document_id=oid(2),
        processing_attempt_id=oid(3),
        source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        requested_pages=PageSelection((1, 2)),
        status=actual_status,
        pages=(first, second),
        provenance=ProviderProvenance(
            "test.mock", "test.adapter", "v1", "synthetic.engine", "v1", "routing.v1", "in.memory"
        ),
        warnings=(),
        error_code=ResultErrorCode.PAGE_FAILED if failed_second else None,
        resource_usage=ResourceUsage(1.0, 1 if failed_second else 2, 1),
    )


def context() -> tuple[object, object]:
    source = SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA")
    decision = classify_synthetic(
        classification_request(
            (classification_candidate(DocumentType.LAB_REPORT, source=source),), source=source
        )
    )
    return decision, build_synthetic_processor_registry().resolve(decision)


def verify(value: object, processed: object) -> StructuralMatchOutcome:
    decision, receipt = context()
    return verify_structural_evidence(
        candidate=value, result=processed, classification=decision, receipt=receipt
    )


def test_matching_is_unconfirmed_deterministic_and_source_access_unverified() -> None:
    value = candidate()
    first = verify(value, result())
    second = verify(value, result())
    assert first == second
    assert first.status is StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED
    assert first.source_access is SourceAccessStatus.NOT_VERIFIED
    assert first.matched_references == 1


def test_table_cell_requires_full_table_cell_block_and_geometry_identity() -> None:
    ref = evidence(
        kind=EvidenceKind.TABLE_CELL, block_id="block.cell", table_id="table.1", cell_id="cell.1"
    )
    assert (
        verify(candidate(evidence=(ref,)), result()).status
        is StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED
    )
    with pytest.raises(CandidateContractError):
        verify(
            candidate(
                evidence=(
                    evidence(
                        kind=EvidenceKind.TABLE_CELL,
                        block_id="block.cell",
                        table_id="table.1",
                        cell_id="cell.missing",
                    ),
                )
            ),
            result(),
        )


def test_table_cell_matches_its_own_box_without_assuming_block_box_equality() -> None:
    cell_box = NormalizedBox(0.2, 0.3, 0.5, 0.6)
    ref = evidence(
        kind=EvidenceKind.TABLE_CELL,
        block_id="block.cell",
        table_id="table.1",
        cell_id="cell.1",
        box=cell_box,
    )
    assert (
        verify(candidate(evidence=(ref,)), result(cell_box=cell_box)).status
        is StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED
    )


def test_abstained_and_partial_results_never_become_positive() -> None:
    abstained = candidate(
        disposition=CandidateDisposition.ABSTAINED,
        evidence=(),
        reason=CandidateReason.SOURCE_UNAVAILABLE,
    )
    assert verify(abstained, result()).status is StructuralMatchStatus.ABSTAINED_UNVERIFIED
    assert (
        verify(candidate(), result(failed_second=True)).status
        is StructuralMatchStatus.ABSTAINED_UNVERIFIED
    )


@pytest.mark.parametrize(
    ("target", "field", "value"),
    [
        ("result", "processing_attempt_id", OpaqueId(UUID(int=9))),
        ("result", "result_contract_version", "future.v2"),
        ("decision", "selected_type", DocumentType.PRESCRIPTION),
        ("receipt", "processor_version", "v2"),
    ],
)
def test_mutated_cross_phase_metadata_is_rejected(target: str, field: str, value: object) -> None:
    processed = result()
    decision, receipt = context()
    selected: Any = {"result": processed, "decision": decision, "receipt": receipt}[target]
    object.__setattr__(selected, field, value)
    with pytest.raises(CandidateContractError):
        verify_structural_evidence(
            candidate=candidate(), result=processed, classification=decision, receipt=receipt
        )


def test_nonexistent_wrong_page_kind_box_and_stale_context_are_rejected() -> None:
    bad = (
        evidence(block_id="block.missing"),
        evidence(box=NormalizedBox(0.2, 0.2, 0.3, 0.4)),
        evidence(page_number=3),
        evidence(processing_attempt_id=oid(8)),
    )
    for ref in bad:
        with pytest.raises(CandidateContractError):
            value = candidate(evidence=(ref,), processing_attempt_id=ref.processing_attempt_id)
            verify(value, result())


def test_verifier_never_reads_or_formats_ocr_text() -> None:
    processed = result()
    object.__setattr__(processed.pages[0].blocks[0], "text", ExplodingText())
    outcome = verify(candidate(), processed)
    assert outcome.status is StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED


def test_mutated_success_result_with_failed_page_is_rejected() -> None:
    processed = result(failed_second=True)
    object.__setattr__(processed, "status", ResultStatus.SUCCEEDED)
    with pytest.raises(CandidateContractError):
        verify(candidate(), processed)


@pytest.mark.parametrize("location", ["page", "block", "provenance"])
def test_hostile_mutated_result_objects_are_type_checked_before_traversal(location: str) -> None:
    processed = result()
    hostile = HostileNestedObject()
    if location == "page":
        object.__setattr__(processed, "pages", (hostile,))
    elif location == "block":
        object.__setattr__(processed.pages[0], "blocks", (hostile,))
    else:
        object.__setattr__(processed, "provenance", hostile)
    with pytest.raises(CandidateContractError):
        verify(candidate(), processed)


def test_forged_noncanonical_requested_page_graph_is_rejected() -> None:
    processed = result()
    object.__setattr__(processed, "pages", tuple(reversed(processed.pages)))
    object.__setattr__(processed.requested_pages, "pages", (2, 1))
    with pytest.raises(CandidateContractError):
        verify(candidate(), processed)


def test_forged_duplicate_table_identity_is_rejected_even_without_duplicate_cells() -> None:
    processed = result()
    duplicate = TableResult("table.1", ())
    object.__setattr__(processed.pages[0], "tables", (*processed.pages[0].tables, duplicate))
    with pytest.raises(CandidateContractError):
        verify(candidate(), processed)


def test_outcome_constructor_rejects_unexpected_authority_field_with_closed_error() -> None:
    with pytest.raises(CandidateContractError):
        StructuralMatchOutcome(
            status=StructuralMatchStatus.ABSTAINED_UNVERIFIED,
            source_access=SourceAccessStatus.NOT_VERIFIED,
            matched_references=0,
            clinical_status="APPROVED",
        )
