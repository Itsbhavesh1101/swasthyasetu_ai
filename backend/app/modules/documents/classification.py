"""Closed, synthetic-only document classification decision contracts.

This module validates caller-declared machine labels. It never inspects document
content and cannot establish clinical truth or activate a processor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.modules.documents.contracts import SyntheticSourceRef
from app.shared.types import OpaqueId

CLASSIFICATION_SCHEMA_VERSION: Final = "synthetic-document-classification.v1"
CLASSIFICATION_CONFIG_VERSION: Final = "synthetic-label-normalizer.v1"
MAX_CLASSIFICATION_CANDIDATES: Final = 16

_REFERENCE = re.compile(r"^SYNTHETIC_CLASSIFICATION_[A-Z0-9_]{1,48}$")


class DocumentType(StrEnum):
    PRESCRIPTION = "PRESCRIPTION"
    LAB_REPORT = "LAB_REPORT"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    DIAGNOSTIC_REPORT = "DIAGNOSTIC_REPORT"
    IMAGING_REPORT = "IMAGING_REPORT"
    REFERRAL_LETTER = "REFERRAL_LETTER"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


PROCESSABLE_DOCUMENT_TYPES: Final = (
    DocumentType.PRESCRIPTION,
    DocumentType.LAB_REPORT,
    DocumentType.DISCHARGE_SUMMARY,
    DocumentType.DIAGNOSTIC_REPORT,
    DocumentType.IMAGING_REPORT,
    DocumentType.REFERRAL_LETTER,
)
_TYPE_ORDER: Final = {item: index for index, item in enumerate(DocumentType)}


class ClassificationAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class ClassificationDisposition(StrEnum):
    SELECTED = "SELECTED"
    ABSTAINED = "ABSTAINED"
    CONFLICT = "CONFLICT"
    UNSUPPORTED = "UNSUPPORTED"


class ClassificationReason(StrEnum):
    EXACT_SYNTHETIC_LABEL = "EXACT_SYNTHETIC_LABEL"
    ABSENT_EVIDENCE = "ABSENT_EVIDENCE"
    UNKNOWN_DECLARATION = "UNKNOWN_DECLARATION"
    OTHER_DECLARATION = "OTHER_DECLARATION"
    CONFLICTING_DECLARATIONS = "CONFLICTING_DECLARATIONS"


class ClassificationErrorCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_VERSION = "INVALID_VERSION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    CONTEXT_MISMATCH = "CONTEXT_MISMATCH"
    INVALID_DECISION = "INVALID_DECISION"
    UNEXPECTED_FIELD = "UNEXPECTED_FIELD"


class ClassificationContractError(ValueError):
    """Content-free synthetic classification failure."""

    def __init__(self, code: ClassificationErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: ClassificationErrorCode) -> ClassificationContractError:
    return ClassificationContractError(code)


def _opaque(value: object) -> None:
    if type(value) is not OpaqueId or type(value.value) is not UUID:
        raise _fail(ClassificationErrorCode.INVALID_TYPE)


@dataclass(frozen=True, slots=True)
class SyntheticClassificationRef:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.value) is not str or _REFERENCE.fullmatch(self.value) is None:
            raise _fail(ClassificationErrorCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True, kw_only=True, init=False)
class SyntheticClassificationCandidate:
    """One explicit synthetic label with no confidence or content payload."""

    candidate_ref: SyntheticClassificationRef = field(repr=False)
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    document_type: DocumentType
    schema_version: str
    config_version: str

    def __init__(
        self,
        *,
        candidate_ref: SyntheticClassificationRef,
        request_id: OpaqueId,
        document_id: OpaqueId,
        processing_attempt_id: OpaqueId,
        source: SyntheticSourceRef,
        document_type: DocumentType,
        schema_version: str,
        config_version: str,
        **unexpected: object,
    ) -> None:
        if unexpected:
            raise _fail(ClassificationErrorCode.UNEXPECTED_FIELD)
        object.__setattr__(self, "candidate_ref", candidate_ref)
        object.__setattr__(self, "request_id", request_id)
        object.__setattr__(self, "document_id", document_id)
        object.__setattr__(self, "processing_attempt_id", processing_attempt_id)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "document_type", document_type)
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "config_version", config_version)
        self.__post_init__()

    def __post_init__(self) -> None:
        if (
            type(self.candidate_ref) is not SyntheticClassificationRef
            or type(self.source) is not SyntheticSourceRef
        ):
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        if type(self.source.value) is not str:
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        for value in (self.request_id, self.document_id, self.processing_attempt_id):
            _opaque(value)
        if len({self.request_id, self.document_id, self.processing_attempt_id}) != 3:
            raise _fail(ClassificationErrorCode.DUPLICATE_IDENTITY)
        if type(self.document_type) is not DocumentType:
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        if (
            self.schema_version != CLASSIFICATION_SCHEMA_VERSION
            or self.config_version != CLASSIFICATION_CONFIG_VERSION
        ):
            raise _fail(ClassificationErrorCode.INVALID_VERSION)


def _snapshot_candidate(
    candidate: SyntheticClassificationCandidate,
) -> SyntheticClassificationCandidate:
    """Detach nested references while revalidating every caller-owned field."""

    return SyntheticClassificationCandidate(
        candidate_ref=SyntheticClassificationRef(candidate.candidate_ref.value),
        request_id=OpaqueId(candidate.request_id.value),
        document_id=OpaqueId(candidate.document_id.value),
        processing_attempt_id=OpaqueId(candidate.processing_attempt_id.value),
        source=SyntheticSourceRef(candidate.source.value),
        document_type=candidate.document_type,
        schema_version=candidate.schema_version,
        config_version=candidate.config_version,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ClassificationRequest:
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    candidates: tuple[SyntheticClassificationCandidate, ...] = field(repr=False)
    schema_version: str
    config_version: str

    def __post_init__(self) -> None:
        for value in (self.request_id, self.document_id, self.processing_attempt_id):
            _opaque(value)
        if len({self.request_id, self.document_id, self.processing_attempt_id}) != 3:
            raise _fail(ClassificationErrorCode.DUPLICATE_IDENTITY)
        if type(self.source) is not SyntheticSourceRef or type(self.source.value) is not str:
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        if type(self.candidates) is not tuple or any(
            type(item) is not SyntheticClassificationCandidate for item in self.candidates
        ):
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        if len(self.candidates) > MAX_CLASSIFICATION_CANDIDATES:
            raise _fail(ClassificationErrorCode.LIMIT_EXCEEDED)
        if (
            self.schema_version != CLASSIFICATION_SCHEMA_VERSION
            or self.config_version != CLASSIFICATION_CONFIG_VERSION
        ):
            raise _fail(ClassificationErrorCode.INVALID_VERSION)
        source = SyntheticSourceRef(self.source.value)
        candidates = tuple(_snapshot_candidate(item) for item in self.candidates)
        object.__setattr__(self, "request_id", OpaqueId(self.request_id.value))
        object.__setattr__(self, "document_id", OpaqueId(self.document_id.value))
        object.__setattr__(
            self, "processing_attempt_id", OpaqueId(self.processing_attempt_id.value)
        )
        object.__setattr__(self, "source", source)
        refs = tuple(item.candidate_ref.value for item in candidates)
        if len(refs) != len(set(refs)):
            raise _fail(ClassificationErrorCode.DUPLICATE_IDENTITY)
        if any(
            (
                item.request_id != self.request_id
                or item.document_id != self.document_id
                or item.processing_attempt_id != self.processing_attempt_id
                or item.source != self.source
            )
            for item in candidates
        ):
            raise _fail(ClassificationErrorCode.CONTEXT_MISMATCH)
        canonical = tuple(
            sorted(
                candidates,
                key=lambda item: (_TYPE_ORDER[item.document_type], item.candidate_ref.value),
            )
        )
        object.__setattr__(self, "candidates", canonical)


@dataclass(frozen=True, slots=True, kw_only=True)
class ClassificationDecision:
    request_id: OpaqueId = field(repr=False)
    document_id: OpaqueId = field(repr=False)
    processing_attempt_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    candidates: tuple[SyntheticClassificationCandidate, ...] = field(repr=False)
    schema_version: str
    config_version: str
    authority: ClassificationAuthority
    disposition: ClassificationDisposition
    reason: ClassificationReason
    selected_type: DocumentType | None

    def __post_init__(self) -> None:
        request = ClassificationRequest(
            request_id=self.request_id,
            document_id=self.document_id,
            processing_attempt_id=self.processing_attempt_id,
            source=self.source,
            candidates=self.candidates,
            schema_version=self.schema_version,
            config_version=self.config_version,
        )
        object.__setattr__(self, "request_id", request.request_id)
        object.__setattr__(self, "document_id", request.document_id)
        object.__setattr__(self, "processing_attempt_id", request.processing_attempt_id)
        object.__setattr__(self, "source", request.source)
        object.__setattr__(self, "candidates", request.candidates)
        if self.authority is not ClassificationAuthority.ENGINEERING_ONLY:
            raise _fail(ClassificationErrorCode.INVALID_DECISION)
        if (
            type(self.disposition) is not ClassificationDisposition
            or type(self.reason) is not ClassificationReason
        ):
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        if self.selected_type is not None and type(self.selected_type) is not DocumentType:
            raise _fail(ClassificationErrorCode.INVALID_TYPE)
        expected = _decision_parts(self.candidates)
        actual = (self.disposition, self.reason, self.selected_type)
        if actual != expected:
            raise _fail(ClassificationErrorCode.INVALID_DECISION)


def _decision_parts(
    candidates: tuple[SyntheticClassificationCandidate, ...],
) -> tuple[ClassificationDisposition, ClassificationReason, DocumentType | None]:
    if not candidates:
        return (
            ClassificationDisposition.ABSTAINED,
            ClassificationReason.ABSENT_EVIDENCE,
            None,
        )
    declared = {item.document_type for item in candidates}
    if declared == {DocumentType.UNKNOWN}:
        return (
            ClassificationDisposition.ABSTAINED,
            ClassificationReason.UNKNOWN_DECLARATION,
            None,
        )
    if declared == {DocumentType.OTHER}:
        return (
            ClassificationDisposition.UNSUPPORTED,
            ClassificationReason.OTHER_DECLARATION,
            None,
        )
    if len(declared) == 1:
        selected = next(iter(declared))
        if selected in PROCESSABLE_DOCUMENT_TYPES:
            return (
                ClassificationDisposition.SELECTED,
                ClassificationReason.EXACT_SYNTHETIC_LABEL,
                selected,
            )
    return (
        ClassificationDisposition.CONFLICT,
        ClassificationReason.CONFLICTING_DECLARATIONS,
        None,
    )


def classify_synthetic(request: ClassificationRequest) -> ClassificationDecision:
    """Normalize declared synthetic labels without inspecting any source or OCR output."""

    if type(request) is not ClassificationRequest:
        raise _fail(ClassificationErrorCode.INVALID_TYPE)
    disposition, reason, selected = _decision_parts(request.candidates)
    return ClassificationDecision(
        request_id=request.request_id,
        document_id=request.document_id,
        processing_attempt_id=request.processing_attempt_id,
        source=request.source,
        candidates=request.candidates,
        schema_version=request.schema_version,
        config_version=request.config_version,
        authority=ClassificationAuthority.ENGINEERING_ONLY,
        disposition=disposition,
        reason=reason,
        selected_type=selected,
    )
