"""Descriptor-only synthetic ingestion assessment; never a file scanner."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final
from uuid import UUID

from app.modules.documents.classification import DocumentType
from app.modules.documents.contracts import SyntheticSourceRef
from app.modules.documents.domain import (
    DOCUMENT_METADATA_SCHEMA_VERSION,
    DocumentDomainCode,
    DocumentDomainError,
    SyntheticDocumentAuthority,
    SyntheticDocumentDescriptor,
    SyntheticOwnerScope,
    SyntheticRepresentation,
    _snapshot_descriptor,
)
from app.shared.types import OpaqueId

INGESTION_ASSESSMENT_SCHEMA_VERSION: Final = "synthetic-ingestion-assessment.v1"


class SyntheticIngestionDisposition(StrEnum):
    SYNTHETIC_COMPATIBLE = "SYNTHETIC_COMPATIBLE"
    REJECTED = "REJECTED"
    UNKNOWN_REQUIRES_REVIEW = "UNKNOWN_REQUIRES_REVIEW"


class SyntheticIngestionReason(StrEnum):
    DECLARED_FIXTURE_COMPATIBLE = "DECLARED_FIXTURE_COMPATIBLE"
    UNKNOWN_DOCUMENT_TYPE = "UNKNOWN_DOCUMENT_TYPE"
    UNSUPPORTED_DOCUMENT_TYPE = "UNSUPPORTED_DOCUMENT_TYPE"
    REPRESENTATION_MISMATCH = "REPRESENTATION_MISMATCH"
    SOURCE_MISMATCH = "SOURCE_MISMATCH"
    OWNER_SCOPE_MISMATCH = "OWNER_SCOPE_MISMATCH"


class SyntheticIdempotencyDisposition(StrEnum):
    MATCH = "MATCH"
    DISTINCT = "DISTINCT"
    CONFLICT = "CONFLICT"
    OWNER_SCOPE_MISMATCH = "OWNER_SCOPE_MISMATCH"


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticIngestionAssessment:
    document_id: OpaqueId = field(repr=False)
    source: SyntheticSourceRef = field(repr=False)
    owner_scope: SyntheticOwnerScope = field(repr=False)
    metadata_version: int
    disposition: SyntheticIngestionDisposition
    reason: SyntheticIngestionReason
    schema_version: str = INGESTION_ASSESSMENT_SCHEMA_VERSION
    authority: SyntheticDocumentAuthority = SyntheticDocumentAuthority.ENGINEERING_ONLY

    def __post_init__(self) -> None:
        # Reuse the descriptor constructor as the only public producer; receipts are
        # intentionally not accepted as authority by any lifecycle transition.
        if (
            type(self.document_id) is not OpaqueId
            or type(self.document_id.value) is not UUID
            or type(self.source) is not SyntheticSourceRef
            or type(self.owner_scope) is not SyntheticOwnerScope
        ):
            raise DocumentDomainError(DocumentDomainCode.INVALID_TYPE)
        if (
            type(self.disposition) is not SyntheticIngestionDisposition
            or type(self.reason) is not SyntheticIngestionReason
        ):
            raise DocumentDomainError(DocumentDomainCode.INVALID_TYPE)
        if self.schema_version != INGESTION_ASSESSMENT_SCHEMA_VERSION:
            raise DocumentDomainError(DocumentDomainCode.INVALID_VERSION)
        if self.authority is not SyntheticDocumentAuthority.ENGINEERING_ONLY:
            raise DocumentDomainError(DocumentDomainCode.INVALID_VALUE)
        if type(self.metadata_version) is not int or not 1 <= self.metadata_version <= 1_000_000:
            raise DocumentDomainError(DocumentDomainCode.INVALID_VERSION)
        valid_pairs = {
            (
                SyntheticIngestionDisposition.SYNTHETIC_COMPATIBLE,
                SyntheticIngestionReason.DECLARED_FIXTURE_COMPATIBLE,
            ),
            (
                SyntheticIngestionDisposition.UNKNOWN_REQUIRES_REVIEW,
                SyntheticIngestionReason.UNKNOWN_DOCUMENT_TYPE,
            ),
            *(
                (SyntheticIngestionDisposition.REJECTED, reason)
                for reason in (
                    SyntheticIngestionReason.UNSUPPORTED_DOCUMENT_TYPE,
                    SyntheticIngestionReason.REPRESENTATION_MISMATCH,
                    SyntheticIngestionReason.SOURCE_MISMATCH,
                    SyntheticIngestionReason.OWNER_SCOPE_MISMATCH,
                )
            ),
        }
        if (self.disposition, self.reason) not in valid_pairs:
            raise DocumentDomainError(DocumentDomainCode.INVALID_VALUE)
        object.__setattr__(self, "document_id", OpaqueId(self.document_id.value))
        object.__setattr__(self, "source", SyntheticSourceRef(self.source.value))
        object.__setattr__(self, "owner_scope", SyntheticOwnerScope(self.owner_scope.value))


def assess_synthetic_ingestion(
    descriptor: SyntheticDocumentDescriptor,
    *,
    expected_owner_scope: SyntheticOwnerScope,
    expected_source: SyntheticSourceRef,
    expected_representation: SyntheticRepresentation,
) -> SyntheticIngestionAssessment:
    """Compare declared fixture metadata without reading or validating content."""

    value = _snapshot_descriptor(descriptor)
    if (
        type(expected_owner_scope) is not SyntheticOwnerScope
        or type(expected_source) is not SyntheticSourceRef
        or type(expected_representation) is not SyntheticRepresentation
    ):
        raise DocumentDomainError(DocumentDomainCode.INVALID_TYPE)
    if value.schema_version != DOCUMENT_METADATA_SCHEMA_VERSION:
        raise DocumentDomainError(DocumentDomainCode.INVALID_VERSION)
    if value.owner_scope != expected_owner_scope:
        disposition = SyntheticIngestionDisposition.REJECTED
        reason = SyntheticIngestionReason.OWNER_SCOPE_MISMATCH
    elif value.source != expected_source:
        disposition = SyntheticIngestionDisposition.REJECTED
        reason = SyntheticIngestionReason.SOURCE_MISMATCH
    elif value.representation is not expected_representation:
        disposition = SyntheticIngestionDisposition.REJECTED
        reason = SyntheticIngestionReason.REPRESENTATION_MISMATCH
    elif value.document_type is DocumentType.UNKNOWN:
        disposition = SyntheticIngestionDisposition.UNKNOWN_REQUIRES_REVIEW
        reason = SyntheticIngestionReason.UNKNOWN_DOCUMENT_TYPE
    elif value.document_type is DocumentType.OTHER:
        disposition = SyntheticIngestionDisposition.REJECTED
        reason = SyntheticIngestionReason.UNSUPPORTED_DOCUMENT_TYPE
    else:
        disposition = SyntheticIngestionDisposition.SYNTHETIC_COMPATIBLE
        reason = SyntheticIngestionReason.DECLARED_FIXTURE_COMPATIBLE
    return SyntheticIngestionAssessment(
        document_id=value.document_id,
        source=value.source,
        owner_scope=value.owner_scope,
        metadata_version=value.metadata_version,
        disposition=disposition,
        reason=reason,
    )


def compare_owner_scoped_idempotency(
    left: SyntheticDocumentDescriptor, right: SyntheticDocumentDescriptor
) -> SyntheticIdempotencyDisposition:
    """Compare two supplied fixtures only; no lookup, cache, or digest authority."""

    first = _snapshot_descriptor(left)
    second = _snapshot_descriptor(right)
    if first.owner_scope != second.owner_scope:
        return SyntheticIdempotencyDisposition.OWNER_SCOPE_MISMATCH
    same_document = first.document_id == second.document_id
    same_key = first.idempotency_key == second.idempotency_key
    if same_document and not same_key:
        return SyntheticIdempotencyDisposition.CONFLICT
    if not same_document:
        return (
            SyntheticIdempotencyDisposition.CONFLICT
            if same_key
            else SyntheticIdempotencyDisposition.DISTINCT
        )
    comparable = (
        first.document_id,
        first.source,
        first.owner_scope,
        first.idempotency_key,
        first.sha256_claim,
        first.document_type,
        first.representation,
        first.byte_count_claim,
        first.page_count_claim,
        first.metadata_version,
        first.generation,
        first.declared_at,
        first.schema_version,
        first.authority,
    )
    other = (
        second.document_id,
        second.source,
        second.owner_scope,
        second.idempotency_key,
        second.sha256_claim,
        second.document_type,
        second.representation,
        second.byte_count_claim,
        second.page_count_claim,
        second.metadata_version,
        second.generation,
        second.declared_at,
        second.schema_version,
        second.authority,
    )
    return (
        SyntheticIdempotencyDisposition.MATCH
        if comparable == other
        else SyntheticIdempotencyDisposition.CONFLICT
    )
