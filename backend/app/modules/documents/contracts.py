"""Immutable provider-neutral parser/OCR contracts for synthetic engineering tests."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from app.shared.types import OpaqueId

PARSER_REQUEST_CONTRACT_VERSION: Final = "document-parser-request.v1"
OCR_REQUEST_CONTRACT_VERSION: Final = "ocr-request.v1"
RESULT_CONTRACT_VERSION: Final = "document-processing-result.v1"
MAX_PAGES: Final = 32
MAX_BLOCKS_PER_PAGE: Final = 128
MAX_TABLES_PER_PAGE: Final = 16
MAX_CELLS_PER_TABLE: Final = 256
MAX_TABLE_GRID_EXTENT: Final = MAX_CELLS_PER_TABLE
MAX_HINTS: Final = 8
MAX_TEXT_LENGTH: Final = 128
MAX_ELAPSED_MS: Final = 300_000.0

_TOKEN = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")
_SYNTHETIC_SOURCE = re.compile(r"^SYNTHETIC_SOURCE_[A-Z0-9_]{1,64}$")
_SYNTHETIC_TEXT = re.compile(r"^SYNTHETIC_[A-Z0-9]+(?:_[A-Z0-9]+)*$")
_HINT = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,15}$")
_FORBIDDEN_AUTHORITY = (
    "APPROVED",
    "CLINICIAN_CONFIRMED",
    "MEDICALLY_CLEARED",
    "TRIAGE",
    "TREATMENT",
)


class DocumentContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_VERSION = "INVALID_VERSION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INVALID_COVERAGE = "INVALID_COVERAGE"
    INVALID_STATUS = "INVALID_STATUS"


class DocumentContractError(ValueError):
    """Content-free contract failure."""

    def __init__(self, code: DocumentContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: DocumentContractCode) -> DocumentContractError:
    return DocumentContractError(code)


def _id(value: object) -> None:
    if not isinstance(value, OpaqueId):
        raise _fail(DocumentContractCode.INVALID_TYPE)


def _token(value: object) -> None:
    if not isinstance(value, str) or _TOKEN.fullmatch(value) is None:
        raise _fail(DocumentContractCode.INVALID_VALUE)


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise _fail(DocumentContractCode.INVALID_TYPE)
    if value.tzinfo is None or value.utcoffset() is None:
        raise _fail(DocumentContractCode.INVALID_VALUE)
    return value.astimezone(UTC)


def _tuple(value: object, kind: type[object], maximum: int) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, kind) for item in value):
        raise _fail(DocumentContractCode.INVALID_TYPE)
    if len(value) > maximum:
        raise _fail(DocumentContractCode.LIMIT_EXCEEDED)


class ParserMode(StrEnum):
    NATIVE_TEXT = "NATIVE_TEXT"
    NATIVE_LAYOUT = "NATIVE_LAYOUT"


class OCRMode(StrEnum):
    TEXT = "TEXT"
    LAYOUT = "LAYOUT"
    TABLE_AWARE = "TABLE_AWARE"


class ResultStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    NEEDS_FALLBACK = "NEEDS_FALLBACK"


class PageStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class BlockKind(StrEnum):
    TEXT = "TEXT"
    TITLE = "TITLE"
    TABLE_CELL = "TABLE_CELL"


class ConfidenceKind(StrEnum):
    UNKNOWN = "UNKNOWN"
    RECOGNIZER = "RECOGNIZER"
    HEURISTIC = "HEURISTIC"


class WarningCode(StrEnum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    PAGE_INCOMPLETE = "PAGE_INCOMPLETE"
    LANGUAGE_UNSUPPORTED = "LANGUAGE_UNSUPPORTED"


class ResultErrorCode(StrEnum):
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    REFUSED = "REFUSED"
    ENGINE_UNAVAILABLE = "ENGINE_UNAVAILABLE"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"
    MALFORMED_PROVIDER_RESULT = "MALFORMED_PROVIDER_RESULT"
    PAGE_FAILED = "PAGE_FAILED"


@dataclass(frozen=True, slots=True)
class SyntheticSourceRef:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or _SYNTHETIC_SOURCE.fullmatch(self.value) is None:
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class PageSelection:
    pages: tuple[int, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pages, tuple) or not self.pages:
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if len(self.pages) > MAX_PAGES:
            raise _fail(DocumentContractCode.LIMIT_EXCEEDED)
        if any(type(page) is not int or page < 1 for page in self.pages):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if self.pages != tuple(sorted(set(self.pages))):
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)


@dataclass(frozen=True, slots=True)
class ResourceProfile:
    max_pages: int
    max_blocks_per_page: int
    max_tables_per_page: int
    max_cells_per_table: int

    def __post_init__(self) -> None:
        values = (
            (self.max_pages, MAX_PAGES),
            (self.max_blocks_per_page, MAX_BLOCKS_PER_PAGE),
            (self.max_tables_per_page, MAX_TABLES_PER_PAGE),
            (self.max_cells_per_table, MAX_CELLS_PER_TABLE),
        )
        if any(type(value) is not int for value, _ in values):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if any(not 1 <= value <= limit for value, limit in values):
            raise _fail(DocumentContractCode.LIMIT_EXCEEDED)


def _request_common(request: DocumentParserRequest | OCRRequest, expected_version: str) -> None:
    for name in ("request_id", "document_id", "processing_attempt_id"):
        _id(getattr(request, name))
    if request.contract_version != expected_version:
        raise _fail(DocumentContractCode.INVALID_VERSION)
    _token(request.routing_version)
    source = request.source
    pages = request.pages
    profile = request.resource_profile
    if (
        not isinstance(source, SyntheticSourceRef)
        or not isinstance(pages, PageSelection)
        or not isinstance(profile, ResourceProfile)
    ):
        raise _fail(DocumentContractCode.INVALID_TYPE)
    if len(pages.pages) > profile.max_pages:
        raise _fail(DocumentContractCode.LIMIT_EXCEEDED)
    hints = request.language_hints
    scripts = request.script_hints
    for values in (hints, scripts):
        if not isinstance(values, tuple) or len(values) > MAX_HINTS:
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if any(not isinstance(item, str) or _HINT.fullmatch(item) is None for item in values):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if len(values) != len(set(values)):
            raise _fail(DocumentContractCode.INVALID_VALUE)
    requested = _utc(request.requested_at)
    deadline = _utc(request.deadline_at)
    object.__setattr__(request, "requested_at", requested)
    object.__setattr__(request, "deadline_at", deadline)
    if deadline <= requested:
        raise _fail(DocumentContractCode.INVALID_VALUE)
    correlation = request.correlation_id
    if correlation is not None:
        _token(correlation)


@dataclass(frozen=True, slots=True, kw_only=True)
class DocumentParserRequest:
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    pages: PageSelection
    mode: ParserMode
    language_hints: tuple[str, ...]
    script_hints: tuple[str, ...]
    contract_version: str
    routing_version: str
    requested_at: datetime
    deadline_at: datetime
    resource_profile: ResourceProfile
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, ParserMode):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        _request_common(self, PARSER_REQUEST_CONTRACT_VERSION)
        if len({self.request_id, self.document_id, self.processing_attempt_id}) != 3:
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)


@dataclass(frozen=True, slots=True, kw_only=True)
class OCRRequest:
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    pages: PageSelection
    mode: OCRMode
    language_hints: tuple[str, ...]
    script_hints: tuple[str, ...]
    contract_version: str
    routing_version: str
    requested_at: datetime
    deadline_at: datetime
    resource_profile: ResourceProfile
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, OCRMode):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        _request_common(self, OCR_REQUEST_CONTRACT_VERSION)
        if len({self.request_id, self.document_id, self.processing_attempt_id}) != 3:
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)


@dataclass(frozen=True, slots=True)
class NormalizedBox:
    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self) -> None:
        values = (self.left, self.top, self.right, self.bottom)
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if self.left >= self.right or self.top >= self.bottom:
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class Confidence:
    kind: ConfidenceKind
    value: float | None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConfidenceKind):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if self.kind is ConfidenceKind.UNKNOWN:
            if self.value is not None:
                raise _fail(DocumentContractCode.INVALID_VALUE)
        elif (
            isinstance(self.value, bool)
            or not isinstance(self.value, (int, float))
            or not math.isfinite(self.value)
            or not 0 <= self.value <= 1
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class LanguageDescriptor:
    language: str
    script: str
    confidence: Confidence

    def __post_init__(self) -> None:
        if not isinstance(self.language, str) or not isinstance(self.script, str):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if (
            _HINT.fullmatch(self.language) is None
            or _HINT.fullmatch(self.script) is None
            or not isinstance(self.confidence, Confidence)
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class TextBlock:
    block_id: str
    kind: BlockKind
    text: str = field(repr=False)
    reading_order: int
    box: NormalizedBox
    confidence: Confidence

    def __post_init__(self) -> None:
        _token(self.block_id)
        if (
            not isinstance(self.kind, BlockKind)
            or type(self.reading_order) is not int
            or self.reading_order < 0
        ):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if (
            not isinstance(self.text, str)
            or len(self.text) > MAX_TEXT_LENGTH
            or _SYNTHETIC_TEXT.fullmatch(self.text) is None
            or any(marker in self.text for marker in _FORBIDDEN_AUTHORITY)
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if not isinstance(self.box, NormalizedBox) or not isinstance(self.confidence, Confidence):
            raise _fail(DocumentContractCode.INVALID_TYPE)


@dataclass(frozen=True, slots=True)
class TableCell:
    cell_id: str
    block_id: str
    row: int
    column: int
    row_span: int
    column_span: int
    box: NormalizedBox

    def __post_init__(self) -> None:
        _token(self.cell_id)
        _token(self.block_id)
        if any(
            type(value) is not int
            for value in (self.row, self.column, self.row_span, self.column_span)
        ):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if self.row < 0 or self.column < 0 or self.row_span < 1 or self.column_span < 1:
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if (
            self.row >= MAX_TABLE_GRID_EXTENT
            or self.column >= MAX_TABLE_GRID_EXTENT
            or self.row_span > MAX_TABLE_GRID_EXTENT
            or self.column_span > MAX_TABLE_GRID_EXTENT
            or self.row + self.row_span > MAX_TABLE_GRID_EXTENT
            or self.column + self.column_span > MAX_TABLE_GRID_EXTENT
        ):
            raise _fail(DocumentContractCode.LIMIT_EXCEEDED)
        if not isinstance(self.box, NormalizedBox):
            raise _fail(DocumentContractCode.INVALID_TYPE)


@dataclass(frozen=True, slots=True)
class TableResult:
    table_id: str
    cells: tuple[TableCell, ...]

    def __post_init__(self) -> None:
        _token(self.table_id)
        _tuple(self.cells, TableCell, MAX_CELLS_PER_TABLE)
        if len({cell.cell_id for cell in self.cells}) != len(self.cells) or len(
            {(cell.row, cell.column) for cell in self.cells}
        ) != len(self.cells):
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)
        if self.cells != tuple(
            sorted(self.cells, key=lambda cell: (cell.row, cell.column, cell.cell_id))
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class PageResult:
    page_number: int
    status: PageStatus
    width: int
    height: int
    rotation_degrees: int
    languages: tuple[LanguageDescriptor, ...]
    blocks: tuple[TextBlock, ...]
    tables: tuple[TableResult, ...]
    error_code: ResultErrorCode | None = None

    def __post_init__(self) -> None:
        if (
            type(self.page_number) is not int
            or self.page_number < 1
            or not isinstance(self.status, PageStatus)
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if (
            type(self.width) is not int
            or type(self.height) is not int
            or self.width < 1
            or self.height < 1
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if type(self.rotation_degrees) is not int:
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if self.rotation_degrees not in (0, 90, 180, 270):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if self.error_code is not None and not isinstance(self.error_code, ResultErrorCode):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        _tuple(self.languages, LanguageDescriptor, MAX_HINTS)
        _tuple(self.blocks, TextBlock, MAX_BLOCKS_PER_PAGE)
        _tuple(self.tables, TableResult, MAX_TABLES_PER_PAGE)
        if len({block.block_id for block in self.blocks}) != len(self.blocks):
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)
        if self.blocks != tuple(
            sorted(self.blocks, key=lambda block: (block.reading_order, block.block_id))
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if len({table.table_id for table in self.tables}) != len(self.tables):
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)
        blocks_by_id = {block.block_id: block for block in self.blocks}
        if any(
            cell.block_id not in blocks_by_id
            or blocks_by_id[cell.block_id].kind is not BlockKind.TABLE_CELL
            for table in self.tables
            for cell in table.cells
        ):
            raise _fail(DocumentContractCode.IDENTITY_MISMATCH)
        if self.status is PageStatus.FAILED:
            if self.languages or self.blocks or self.tables or self.error_code is None:
                raise _fail(DocumentContractCode.INVALID_STATUS)
        elif self.error_code is not None:
            raise _fail(DocumentContractCode.INVALID_STATUS)


@dataclass(frozen=True, slots=True)
class ProviderProvenance:
    provider_id: str
    adapter_id: str
    adapter_version: str
    engine_id: str
    engine_version: str
    routing_version: str
    runtime_backend: str

    def __post_init__(self) -> None:
        for value in (
            self.provider_id,
            self.adapter_id,
            self.adapter_version,
            self.engine_id,
            self.engine_version,
            self.routing_version,
            self.runtime_backend,
        ):
            _token(value)


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    elapsed_ms: float
    processed_pages: int
    peak_memory_bytes: int | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.elapsed_ms, bool)
            or not isinstance(self.elapsed_ms, (int, float))
            or not math.isfinite(self.elapsed_ms)
            or not 0 <= self.elapsed_ms <= MAX_ELAPSED_MS
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if type(self.processed_pages) is not int or not 0 <= self.processed_pages <= MAX_PAGES:
            raise _fail(DocumentContractCode.INVALID_VALUE)
        if self.peak_memory_bytes is not None and (
            type(self.peak_memory_bytes) is not int or self.peak_memory_bytes < 0
        ):
            raise _fail(DocumentContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True, kw_only=True)
class DocumentProcessingResult:
    result_contract_version: str
    request_contract_version: str
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    requested_pages: PageSelection
    status: ResultStatus
    pages: tuple[PageResult, ...] = field(repr=False)
    provenance: ProviderProvenance
    warnings: tuple[WarningCode, ...]
    error_code: ResultErrorCode | None
    resource_usage: ResourceUsage

    def __post_init__(self) -> None:
        if (
            self.result_contract_version != RESULT_CONTRACT_VERSION
            or self.request_contract_version
            not in {PARSER_REQUEST_CONTRACT_VERSION, OCR_REQUEST_CONTRACT_VERSION}
        ):
            raise _fail(DocumentContractCode.INVALID_VERSION)
        for value in (self.request_id, self.document_id, self.processing_attempt_id):
            _id(value)
        if len({self.request_id, self.document_id, self.processing_attempt_id}) != 3:
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)
        if not isinstance(self.source, SyntheticSourceRef):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if (
            not isinstance(self.requested_pages, PageSelection)
            or not isinstance(self.status, ResultStatus)
            or not isinstance(self.provenance, ProviderProvenance)
            or not isinstance(self.resource_usage, ResourceUsage)
        ):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        _tuple(self.pages, PageResult, MAX_PAGES)
        _tuple(self.warnings, WarningCode, len(WarningCode))
        if self.error_code is not None and not isinstance(self.error_code, ResultErrorCode):
            raise _fail(DocumentContractCode.INVALID_TYPE)
        if self.warnings != tuple(sorted(set(self.warnings), key=lambda item: item.value)):
            raise _fail(DocumentContractCode.DUPLICATE_IDENTITY)
        page_numbers = tuple(page.page_number for page in self.pages)
        if page_numbers != self.requested_pages.pages:
            raise _fail(DocumentContractCode.INVALID_COVERAGE)
        successes = sum(page.status is PageStatus.SUCCEEDED for page in self.pages)
        failures = len(self.pages) - successes
        if self.resource_usage.processed_pages != successes:
            raise _fail(DocumentContractCode.INVALID_COVERAGE)
        if self.status is ResultStatus.SUCCEEDED and (failures or self.error_code is not None):
            raise _fail(DocumentContractCode.INVALID_STATUS)
        if self.status is ResultStatus.PARTIAL and (
            successes == 0 or failures == 0 or self.error_code is None
        ):
            raise _fail(DocumentContractCode.INVALID_STATUS)
        if self.status in {ResultStatus.FAILED, ResultStatus.NEEDS_FALLBACK} and (
            successes or self.error_code is None
        ):
            raise _fail(DocumentContractCode.INVALID_STATUS)

    def assert_matches(self, request: OCRRequest | DocumentParserRequest) -> None:
        if (
            self.request_id,
            self.document_id,
            self.processing_attempt_id,
            self.source,
            self.requested_pages,
            self.request_contract_version,
        ) != (
            request.request_id,
            request.document_id,
            request.processing_attempt_id,
            request.source,
            request.pages,
            request.contract_version,
        ):
            raise _fail(DocumentContractCode.IDENTITY_MISMATCH)
        if self.provenance.routing_version != request.routing_version:
            raise _fail(DocumentContractCode.IDENTITY_MISMATCH)
        for page in self.pages:
            if (
                len(page.blocks) > request.resource_profile.max_blocks_per_page
                or len(page.tables) > request.resource_profile.max_tables_per_page
                or any(
                    len(table.cells) > request.resource_profile.max_cells_per_table
                    for table in page.tables
                )
            ):
                raise _fail(DocumentContractCode.LIMIT_EXCEEDED)
