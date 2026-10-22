"""Pure structural matching for synthetic, unconfirmed document candidates."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.modules.documents.candidates import (
    MAX_EVIDENCE_REFERENCES,
    CandidateContractCode,
    CandidateContractError,
    CandidateDisposition,
    EvidenceKind,
    snapshot_candidate,
)
from app.modules.documents.classification import (
    ClassificationContractError,
    ClassificationDecision,
    ClassificationDisposition,
)
from app.modules.documents.contracts import (
    MAX_BLOCKS_PER_PAGE,
    MAX_CELLS_PER_TABLE,
    MAX_HINTS,
    MAX_PAGES,
    MAX_TABLES_PER_PAGE,
    OCR_REQUEST_CONTRACT_VERSION,
    PARSER_REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    BlockKind,
    Confidence,
    DocumentContractError,
    DocumentProcessingResult,
    LanguageDescriptor,
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
    WarningCode,
)
from app.modules.documents.registry import (
    ProcessorAuthority,
    ProcessorDisposition,
    ProcessorRegistryError,
    ProcessorResolutionReceipt,
    RegistryResolutionStatus,
)
from app.shared.types import OpaqueId

_TOKEN: Final = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")


class StructuralMatchStatus(StrEnum):
    STRUCTURALLY_MATCHED_UNCONFIRMED = "STRUCTURALLY_MATCHED_UNCONFIRMED"
    ABSTAINED_UNVERIFIED = "ABSTAINED_UNVERIFIED"


class SourceAccessStatus(StrEnum):
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True, slots=True, init=False)
class StructuralMatchOutcome:
    status: StructuralMatchStatus
    source_access: SourceAccessStatus
    matched_references: int

    def __init__(
        self,
        status: StructuralMatchStatus,
        source_access: SourceAccessStatus,
        matched_references: int,
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise CandidateContractError(CandidateContractCode.UNEXPECTED_FIELD)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_access", source_access)
        object.__setattr__(self, "matched_references", matched_references)
        self.__post_init__()

    def __post_init__(self) -> None:
        if (
            type(self.status) is not StructuralMatchStatus
            or self.source_access is not SourceAccessStatus.NOT_VERIFIED
        ):
            raise CandidateContractError(CandidateContractCode.INVALID_TYPE)
        if (
            type(self.matched_references) is not int
            or not 0 <= self.matched_references <= MAX_EVIDENCE_REFERENCES
        ):
            raise CandidateContractError(CandidateContractCode.INVALID_VALUE)
        if (self.status is StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED) != (
            self.matched_references > 0
        ):
            raise CandidateContractError(CandidateContractCode.INVALID_STATUS)


def _fail(code: CandidateContractCode) -> CandidateContractError:
    return CandidateContractError(code)


def _snapshot_decision(value: object) -> ClassificationDecision:
    if type(value) is not ClassificationDecision:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return ClassificationDecision(
            request_id=value.request_id,
            document_id=value.document_id,
            processing_attempt_id=value.processing_attempt_id,
            source=value.source,
            candidates=value.candidates,
            schema_version=value.schema_version,
            config_version=value.config_version,
            authority=value.authority,
            disposition=value.disposition,
            reason=value.reason,
            selected_type=value.selected_type,
        )
    except (ClassificationContractError, ValueError, TypeError, AttributeError):
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH) from None


def _snapshot_receipt(value: object) -> ProcessorResolutionReceipt:
    if type(value) is not ProcessorResolutionReceipt:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return ProcessorResolutionReceipt(
            registry_schema_version=value.registry_schema_version,
            receipt_schema_version=value.receipt_schema_version,
            classification_schema_version=value.classification_schema_version,
            document_type=value.document_type,
            processor_id=value.processor_id,
            processor_version=value.processor_version,
            parser_modes=value.parser_modes,
            ocr_modes=value.ocr_modes,
            input_schema_versions=value.input_schema_versions,
            output_schema_version=value.output_schema_version,
            authority=value.authority,
            processor_disposition=value.processor_disposition,
            status=value.status,
            reason=value.reason,
        )
    except (ProcessorRegistryError, ValueError, TypeError, AttributeError):
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH) from None


def _safe_box(value: object) -> NormalizedBox:
    if type(value) is not NormalizedBox:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return NormalizedBox(value.left, value.top, value.right, value.bottom)
    except (TypeError, ValueError, AttributeError):
        raise _fail(CandidateContractCode.INVALID_VALUE) from None


def _safe_id(value: object) -> OpaqueId:
    if type(value) is not OpaqueId or type(value.value) is not UUID:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    return OpaqueId(value.value)


def _safe_source(value: object) -> SyntheticSourceRef:
    if type(value) is not SyntheticSourceRef or type(value.value) is not str:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return SyntheticSourceRef(value.value)
    except DocumentContractError:
        raise _fail(CandidateContractCode.INVALID_VALUE) from None


def _safe_confidence(value: object) -> Confidence:
    if type(value) is not Confidence:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return Confidence(value.kind, value.value)
    except DocumentContractError:
        raise _fail(CandidateContractCode.INVALID_VALUE) from None


def _validate_languages(value: object) -> None:
    if type(value) is not tuple:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    if len(value) > MAX_HINTS:
        raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
    for language in value:
        if type(language) is not LanguageDescriptor:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        confidence = _safe_confidence(language.confidence)
        try:
            LanguageDescriptor(language.language, language.script, confidence)
        except DocumentContractError:
            raise _fail(CandidateContractCode.INVALID_VALUE) from None


def _validate_resource_usage(value: object, succeeded: int) -> None:
    if type(value) is not ResourceUsage:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        checked = ResourceUsage(value.elapsed_ms, value.processed_pages, value.peak_memory_bytes)
    except DocumentContractError:
        raise _fail(CandidateContractCode.INVALID_VALUE) from None
    if checked.processed_pages != succeeded:
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)


@dataclass(frozen=True, slots=True)
class _ResultSnapshot:
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    result_contract_version: str
    request_contract_version: str
    routing_version: str
    requested_pages: tuple[int, ...]
    page_statuses: tuple[tuple[int, PageStatus], ...]
    status: ResultStatus


def _result_index(
    value: object,
) -> tuple[_ResultSnapshot, dict[tuple[int, str, str, str, str], NormalizedBox]]:
    """Validate structural fields without reading, copying, hashing, or formatting block text."""
    if type(value) is not DocumentProcessingResult:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        if type(value.status) is not ResultStatus:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if (
            type(value.result_contract_version) is not str
            or type(value.request_contract_version) is not str
        ):
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if (
            value.result_contract_version != RESULT_CONTRACT_VERSION
            or value.request_contract_version
            not in (
                PARSER_REQUEST_CONTRACT_VERSION,
                OCR_REQUEST_CONTRACT_VERSION,
            )
        ):
            raise _fail(CandidateContractCode.INVALID_VERSION)
        if type(value.pages) is not tuple:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if len(value.pages) > MAX_PAGES:
            raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
        if any(type(page) is not PageResult for page in value.pages):
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if type(value.requested_pages) is not PageSelection:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if type(value.provenance) is not ProviderProvenance:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        request_id = _safe_id(value.request_id)
        document_id = _safe_id(value.document_id)
        attempt_id = _safe_id(value.processing_attempt_id)
        if len({request_id, document_id, attempt_id}) != 3:
            raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
        source = _safe_source(value.source)
        requested_pages = PageSelection(value.requested_pages.pages).pages
        provenance = ProviderProvenance(
            value.provenance.provider_id,
            value.provenance.adapter_id,
            value.provenance.adapter_version,
            value.provenance.engine_id,
            value.provenance.engine_version,
            value.provenance.routing_version,
            value.provenance.runtime_backend,
        )
        if type(value.warnings) is not tuple:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if len(value.warnings) > len(WarningCode):
            raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
        if any(type(warning) is not WarningCode for warning in value.warnings):
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if value.warnings != tuple(sorted(set(value.warnings), key=lambda item: item.value)):
            raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
        if value.error_code is not None and type(value.error_code) is not ResultErrorCode:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        index: dict[tuple[int, str, str, str, str], NormalizedBox] = {}
        page_numbers: list[int] = []
        page_statuses: list[tuple[int, PageStatus]] = []
        succeeded = 0
        for page in value.pages:
            if type(page.page_number) is not int or page.page_number < 1:
                raise _fail(CandidateContractCode.INVALID_VALUE)
            if type(page.status) is not PageStatus:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if type(page.width) is not int or type(page.height) is not int:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if page.width < 1 or page.height < 1:
                raise _fail(CandidateContractCode.INVALID_VALUE)
            if type(page.rotation_degrees) is not int:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if page.rotation_degrees not in (0, 90, 180, 270):
                raise _fail(CandidateContractCode.INVALID_VALUE)
            if page.error_code is not None and type(page.error_code) is not ResultErrorCode:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            _validate_languages(page.languages)
            if type(page.blocks) is not tuple:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if len(page.blocks) > MAX_BLOCKS_PER_PAGE:
                raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
            if any(type(block) is not TextBlock for block in page.blocks):
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if type(page.tables) is not tuple:
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if len(page.tables) > MAX_TABLES_PER_PAGE:
                raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
            if any(type(table) is not TableResult for table in page.tables):
                raise _fail(CandidateContractCode.INVALID_TYPE)
            if page.status is PageStatus.SUCCEEDED:
                succeeded += 1
                if page.error_code is not None:
                    raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
            elif page.languages or page.blocks or page.tables or page.error_code is None:
                raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
            blocks: dict[str, tuple[BlockKind, NormalizedBox]] = {}
            block_order: list[tuple[int, str]] = []
            for block in page.blocks:
                # The content-bearing block field is outside this verifier's trust claim.
                # Structural validation remains text-blind even for hostile values.
                block_id, kind = block.block_id, block.kind
                if (
                    type(block_id) is not str
                    or _TOKEN.fullmatch(block_id) is None
                    or type(kind) is not BlockKind
                ):
                    raise _fail(CandidateContractCode.INVALID_VALUE)
                if type(block.reading_order) is not int:
                    raise _fail(CandidateContractCode.INVALID_TYPE)
                if block.reading_order < 0:
                    raise _fail(CandidateContractCode.INVALID_VALUE)
                if block_id in blocks:
                    raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
                _safe_confidence(block.confidence)
                blocks[block_id] = (kind, _safe_box(block.box))
                block_order.append((block.reading_order, block_id))
                if kind in {BlockKind.TEXT, BlockKind.TITLE}:
                    index[(page.page_number, EvidenceKind.BLOCK.value, "", "", block_id)] = blocks[
                        block_id
                    ][1]
            if block_order != sorted(block_order):
                raise _fail(CandidateContractCode.INVALID_VALUE)
            table_ids: set[str] = set()
            for table in page.tables:
                if type(table.table_id) is not str or _TOKEN.fullmatch(table.table_id) is None:
                    raise _fail(CandidateContractCode.INVALID_VALUE)
                if table.table_id in table_ids:
                    raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
                table_ids.add(table.table_id)
                if type(table.cells) is not tuple:
                    raise _fail(CandidateContractCode.INVALID_TYPE)
                if len(table.cells) > MAX_CELLS_PER_TABLE:
                    raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
                if any(type(cell) is not TableCell for cell in table.cells):
                    raise _fail(CandidateContractCode.INVALID_TYPE)
                cell_ids: set[str] = set()
                positions: set[tuple[int, int]] = set()
                cell_order: list[tuple[int, int, str]] = []
                for cell in table.cells:
                    if any(
                        type(item) is not str or _TOKEN.fullmatch(item) is None
                        for item in (cell.cell_id, cell.block_id)
                    ):
                        raise _fail(CandidateContractCode.INVALID_VALUE)
                    if any(
                        type(item) is not int
                        for item in (cell.row, cell.column, cell.row_span, cell.column_span)
                    ):
                        raise _fail(CandidateContractCode.INVALID_TYPE)
                    cell_box = _safe_box(cell.box)
                    try:
                        checked_cell = TableCell(
                            cell.cell_id,
                            cell.block_id,
                            cell.row,
                            cell.column,
                            cell.row_span,
                            cell.column_span,
                            cell_box,
                        )
                    except DocumentContractError:
                        raise _fail(CandidateContractCode.INVALID_VALUE) from None
                    if (
                        checked_cell.cell_id in cell_ids
                        or (
                            checked_cell.row,
                            checked_cell.column,
                        )
                        in positions
                    ):
                        raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
                    cell_ids.add(checked_cell.cell_id)
                    positions.add((checked_cell.row, checked_cell.column))
                    cell_order.append((checked_cell.row, checked_cell.column, checked_cell.cell_id))
                    block_entry = blocks.get(cell.block_id)
                    if block_entry is None or block_entry[0] is not BlockKind.TABLE_CELL:
                        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
                    key = (
                        page.page_number,
                        EvidenceKind.TABLE_CELL.value,
                        table.table_id,
                        cell.cell_id,
                        cell.block_id,
                    )
                    if key in index:
                        raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
                    index[key] = cell_box
                if cell_order != sorted(cell_order):
                    raise _fail(CandidateContractCode.INVALID_VALUE)
            page_numbers.append(page.page_number)
            page_statuses.append((page.page_number, page.status))
        if tuple(page_numbers) != requested_pages:
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        _validate_resource_usage(value.resource_usage, succeeded)
        failed = len(value.pages) - succeeded
        if value.status is ResultStatus.SUCCEEDED and (failed or value.error_code is not None):
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        if value.status is ResultStatus.PARTIAL and (
            succeeded == 0 or failed == 0 or value.error_code is None
        ):
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        if value.status in {ResultStatus.FAILED, ResultStatus.NEEDS_FALLBACK} and (
            succeeded or value.error_code is None
        ):
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        return (
            _ResultSnapshot(
                request_id=request_id,
                document_id=document_id,
                processing_attempt_id=attempt_id,
                source=source,
                result_contract_version=value.result_contract_version,
                request_contract_version=value.request_contract_version,
                routing_version=provenance.routing_version,
                requested_pages=requested_pages,
                page_statuses=tuple(page_statuses),
                status=value.status,
            ),
            index,
        )
    except CandidateContractError:
        raise
    except DocumentContractError:
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH) from None
    except (AttributeError, TypeError):
        raise _fail(CandidateContractCode.INVALID_TYPE) from None


def verify_structural_evidence(
    *, candidate: object, result: object, classification: object, receipt: object
) -> StructuralMatchOutcome:
    """Match identities only; source access and all clinical meaning remain unverified."""
    checked = snapshot_candidate(candidate)
    decision = _snapshot_decision(classification)
    metadata = _snapshot_receipt(receipt)
    processed, index = _result_index(result)
    context = (
        checked.request_id,
        checked.document_id,
        checked.processing_attempt_id,
        checked.source,
    )
    if (
        processed.request_id,
        processed.document_id,
        processed.processing_attempt_id,
        processed.source,
    ) != context:
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    if processed.routing_version != checked.routing_version:
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    if (
        decision.request_id,
        decision.document_id,
        decision.processing_attempt_id,
        decision.source,
    ) != context:
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    if (
        decision.disposition is not ClassificationDisposition.SELECTED
        or decision.selected_type is not checked.document_type
    ):
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    if (
        metadata.status is not RegistryResolutionStatus.PINNED_METADATA
        or metadata.authority is not ProcessorAuthority.ENGINEERING_ONLY
        or metadata.processor_disposition is not ProcessorDisposition.NOOP_ABSTAIN
        or (
            metadata.document_type,
            metadata.processor_id,
            metadata.processor_version,
            metadata.output_schema_version,
        )
        != (
            checked.document_type,
            checked.processor_id,
            checked.processor_version,
            processed.result_contract_version,
        )
        or processed.request_contract_version not in metadata.input_schema_versions
    ):
        raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    if checked.disposition is CandidateDisposition.ABSTAINED:
        return StructuralMatchOutcome(
            StructuralMatchStatus.ABSTAINED_UNVERIFIED, SourceAccessStatus.NOT_VERIFIED, 0
        )
    if processed.status is not ResultStatus.SUCCEEDED:
        return StructuralMatchOutcome(
            StructuralMatchStatus.ABSTAINED_UNVERIFIED, SourceAccessStatus.NOT_VERIFIED, 0
        )
    for evidence in checked.evidence:
        page_status = dict(processed.page_statuses).get(evidence.page_number)
        if page_status is not PageStatus.SUCCEEDED:
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        actual = index.get(evidence.identity)
        if actual is None or actual != evidence.box:
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
    return StructuralMatchOutcome(
        StructuralMatchStatus.STRUCTURALLY_MATCHED_UNCONFIRMED,
        SourceAccessStatus.NOT_VERIFIED,
        len(checked.evidence),
    )
