"""Stable synthetic request/result builders for test-only OCR evidence."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.modules.documents.contracts import (
    OCR_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    BlockKind,
    Confidence,
    ConfidenceKind,
    DocumentProcessingResult,
    NormalizedBox,
    OCRMode,
    OCRRequest,
    PageResult,
    PageSelection,
    PageStatus,
    ProviderProvenance,
    ResourceProfile,
    ResourceUsage,
    ResultErrorCode,
    ResultStatus,
    SyntheticSourceRef,
    TextBlock,
    WarningCode,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def request(*, document_id_seed: int = 2) -> OCRRequest:
    return OCRRequest(
        request_id=oid(1),
        document_id=oid(document_id_seed),
        processing_attempt_id=oid(3),
        source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        pages=PageSelection((1, 2)),
        mode=OCRMode.LAYOUT,
        language_hints=("en",),
        script_hints=("Latn",),
        contract_version=OCR_REQUEST_CONTRACT_VERSION,
        routing_version="routing.v1",
        requested_at=NOW,
        deadline_at=NOW + timedelta(seconds=5),
        resource_profile=ResourceProfile(2, 4, 1, 4),
        correlation_id="test.correlation",
    )


def _page(number: int, *, failed: bool) -> PageResult:
    blocks = (
        ()
        if failed
        else (
            TextBlock(
                block_id=f"block.{number}",
                kind=BlockKind.TEXT,
                text=f"SYNTHETIC_TOKEN_{number}",
                reading_order=0,
                box=NormalizedBox(0.1, 0.1, 0.9, 0.2),
                confidence=Confidence(ConfidenceKind.RECOGNIZER, 0.75),
            ),
        )
    )
    return PageResult(
        number,
        PageStatus.FAILED if failed else PageStatus.SUCCEEDED,
        100,
        200,
        0,
        (),
        blocks,
        (),
        ResultErrorCode.PAGE_FAILED if failed else None,
    )


def result(*, status: ResultStatus = ResultStatus.SUCCEEDED) -> DocumentProcessingResult:
    failed = status in {ResultStatus.FAILED, ResultStatus.NEEDS_FALLBACK}
    pages = (_page(1, failed=failed), _page(2, failed=failed or status is ResultStatus.PARTIAL))
    error = None
    warnings: tuple[WarningCode, ...] = ()
    if status is ResultStatus.PARTIAL:
        error = ResultErrorCode.PAGE_FAILED
        warnings = (WarningCode.PAGE_INCOMPLETE,)
    elif status is ResultStatus.FAILED:
        error = ResultErrorCode.ENGINE_UNAVAILABLE
    elif status is ResultStatus.NEEDS_FALLBACK:
        error = ResultErrorCode.UNSUPPORTED_INPUT
    return DocumentProcessingResult(
        result_contract_version=RESULT_CONTRACT_VERSION,
        request_contract_version=OCR_REQUEST_CONTRACT_VERSION,
        request_id=oid(1),
        document_id=oid(2),
        processing_attempt_id=oid(3),
        source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        requested_pages=PageSelection((1, 2)),
        status=status,
        pages=pages,
        provenance=ProviderProvenance(
            "test.mock",
            "test.mock.adapter",
            "v1",
            "synthetic.engine",
            "v1",
            "routing.v1",
            "in.memory",
        ),
        warnings=warnings,
        error_code=error,
        resource_usage=ResourceUsage(
            5.0, sum(page.status is PageStatus.SUCCEEDED for page in pages)
        ),
    )
