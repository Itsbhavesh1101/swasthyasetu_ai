"""Pure synthetic document metadata and lifecycle contracts.

These values describe engineering fixtures only.  In particular, ``ACCEPTED``
does not mean malware-cleared, authorized, authentic, or clinically reliable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.modules.documents.classification import DocumentType
from app.modules.documents.contracts import SyntheticSourceRef
from app.shared.types import OpaqueId

DOCUMENT_METADATA_SCHEMA_VERSION: Final = "synthetic-document-metadata.v1"
DOCUMENT_LIFECYCLE_SCHEMA_VERSION: Final = "synthetic-document-lifecycle.v1"
SIMULATED_VALIDATION_SCHEMA_VERSION: Final = "synthetic-validation-decision.v1"

# Engineering-fixture bounds only. They are not approved upload policy.
MAX_SYNTHETIC_BYTE_COUNT_CLAIM: Final = 50 * 1024 * 1024
MAX_SYNTHETIC_PAGE_COUNT_CLAIM: Final = 100
MAX_DOCUMENT_VERSION: Final = 1_000_000
MAX_DOCUMENT_GENERATION: Final = 100

_OWNER_SCOPE = re.compile(r"^SYNTHETIC_OWNER_[A-Z0-9_]{1,48}$")
_IDEMPOTENCY = re.compile(r"^SYNTHETIC_IDEMPOTENCY_[A-Z0-9_]{1,48}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class DocumentDomainCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_VERSION = "INVALID_VERSION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    STALE_STATE = "STALE_STATE"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    INVALID_DECISION = "INVALID_DECISION"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"


class DocumentDomainError(ValueError):
    """A stable, content-free synthetic-domain failure."""

    def __init__(self, code: DocumentDomainCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: DocumentDomainCode) -> DocumentDomainError:
    return DocumentDomainError(code)


def _opaque(value: object) -> OpaqueId:
    if type(value) is not OpaqueId or type(value.value) is not UUID:
        raise _fail(DocumentDomainCode.INVALID_TYPE)
    return OpaqueId(value.value)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _fail(DocumentDomainCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _positive(value: object, maximum: int) -> int:
    if type(value) is not int:
        raise _fail(DocumentDomainCode.INVALID_TYPE)
    if not 1 <= value <= maximum:
        raise _fail(DocumentDomainCode.LIMIT_EXCEEDED)
    return value


class SyntheticDocumentAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticRepresentation(StrEnum):
    SYNTHETIC_PDF = "SYNTHETIC_PDF"
    SYNTHETIC_PNG = "SYNTHETIC_PNG"
    SYNTHETIC_JPEG = "SYNTHETIC_JPEG"


class DocumentStatus(StrEnum):
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    ACCEPTED = "ACCEPTED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class SyntheticValidationDisposition(StrEnum):
    SYNTHETIC_COMPATIBLE = "SYNTHETIC_COMPATIBLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class SyntheticOwnerScope:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.value) is not str or _OWNER_SCOPE.fullmatch(self.value) is None:
            raise _fail(DocumentDomainCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class SyntheticIdempotencyKey:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.value) is not str or _IDEMPOTENCY.fullmatch(self.value) is None:
            raise _fail(DocumentDomainCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True)
class SyntheticSha256:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if type(self.value) is not str or _SHA256.fullmatch(self.value) is None:
            raise _fail(DocumentDomainCode.INVALID_VALUE)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticDocumentDescriptor:
    """Bounded caller-declared metadata; no field is observed from a real file."""

    document_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    owner_scope: SyntheticOwnerScope = field(repr=False)
    idempotency_key: SyntheticIdempotencyKey = field(repr=False)
    sha256_claim: SyntheticSha256 = field(repr=False)
    document_type: DocumentType
    representation: SyntheticRepresentation
    byte_count_claim: int
    page_count_claim: int
    metadata_version: int
    generation: int
    declared_at: datetime
    schema_version: str = DOCUMENT_METADATA_SCHEMA_VERSION
    authority: SyntheticDocumentAuthority = SyntheticDocumentAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        document_id = _opaque(self.document_id)
        if type(self.source) is not SyntheticSourceRef or type(self.source.value) is not str:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.owner_scope) is not SyntheticOwnerScope:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.idempotency_key) is not SyntheticIdempotencyKey:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.sha256_claim) is not SyntheticSha256:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.document_type) is not DocumentType:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.representation) is not SyntheticRepresentation:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if self.schema_version != DOCUMENT_METADATA_SCHEMA_VERSION:
            raise _fail(DocumentDomainCode.INVALID_VERSION)
        if self.authority is not SyntheticDocumentAuthority.ENGINEERING_ONLY:
            raise _fail(DocumentDomainCode.INVALID_VALUE)
        byte_count = _positive(self.byte_count_claim, MAX_SYNTHETIC_BYTE_COUNT_CLAIM)
        page_count = _positive(self.page_count_claim, MAX_SYNTHETIC_PAGE_COUNT_CLAIM)
        metadata_version = _positive(self.metadata_version, MAX_DOCUMENT_VERSION)
        generation = _positive(self.generation, MAX_DOCUMENT_GENERATION)
        declared_at = _utc(self.declared_at)
        object.__setattr__(self, "document_id", document_id)
        object.__setattr__(self, "source", SyntheticSourceRef(self.source.value))
        object.__setattr__(self, "owner_scope", SyntheticOwnerScope(self.owner_scope.value))
        object.__setattr__(
            self, "idempotency_key", SyntheticIdempotencyKey(self.idempotency_key.value)
        )
        object.__setattr__(self, "sha256_claim", SyntheticSha256(self.sha256_claim.value))
        object.__setattr__(self, "byte_count_claim", byte_count)
        object.__setattr__(self, "page_count_claim", page_count)
        object.__setattr__(self, "metadata_version", metadata_version)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "declared_at", declared_at)


def _snapshot_descriptor(value: object) -> SyntheticDocumentDescriptor:
    if type(value) is not SyntheticDocumentDescriptor:
        raise _fail(DocumentDomainCode.INVALID_TYPE)
    try:
        return SyntheticDocumentDescriptor(
            document_id=value.document_id,
            source=value.source,
            owner_scope=value.owner_scope,
            idempotency_key=value.idempotency_key,
            sha256_claim=value.sha256_claim,
            document_type=value.document_type,
            representation=value.representation,
            byte_count_claim=value.byte_count_claim,
            page_count_claim=value.page_count_claim,
            metadata_version=value.metadata_version,
            generation=value.generation,
            declared_at=value.declared_at,
            schema_version=value.schema_version,
            authority=value.authority,
        )
    except DocumentDomainError:
        raise
    except (AttributeError, TypeError):
        raise _fail(DocumentDomainCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticValidationDecision:
    """Explicit simulation input; it cannot represent a scanner or authorization verdict."""

    document_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    owner_scope: SyntheticOwnerScope = field(repr=False)
    metadata_version: int
    disposition: SyntheticValidationDisposition
    decided_at: datetime
    schema_version: str = SIMULATED_VALIDATION_SCHEMA_VERSION
    authority: SyntheticDocumentAuthority = SyntheticDocumentAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_id", _opaque(self.document_id))
        if type(self.source) is not SyntheticSourceRef or type(self.source.value) is not str:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.owner_scope) is not SyntheticOwnerScope:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if type(self.disposition) is not SyntheticValidationDisposition:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if self.schema_version != SIMULATED_VALIDATION_SCHEMA_VERSION:
            raise _fail(DocumentDomainCode.INVALID_VERSION)
        if self.authority is not SyntheticDocumentAuthority.ENGINEERING_ONLY:
            raise _fail(DocumentDomainCode.INVALID_DECISION)
        object.__setattr__(self, "source", SyntheticSourceRef(self.source.value))
        object.__setattr__(self, "owner_scope", SyntheticOwnerScope(self.owner_scope.value))
        object.__setattr__(
            self, "metadata_version", _positive(self.metadata_version, MAX_DOCUMENT_VERSION)
        )
        object.__setattr__(self, "decided_at", _utc(self.decided_at))


_ALLOWED: Final = {
    DocumentStatus.UPLOADED: frozenset({DocumentStatus.VALIDATING}),
    DocumentStatus.VALIDATING: frozenset({DocumentStatus.ACCEPTED, DocumentStatus.REJECTED}),
    DocumentStatus.ACCEPTED: frozenset({DocumentStatus.QUEUED, DocumentStatus.REJECTED}),
    DocumentStatus.QUEUED: frozenset(
        {DocumentStatus.PROCESSING, DocumentStatus.FAILED, DocumentStatus.REJECTED}
    ),
    DocumentStatus.PROCESSING: frozenset(
        {
            DocumentStatus.NEEDS_REVIEW,
            DocumentStatus.SUCCEEDED,
            DocumentStatus.FAILED,
            DocumentStatus.REJECTED,
        }
    ),
    DocumentStatus.FAILED: frozenset({DocumentStatus.QUEUED}),
    DocumentStatus.NEEDS_REVIEW: frozenset({DocumentStatus.QUEUED}),
    DocumentStatus.SUCCEEDED: frozenset({DocumentStatus.QUEUED}),
    DocumentStatus.REJECTED: frozenset(),
}
_ATTEMPT_STATES: Final = frozenset(
    {
        DocumentStatus.QUEUED,
        DocumentStatus.PROCESSING,
        DocumentStatus.NEEDS_REVIEW,
        DocumentStatus.SUCCEEDED,
        DocumentStatus.FAILED,
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticDocumentState:
    descriptor: SyntheticDocumentDescriptor = field(repr=False)
    status: DocumentStatus
    state_version: int
    generation: int
    occurred_at: datetime
    attempt_ids: tuple[OpaqueId, ...] = field(repr=False)
    current_attempt_id: OpaqueId | None = field(default=None, repr=False)
    schema_version: str = DOCUMENT_LIFECYCLE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        descriptor = _snapshot_descriptor(self.descriptor)
        if type(self.status) is not DocumentStatus:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        if self.schema_version != DOCUMENT_LIFECYCLE_SCHEMA_VERSION:
            raise _fail(DocumentDomainCode.INVALID_VERSION)
        state_version = _positive(self.state_version, MAX_DOCUMENT_VERSION)
        generation = _positive(self.generation, MAX_DOCUMENT_GENERATION)
        if type(self.attempt_ids) is not tuple:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        attempt_ids = tuple(_opaque(item) for item in self.attempt_ids)
        if len(attempt_ids) != len(set(attempt_ids)) or descriptor.document_id in attempt_ids:
            raise _fail(DocumentDomainCode.DUPLICATE_IDENTITY)
        current = None if self.current_attempt_id is None else _opaque(self.current_attempt_id)
        if (self.status in _ATTEMPT_STATES) != (current is not None):
            raise _fail(DocumentDomainCode.INVALID_VALUE)
        if current is not None and (not attempt_ids or current != attempt_ids[-1]):
            raise _fail(DocumentDomainCode.IDENTITY_MISMATCH)
        if current is None and attempt_ids and self.status is not DocumentStatus.REJECTED:
            raise _fail(DocumentDomainCode.INVALID_VALUE)
        if len(attempt_ids) != generation - descriptor.generation + (1 if attempt_ids else 0):
            raise _fail(DocumentDomainCode.INVALID_VERSION)
        occurred = _utc(self.occurred_at)
        if occurred < descriptor.declared_at:
            raise _fail(DocumentDomainCode.INVALID_CHRONOLOGY)
        object.__setattr__(self, "descriptor", descriptor)
        object.__setattr__(self, "state_version", state_version)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "attempt_ids", attempt_ids)
        object.__setattr__(self, "current_attempt_id", current)

    def transition(
        self,
        target: DocumentStatus,
        *,
        at: datetime,
        expected_document_id: OpaqueId,
        expected_state_version: int,
        expected_metadata_version: int,
        expected_generation: int,
        decision: SyntheticValidationDecision | None = None,
        new_attempt_id: OpaqueId | None = None,
    ) -> SyntheticDocumentState:
        """Apply one canonical, deterministic transition without side effects."""

        if type(target) is not DocumentStatus:
            raise _fail(DocumentDomainCode.INVALID_TYPE)
        expected_id = _opaque(expected_document_id)
        _positive(expected_state_version, MAX_DOCUMENT_VERSION)
        _positive(expected_metadata_version, MAX_DOCUMENT_VERSION)
        _positive(expected_generation, MAX_DOCUMENT_GENERATION)
        if expected_id != self.descriptor.document_id:
            raise _fail(DocumentDomainCode.IDENTITY_MISMATCH)
        if (
            expected_state_version != self.state_version
            or expected_metadata_version != self.descriptor.metadata_version
            or expected_generation != self.generation
        ):
            raise _fail(DocumentDomainCode.STALE_STATE)
        occurred = _utc(at)
        if occurred < self.occurred_at:
            raise _fail(DocumentDomainCode.INVALID_CHRONOLOGY)
        if target not in _ALLOWED[self.status]:
            raise _fail(DocumentDomainCode.INVALID_TRANSITION)

        needs_decision = (
            self.status is DocumentStatus.VALIDATING or target is DocumentStatus.REJECTED
        )
        if needs_decision:
            self._validate_decision(decision, target, occurred)
        elif decision is not None:
            raise _fail(DocumentDomainCode.INVALID_DECISION)

        attempt_ids = self.attempt_ids
        current_attempt_id = self.current_attempt_id
        generation = self.generation
        if target is DocumentStatus.QUEUED:
            if new_attempt_id is None:
                raise _fail(DocumentDomainCode.INVALID_TRANSITION)
            attempt = _opaque(new_attempt_id)
            if attempt == self.descriptor.document_id or attempt in attempt_ids:
                raise _fail(DocumentDomainCode.DUPLICATE_IDENTITY)
            if self.status in {
                DocumentStatus.FAILED,
                DocumentStatus.NEEDS_REVIEW,
                DocumentStatus.SUCCEEDED,
            }:
                generation += 1
            attempt_ids = (*attempt_ids, attempt)
            current_attempt_id = attempt
        elif new_attempt_id is not None:
            raise _fail(DocumentDomainCode.INVALID_TRANSITION)
        if target is DocumentStatus.REJECTED:
            current_attempt_id = None

        return SyntheticDocumentState(
            descriptor=self.descriptor,
            status=target,
            state_version=self.state_version + 1,
            generation=generation,
            occurred_at=occurred,
            attempt_ids=attempt_ids,
            current_attempt_id=current_attempt_id,
        )

    def _validate_decision(
        self,
        decision: SyntheticValidationDecision | None,
        target: DocumentStatus,
        occurred: datetime,
    ) -> None:
        if type(decision) is not SyntheticValidationDecision:
            raise _fail(DocumentDomainCode.INVALID_DECISION)
        expected_disposition = (
            SyntheticValidationDisposition.SYNTHETIC_COMPATIBLE
            if target is DocumentStatus.ACCEPTED
            else SyntheticValidationDisposition.REJECTED
        )
        if (
            decision.document_id != self.descriptor.document_id
            or decision.source != self.descriptor.source
            or decision.owner_scope != self.descriptor.owner_scope
            or decision.metadata_version != self.descriptor.metadata_version
            or decision.disposition is not expected_disposition
            or decision.decided_at > occurred
            or decision.decided_at < self.occurred_at
        ):
            raise _fail(DocumentDomainCode.INVALID_DECISION)


def create_synthetic_document_state(
    descriptor: SyntheticDocumentDescriptor,
) -> SyntheticDocumentState:
    """Create the initial inert UPLOADED state from revalidated metadata."""

    snapshot = _snapshot_descriptor(descriptor)
    return SyntheticDocumentState(
        descriptor=snapshot,
        status=DocumentStatus.UPLOADED,
        state_version=1,
        generation=snapshot.generation,
        occurred_at=snapshot.declared_at,
        attempt_ids=(),
    )
