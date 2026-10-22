"""Detached synthetic candidate and structural-evidence contracts.

These contracts contain no extracted value and grant no source or clinical authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.modules.documents.classification import PROCESSABLE_DOCUMENT_TYPES, DocumentType
from app.modules.documents.contracts import (
    MAX_PAGES,
    Confidence,
    ConfidenceKind,
    NormalizedBox,
    SyntheticSourceRef,
)
from app.shared.types import OpaqueId

CANDIDATE_SCHEMA_VERSION: Final = "synthetic-document-candidate.v1"
EVIDENCE_SCHEMA_VERSION: Final = "synthetic-structural-evidence.v1"
MAX_EVIDENCE_REFERENCES: Final = 128

_REFERENCE = re.compile(r"^SYNTHETIC_CANDIDATE_[A-Z0-9_]{1,38}$")
_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_PROCESSOR_ID = re.compile(r"^[A-Z][A-Za-z0-9]{0,47}Processor$")
_VERSION = re.compile(r"^v[1-9][0-9]{0,5}$")


class CandidateAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class CandidateDisposition(StrEnum):
    UNCONFIRMED = "UNCONFIRMED"
    ABSTAINED = "ABSTAINED"


class EvidenceKind(StrEnum):
    BLOCK = "BLOCK"
    TABLE_CELL = "TABLE_CELL"


class CandidateReason(StrEnum):
    STRUCTURAL_REFERENCE_ONLY = "STRUCTURAL_REFERENCE_ONLY"
    NO_EVIDENCE = "NO_EVIDENCE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PROCESSING_INCOMPLETE = "PROCESSING_INCOMPLETE"
    CLASSIFICATION_NOT_SELECTED = "CLASSIFICATION_NOT_SELECTED"


class CandidateContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_VERSION = "INVALID_VERSION"
    INVALID_STATUS = "INVALID_STATUS"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
    UNEXPECTED_FIELD = "UNEXPECTED_FIELD"


class CandidateContractError(ValueError):
    """Content-free candidate boundary failure."""

    def __init__(self, code: CandidateContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: CandidateContractCode) -> CandidateContractError:
    return CandidateContractError(code)


def _id(value: object) -> OpaqueId:
    if type(value) is not OpaqueId or type(value.value) is not UUID:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    return OpaqueId(value.value)


def _source(value: object) -> SyntheticSourceRef:
    if type(value) is not SyntheticSourceRef or type(value.value) is not str:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return SyntheticSourceRef(value.value)
    except ValueError:
        raise _fail(CandidateContractCode.INVALID_VALUE) from None


def _box(value: object) -> NormalizedBox:
    if type(value) is not NormalizedBox:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return NormalizedBox(value.left, value.top, value.right, value.bottom)
    except (TypeError, ValueError):
        raise _fail(CandidateContractCode.INVALID_VALUE) from None


@dataclass(frozen=True, slots=True)
class SyntheticCandidateRef:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.value) is not str or _REFERENCE.fullmatch(self.value) is None:
            raise _fail(CandidateContractCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class StructuralEvidenceRef:
    evidence_schema_version: str
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    routing_version: str
    page_number: int
    kind: EvidenceKind
    block_id: str = field(repr=False)
    table_id: str | None = field(default=None, repr=False)
    cell_id: str | None = field(default=None, repr=False)
    box: NormalizedBox = field(repr=False)

    def __init__(
        self,
        *,
        evidence_schema_version: str,
        request_id: OpaqueId,
        document_id: OpaqueId,
        processing_attempt_id: OpaqueId,
        source: SyntheticSourceRef,
        routing_version: str,
        page_number: int,
        kind: EvidenceKind,
        block_id: str,
        box: NormalizedBox,
        table_id: str | None = None,
        cell_id: str | None = None,
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise _fail(CandidateContractCode.UNEXPECTED_FIELD)
        object.__setattr__(self, "evidence_schema_version", evidence_schema_version)
        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "document_id", document_id)
        object.__setattr__(self, "processing_attempt_id", processing_attempt_id)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "routing_version", routing_version)
        object.__setattr__(self, "page_number", page_number)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "block_id", block_id)
        object.__setattr__(self, "table_id", table_id)
        object.__setattr__(self, "cell_id", cell_id)
        object.__setattr__(self, "box", box)
        self.__post_init__()

    def __post_init__(self) -> None:
        if self.evidence_schema_version != EVIDENCE_SCHEMA_VERSION:
            raise _fail(CandidateContractCode.INVALID_VERSION)
        identities = tuple(
            _id(item) for item in (self.request_id, self.document_id, self.processing_attempt_id)
        )
        if len(set(identities)) != 3:
            raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
        if type(self.routing_version) is not str or _TOKEN.fullmatch(self.routing_version) is None:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if type(self.page_number) is not int or self.page_number < 1:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if self.page_number > MAX_PAGES:
            raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
        if type(self.kind) is not EvidenceKind:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if type(self.block_id) is not str or _TOKEN.fullmatch(self.block_id) is None:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if self.kind is EvidenceKind.BLOCK:
            if self.table_id is not None or self.cell_id is not None:
                raise _fail(CandidateContractCode.INVALID_VALUE)
        elif (
            type(self.table_id) is not str
            or type(self.cell_id) is not str
            or _TOKEN.fullmatch(self.table_id) is None
            or _TOKEN.fullmatch(self.cell_id) is None
        ):
            raise _fail(CandidateContractCode.INVALID_VALUE)
        object.__setattr__(self, "request_id", identities[0])
        object.__setattr__(self, "document_id", identities[1])
        object.__setattr__(self, "processing_attempt_id", identities[2])
        object.__setattr__(self, "source", _source(self.source))
        object.__setattr__(self, "box", _box(self.box))

    @property
    def identity(self) -> tuple[int, str, str, str, str]:
        return (
            self.page_number,
            self.kind.value,
            self.table_id or "",
            self.cell_id or "",
            self.block_id,
        )


def snapshot_evidence(value: object) -> StructuralEvidenceRef:
    if type(value) is not StructuralEvidenceRef:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return StructuralEvidenceRef(
            evidence_schema_version=value.evidence_schema_version,
            request_id=value.request_id,
            document_id=value.document_id,
            processing_attempt_id=value.processing_attempt_id,
            source=value.source,
            routing_version=value.routing_version,
            page_number=value.page_number,
            kind=value.kind,
            block_id=value.block_id,
            table_id=value.table_id,
            cell_id=value.cell_id,
            box=value.box,
        )
    except AttributeError:
        raise _fail(CandidateContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class SyntheticDocumentCandidate:
    candidate_ref: SyntheticCandidateRef = field(repr=False)
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    document_type: DocumentType
    processor_id: str
    processor_version: str
    candidate_schema_version: str
    routing_version: str
    disposition: CandidateDisposition
    authority: CandidateAuthority
    evidence: tuple[StructuralEvidenceRef, ...] = field(repr=False)
    confidence: Confidence
    reason: CandidateReason
    created_at: datetime

    def __init__(
        self,
        *,
        candidate_ref: SyntheticCandidateRef,
        request_id: OpaqueId,
        document_id: OpaqueId,
        processing_attempt_id: OpaqueId,
        source: SyntheticSourceRef,
        document_type: DocumentType,
        processor_id: str,
        processor_version: str,
        candidate_schema_version: str,
        routing_version: str,
        disposition: CandidateDisposition,
        authority: CandidateAuthority,
        evidence: tuple[StructuralEvidenceRef, ...],
        confidence: Confidence,
        reason: CandidateReason,
        created_at: datetime,
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise _fail(CandidateContractCode.UNEXPECTED_FIELD)
        for name, value in locals().copy().items():
            if name not in {"self", "unexpected"}:
                object.__setattr__(self, name, value)
        self.__post_init__()

    def __post_init__(self) -> None:
        if type(self.candidate_ref) is not SyntheticCandidateRef:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        candidate_ref = SyntheticCandidateRef(self.candidate_ref.value)
        identities = tuple(
            _id(item) for item in (self.request_id, self.document_id, self.processing_attempt_id)
        )
        if len(set(identities)) != 3:
            raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
        source = _source(self.source)
        if (
            type(self.document_type) is not DocumentType
            or self.document_type not in PROCESSABLE_DOCUMENT_TYPES
        ):
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if type(self.processor_id) is not str or _PROCESSOR_ID.fullmatch(self.processor_id) is None:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if (
            type(self.processor_version) is not str
            or _VERSION.fullmatch(self.processor_version) is None
        ):
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if self.candidate_schema_version != CANDIDATE_SCHEMA_VERSION:
            raise _fail(CandidateContractCode.INVALID_VERSION)
        if type(self.routing_version) is not str or _TOKEN.fullmatch(self.routing_version) is None:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if (
            type(self.disposition) is not CandidateDisposition
            or type(self.authority) is not CandidateAuthority
        ):
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if (
            self.authority is not CandidateAuthority.ENGINEERING_ONLY
            or type(self.reason) is not CandidateReason
        ):
            raise _fail(CandidateContractCode.INVALID_STATUS)
        if type(self.evidence) is not tuple:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        if len(self.evidence) > MAX_EVIDENCE_REFERENCES:
            raise _fail(CandidateContractCode.LIMIT_EXCEEDED)
        evidence = tuple(
            sorted(
                (snapshot_evidence(item) for item in self.evidence),
                key=lambda item: item.identity,
            )
        )
        keys = tuple(item.identity for item in evidence)
        if len(keys) != len(set(keys)):
            raise _fail(CandidateContractCode.DUPLICATE_IDENTITY)
        context = (identities[0], identities[1], identities[2], source, self.routing_version)
        if any(
            (
                item.request_id,
                item.document_id,
                item.processing_attempt_id,
                item.source,
                item.routing_version,
            )
            != context
            for item in evidence
        ):
            raise _fail(CandidateContractCode.CONTEXT_MISMATCH)
        if type(self.confidence) is not Confidence:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        try:
            confidence = Confidence(self.confidence.kind, self.confidence.value)
        except (TypeError, ValueError):
            raise _fail(CandidateContractCode.INVALID_VALUE) from None
        if confidence.kind is not ConfidenceKind.UNKNOWN or confidence.value is not None:
            raise _fail(CandidateContractCode.INVALID_VALUE)
        if type(self.created_at) is not datetime or self.created_at.tzinfo is None:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        try:
            offset = self.created_at.utcoffset()
        except Exception:
            raise _fail(CandidateContractCode.INVALID_VALUE) from None
        if offset is None:
            raise _fail(CandidateContractCode.INVALID_TYPE)
        try:
            created = self.created_at.astimezone(UTC)
        except Exception:
            raise _fail(CandidateContractCode.INVALID_VALUE) from None
        if self.disposition is CandidateDisposition.UNCONFIRMED:
            if not evidence or self.reason is not CandidateReason.STRUCTURAL_REFERENCE_ONLY:
                raise _fail(CandidateContractCode.INVALID_STATUS)
        elif evidence or self.reason is CandidateReason.STRUCTURAL_REFERENCE_ONLY:
            raise _fail(CandidateContractCode.INVALID_STATUS)
        object.__setattr__(self, "candidate_ref", candidate_ref)
        object.__setattr__(self, "request_id", identities[0])
        object.__setattr__(self, "document_id", identities[1])
        object.__setattr__(self, "processing_attempt_id", identities[2])
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "created_at", created)


def snapshot_candidate(value: object) -> SyntheticDocumentCandidate:
    """Revalidate and detach a caller-owned candidate at a use boundary."""
    if type(value) is not SyntheticDocumentCandidate:
        raise _fail(CandidateContractCode.INVALID_TYPE)
    try:
        return SyntheticDocumentCandidate(
            candidate_ref=value.candidate_ref,
            request_id=value.request_id,
            document_id=value.document_id,
            processing_attempt_id=value.processing_attempt_id,
            source=value.source,
            document_type=value.document_type,
            processor_id=value.processor_id,
            processor_version=value.processor_version,
            candidate_schema_version=value.candidate_schema_version,
            routing_version=value.routing_version,
            disposition=value.disposition,
            authority=value.authority,
            evidence=value.evidence,
            confidence=value.confidence,
            reason=value.reason,
            created_at=value.created_at,
        )
    except AttributeError:
        raise _fail(CandidateContractCode.INVALID_TYPE) from None
