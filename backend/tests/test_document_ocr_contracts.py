"""Strict synthetic parser/OCR contract tests."""

import traceback
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from math import inf, nan
from typing import Any, cast
from uuid import UUID

import pytest

from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    PARSER_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    BlockKind,
    Confidence,
    ConfidenceKind,
    DocumentContractCode,
    DocumentContractError,
    DocumentParserRequest,
    DocumentProcessingResult,
    LanguageDescriptor,
    NormalizedBox,
    OCRMode,
    OCRRequest,
    PageResult,
    PageSelection,
    PageStatus,
    ParserMode,
    ProviderProvenance,
    ResourceProfile,
    ResourceUsage,
    ResultErrorCode,
    ResultStatus,
    SyntheticSourceRef,
    TableCell,
    TableResult,
    TextBlock,
    WarningCode,
)
from app.modules.documents.ports import DocumentParserPort, OCRPort
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def oid(n: int) -> OpaqueId:
    return OpaqueId(UUID(int=n))


def profile() -> ResourceProfile:
    return ResourceProfile(4, 8, 2, 8)


def request(*, pages: tuple[int, ...] = (1, 2), **changes: Any) -> OCRRequest:
    values: dict[str, object] = {
        "request_id": oid(1),
        "document_id": oid(2),
        "processing_attempt_id": oid(3),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        "pages": PageSelection(pages),
        "mode": OCRMode.LAYOUT,
        "language_hints": ("en",),
        "script_hints": ("Latn",),
        "contract_version": OCR_REQUEST_CONTRACT_VERSION,
        "routing_version": "routing.v1",
        "requested_at": NOW,
        "deadline_at": NOW + timedelta(seconds=5),
        "resource_profile": profile(),
        "correlation_id": "test.correlation",
    }
    values.update(changes)
    return OCRRequest(**values)  # type: ignore[arg-type]


def box() -> NormalizedBox:
    return NormalizedBox(0.1, 0.2, 0.3, 0.4)


def block(number: int = 1, order: int = 0) -> TextBlock:
    return TextBlock(
        f"block.{number}",
        BlockKind.TEXT,
        f"SYNTHETIC_TOKEN_{number}",
        order,
        box(),
        Confidence(ConfidenceKind.RECOGNIZER, 0.75),
    )


def page(number: int, *, failed: bool = False) -> PageResult:
    return PageResult(
        page_number=number,
        status=PageStatus.FAILED if failed else PageStatus.SUCCEEDED,
        width=100,
        height=200,
        rotation_degrees=0,
        languages=()
        if failed
        else (LanguageDescriptor("en", "Latn", Confidence(ConfidenceKind.UNKNOWN, None)),),
        blocks=() if failed else (block(number),),
        tables=(),
        error_code=ResultErrorCode.PAGE_FAILED if failed else None,
    )


def provenance() -> ProviderProvenance:
    return ProviderProvenance(
        "test.mock", "test.adapter", "v1", "synthetic.engine", "v1", "routing.v1", "in.memory"
    )


def result(
    *,
    status: ResultStatus = ResultStatus.SUCCEEDED,
    pages: tuple[PageResult, ...] | None = None,
    error: ResultErrorCode | None = None,
) -> DocumentProcessingResult:
    actual = pages or (page(1), page(2))
    return DocumentProcessingResult(
        result_contract_version=RESULT_CONTRACT_VERSION,
        request_contract_version=OCR_REQUEST_CONTRACT_VERSION,
        request_id=oid(1),
        document_id=oid(2),
        processing_attempt_id=oid(3),
        source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        requested_pages=PageSelection((1, 2)),
        status=status,
        pages=actual,
        provenance=provenance(),
        warnings=(),
        error_code=error,
        resource_usage=ResourceUsage(
            5.0, sum(item.status is PageStatus.SUCCEEDED for item in actual), 1024
        ),
    )


def test_distinct_ports_and_native_raster_modes() -> None:
    assert DocumentParserPort.__name__ != OCRPort.__name__
    parser = DocumentParserRequest(
        request_id=oid(1),
        document_id=oid(2),
        processing_attempt_id=oid(3),
        source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        pages=PageSelection((1,)),
        mode=ParserMode.NATIVE_TEXT,
        language_hints=(),
        script_hints=(),
        contract_version=PARSER_REQUEST_CONTRACT_VERSION,
        routing_version="routing.v1",
        requested_at=NOW,
        deadline_at=NOW + timedelta(seconds=1),
        resource_profile=profile(),
    )
    assert parser.mode is ParserMode.NATIVE_TEXT
    with pytest.raises(DocumentContractError):
        request(mode=ParserMode.NATIVE_TEXT)


