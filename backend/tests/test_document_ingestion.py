"""P11-A descriptor-only assessment and owner-scope tests."""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.modules.documents.classification import DocumentType
from app.modules.documents.contracts import SyntheticSourceRef
from app.modules.documents.domain import (
    DocumentDomainError,
    SyntheticDocumentDescriptor,
    SyntheticIdempotencyKey,
    SyntheticOwnerScope,
    SyntheticRepresentation,
    SyntheticSha256,
)
from app.modules.documents.ingestion import (
    SyntheticIdempotencyDisposition,
    SyntheticIngestionAssessment,
    SyntheticIngestionDisposition,
    SyntheticIngestionReason,
    assess_synthetic_ingestion,
    compare_owner_scoped_idempotency,
)
from app.shared.types import OpaqueId


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def descriptor(**changes: object) -> SyntheticDocumentDescriptor:
    values: dict[str, object] = {
        "document_id": oid(1),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        "owner_scope": SyntheticOwnerScope("SYNTHETIC_OWNER_ALPHA"),
        "idempotency_key": SyntheticIdempotencyKey("SYNTHETIC_IDEMPOTENCY_ALPHA"),
        "sha256_claim": SyntheticSha256("b" * 64),
        "document_type": DocumentType.LAB_REPORT,
        "representation": SyntheticRepresentation.SYNTHETIC_PDF,
        "byte_count_claim": 100,
        "page_count_claim": 1,
        "metadata_version": 1,
        "generation": 1,
        "declared_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    values.update(changes)
    return SyntheticDocumentDescriptor(**values)  # type: ignore[arg-type]


def assess(value: SyntheticDocumentDescriptor) -> SyntheticIngestionAssessment:
    return assess_synthetic_ingestion(
        value,
        expected_owner_scope=SyntheticOwnerScope("SYNTHETIC_OWNER_ALPHA"),
        expected_source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        expected_representation=SyntheticRepresentation.SYNTHETIC_PDF,
    )


def test_descriptor_assessment_is_only_an_engineering_receipt() -> None:
    result = assess(descriptor())
    assert result.disposition is SyntheticIngestionDisposition.SYNTHETIC_COMPATIBLE
    assert result.reason is SyntheticIngestionReason.DECLARED_FIXTURE_COMPATIBLE
    assert "sha256" not in repr(result).lower()


@pytest.mark.parametrize(
    "kind,disposition,reason",
    [
        (
            DocumentType.UNKNOWN,
            SyntheticIngestionDisposition.UNKNOWN_REQUIRES_REVIEW,
            SyntheticIngestionReason.UNKNOWN_DOCUMENT_TYPE,
        ),
        (
            DocumentType.OTHER,
            SyntheticIngestionDisposition.REJECTED,
            SyntheticIngestionReason.UNSUPPORTED_DOCUMENT_TYPE,
        ),
    ],
)
def test_unknown_and_other_fail_closed(
    kind: DocumentType, disposition: SyntheticIngestionDisposition, reason: SyntheticIngestionReason
) -> None:
    result = assess(descriptor(document_type=kind))
    assert (result.disposition, result.reason) == (disposition, reason)


def test_owner_and_declared_representation_mismatches_reject() -> None:
    value = descriptor()
    owner = assess_synthetic_ingestion(
        value,
        expected_owner_scope=SyntheticOwnerScope("SYNTHETIC_OWNER_BETA"),
        expected_source=value.source,
        expected_representation=SyntheticRepresentation.SYNTHETIC_PDF,
    )
    representation = assess_synthetic_ingestion(
        value,
        expected_owner_scope=value.owner_scope,
        expected_source=value.source,
        expected_representation=SyntheticRepresentation.SYNTHETIC_PNG,
    )
    assert owner.reason is SyntheticIngestionReason.OWNER_SCOPE_MISMATCH
    assert representation.reason is SyntheticIngestionReason.REPRESENTATION_MISMATCH
    assert owner.disposition is representation.disposition is SyntheticIngestionDisposition.REJECTED


def test_source_mismatch_rejects_without_granting_access() -> None:
    value = descriptor()
    result = assess_synthetic_ingestion(
        value,
        expected_owner_scope=value.owner_scope,
        expected_source=SyntheticSourceRef("SYNTHETIC_SOURCE_BETA"),
        expected_representation=value.representation,
    )
    assert result.disposition is SyntheticIngestionDisposition.REJECTED
    assert result.reason is SyntheticIngestionReason.SOURCE_MISMATCH


def test_assessment_revalidates_mutated_caller_objects() -> None:
    value = descriptor()
    object.__setattr__(value, "sha256_claim", SyntheticSha256("c" * 64))
    object.__setattr__(value.sha256_claim, "value", "not-a-digest")
    with pytest.raises(DocumentDomainError):
        assess(value)


def test_idempotency_match_requires_same_owner_key_identity_and_metadata() -> None:
    first = descriptor()
    assert (
        compare_owner_scoped_idempotency(first, descriptor())
        is SyntheticIdempotencyDisposition.MATCH
    )
    assert (
        compare_owner_scoped_idempotency(first, descriptor(page_count_claim=2))
        is SyntheticIdempotencyDisposition.CONFLICT
    )
    assert (
        compare_owner_scoped_idempotency(
            first, descriptor(idempotency_key=SyntheticIdempotencyKey("SYNTHETIC_IDEMPOTENCY_BETA"))
        )
        is SyntheticIdempotencyDisposition.DISTINCT
    )


def test_digest_never_enables_cross_owner_or_cross_identity_deduplication() -> None:
    first = descriptor()
    cross_owner = descriptor(owner_scope=SyntheticOwnerScope("SYNTHETIC_OWNER_BETA"))
    other_identity = descriptor(
        document_id=oid(2), idempotency_key=SyntheticIdempotencyKey("SYNTHETIC_IDEMPOTENCY_BETA")
    )
    assert first.sha256_claim == cross_owner.sha256_claim == other_identity.sha256_claim
    assert (
        compare_owner_scoped_idempotency(first, cross_owner)
        is SyntheticIdempotencyDisposition.OWNER_SCOPE_MISMATCH
    )
    assert (
        compare_owner_scoped_idempotency(first, other_identity)
        is SyntheticIdempotencyDisposition.DISTINCT
    )


def test_direct_receipt_constructor_rejects_forged_authority_and_disposition() -> None:
    result = assess(descriptor())
    with pytest.raises(DocumentDomainError):
        replace(result, disposition="MALWARE_CLEARED")  # type: ignore[arg-type]
    with pytest.raises(DocumentDomainError):
        replace(result, authority="APPROVED")  # type: ignore[arg-type]