@pytest.mark.parametrize("pages", [(), (0,), (2, 1), (1, 1), tuple(range(1, 34))])
def test_page_selection_fails_closed(pages: tuple[int, ...]) -> None:
    with pytest.raises(DocumentContractError):
        PageSelection(pages)


@pytest.mark.parametrize(
    "changes",
    [
        {"contract_version": "ocr-request.v2"},
        {"document_id": oid(1)},
        {"deadline_at": NOW},
        {"deadline_at": datetime(2026, 1, 1)},
        {"language_hints": ("en", "en")},
        {"language_hints": ("bad hint",)},
        {"source": SyntheticSourceRef("SYNTHETIC_SOURCE_OK"), "correlation_id": "has space"},
    ],
)
def test_request_rejects_versions_deadlines_and_hints(changes: dict[str, Any]) -> None:
    with pytest.raises(DocumentContractError):
        request(**changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"language_hints": (["private-canary"],)},
        {"script_hints": (False,)},
    ],
)
def test_request_rejects_hostile_hint_types_with_typed_content_free_error(
    changes: dict[str, Any],
) -> None:
    with pytest.raises(DocumentContractError) as raised:
        request(**changes)
    assert raised.value.code is DocumentContractCode.INVALID_VALUE
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))


def test_request_normalizes_aware_deadline_to_utc_and_is_immutable() -> None:
    value = request(
        deadline_at=(NOW + timedelta(hours=5, seconds=5)).astimezone(timezone(timedelta(hours=5)))
    )
    assert value.deadline_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        value.mode = OCRMode.TEXT  # type: ignore[misc]
    assert "SYNTHETIC_SOURCE_ALPHA" not in repr(value)


@pytest.mark.parametrize(
    "coords", [(nan, 0, 1, 1), (0, 0, inf, 1), (-0.1, 0, 1, 1), (0.5, 0, 0.5, 1), (0, 1, 1, 0)]
)
def test_boxes_reject_nonfinite_out_of_range_and_unordered(coords: tuple[float, ...]) -> None:
    with pytest.raises(DocumentContractError):
        NormalizedBox(*coords)


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        (ConfidenceKind.UNKNOWN, 0.0),
        (ConfidenceKind.RECOGNIZER, None),
        (ConfidenceKind.HEURISTIC, nan),
        (ConfidenceKind.RECOGNIZER, -0.1),
        (ConfidenceKind.RECOGNIZER, 1.1),
    ],
)
def test_confidence_has_explicit_unknown_semantics(
    kind: ConfidenceKind, value: float | None
) -> None:
    with pytest.raises(DocumentContractError):
        Confidence(kind, value)
    unknown = Confidence(ConfidenceKind.UNKNOWN, None)
    assert unknown.value is None


def test_sensitive_text_is_hidden_and_authority_tokens_rejected() -> None:
    value = block()
    assert value.text not in repr(value)
    with pytest.raises(DocumentContractError) as raised:
        replace(value, text="SYNTHETIC_CLINICIAN_CONFIRMED")
    assert "CLINICIAN" not in str(raised.value)


@pytest.mark.parametrize(("language", "script"), [(False, "Latn"), ("en", ["private-canary"])])
def test_language_descriptor_rejects_nonstring_fields_without_raw_type_errors(
    language: object, script: object
) -> None:
    with pytest.raises(DocumentContractError) as raised:
        LanguageDescriptor(
            cast(Any, language),
            cast(Any, script),
            Confidence(ConfidenceKind.UNKNOWN, None),
        )
    assert raised.value.code is DocumentContractCode.INVALID_TYPE
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))


@pytest.mark.parametrize("rotation", [False, 0.0, 90.0])
def test_page_rejects_noninteger_rotation_lookalikes(rotation: object) -> None:
    with pytest.raises(DocumentContractError) as raised:
        replace(page(1), rotation_degrees=rotation)  # type: ignore[arg-type]
    assert raised.value.code is DocumentContractCode.INVALID_TYPE


def test_page_rejects_unsorted_duplicate_and_dangling_table_cells() -> None:
    with pytest.raises(DocumentContractError):
        replace(page(1), blocks=(block(2, 1), block(1, 0)))
    cell = TableCell("cell.1", "missing.block", 0, 0, 1, 1, box())
    with pytest.raises(DocumentContractError):
        replace(page(1), tables=(TableResult("table.1", (cell,)),))


def table_cell_block(number: int = 1, order: int = 0) -> TextBlock:
    return TextBlock(
        f"cell.block.{number}",
        BlockKind.TABLE_CELL,
        f"SYNTHETIC_CELL_{number}",
        order,
        box(),
        Confidence(ConfidenceKind.RECOGNIZER, 0.75),
    )


def test_page_rejects_duplicate_tables_and_non_cell_block_linkage() -> None:
    linked = table_cell_block()
    cell = TableCell("cell.1", linked.block_id, 0, 0, 1, 1, box())
    table = TableResult("table.1", (cell,))
    valid = replace(page(1), blocks=(linked,), tables=(table,))
    assert valid.tables == (table,)
    with pytest.raises(DocumentContractError) as duplicate:
        replace(valid, tables=(table, table))
    assert duplicate.value.code is DocumentContractCode.DUPLICATE_IDENTITY

    text = block()
    wrong_kind = TableResult(
        "table.2",
        (TableCell("cell.2", text.block_id, 0, 0, 1, 1, box()),),
    )
    with pytest.raises(DocumentContractError) as mismatched:
        replace(page(1), blocks=(text,), tables=(wrong_kind,))
    assert mismatched.value.code is DocumentContractCode.IDENTITY_MISMATCH


@pytest.mark.parametrize(
    ("row", "column", "row_span", "column_span"),
    [
        (256, 0, 1, 1),
        (0, 256, 1, 1),
        (0, 0, 257, 1),
        (0, 0, 1, 257),
        (255, 0, 2, 1),
        (0, 255, 1, 2),
    ],
)
def test_table_cells_reject_oversized_or_overflowing_grid_coordinates(
    row: int, column: int, row_span: int, column_span: int
) -> None:
    with pytest.raises(DocumentContractError) as raised:
        TableCell("cell.1", "cell.block.1", row, column, row_span, column_span, box())
    assert raised.value.code is DocumentContractCode.LIMIT_EXCEEDED


def test_failed_page_cannot_carry_payload() -> None:
    with pytest.raises(DocumentContractError):
        replace(page(1, failed=True), blocks=(block(),))
    with pytest.raises(DocumentContractError):
        replace(
            page(1, failed=True),
            languages=(LanguageDescriptor("en", "Latn", Confidence(ConfidenceKind.UNKNOWN, None)),),
        )


def test_result_error_codes_are_closed_and_content_free_at_each_constructor() -> None:
    canary = "private-canary-result-error"
    with pytest.raises(DocumentContractError) as page_error:
        replace(page(1, failed=True), error_code=canary)  # type: ignore[arg-type]
    with pytest.raises(DocumentContractError) as failed_error:
        result(
            status=ResultStatus.FAILED,
            pages=(page(1, failed=True), page(2, failed=True)),
            error=cast(Any, canary),
        )
    with pytest.raises(DocumentContractError) as partial_error:
        result(
            status=ResultStatus.PARTIAL,
            pages=(page(1), page(2, failed=True)),
            error=cast(Any, canary),
        )
    for raised in (page_error, failed_error, partial_error):
        assert raised.value.code is DocumentContractCode.INVALID_TYPE
        rendered = "".join(traceback.format_exception(raised.value))
        assert canary not in rendered


def test_result_reconciles_success_partial_and_failure_coverage() -> None:
    success = result()
    success.assert_matches(request())
    partial_pages = (page(1), page(2, failed=True))
    partial = result(
        status=ResultStatus.PARTIAL, pages=partial_pages, error=ResultErrorCode.PAGE_FAILED
    )
    assert partial.status is ResultStatus.PARTIAL
    failed_pages = (page(1, failed=True), page(2, failed=True))
    failed = result(
        status=ResultStatus.FAILED, pages=failed_pages, error=ResultErrorCode.ENGINE_UNAVAILABLE
    )
    assert all(not item.blocks for item in failed.pages)
    with pytest.raises(DocumentContractError):
        result(status=ResultStatus.SUCCEEDED, pages=partial_pages)
    with pytest.raises(DocumentContractError):
        replace(success, request_id=oid(99)).assert_matches(request())
    with pytest.raises(DocumentContractError):
        replace(
            success,
            provenance=replace(provenance(), routing_version="routing.v2"),
        ).assert_matches(request())


def test_result_rejects_missing_reordered_pages_and_duplicate_warnings() -> None:
    with pytest.raises(DocumentContractError):
        result(pages=(page(1),))
    with pytest.raises(DocumentContractError):
        result(pages=(page(2), page(1)))
    with pytest.raises(DocumentContractError):
        replace(result(), warnings=(WarningCode.LOW_CONFIDENCE, WarningCode.LOW_CONFIDENCE))


def test_errors_are_typed_and_content_free() -> None:
    canary = "SYNTHETIC_SOURCE_PRIVATE_CANARY"
    with pytest.raises(DocumentContractError) as raised:
        SyntheticSourceRef(canary + "/path")
    assert raised.value.code is DocumentContractCode.INVALID_VALUE
    assert canary not in repr(raised.value)
