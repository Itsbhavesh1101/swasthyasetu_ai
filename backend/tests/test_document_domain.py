"""P11-A pure synthetic document-domain tests."""

import traceback
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.jobs import JobStatus
from app.modules.documents.classification import DocumentType
from app.modules.documents.contracts import ResultStatus, SyntheticSourceRef
from app.modules.documents.domain import (
    DOCUMENT_METADATA_SCHEMA_VERSION,
    MAX_SYNTHETIC_BYTE_COUNT_CLAIM,
    MAX_SYNTHETIC_PAGE_COUNT_CLAIM,
    DocumentDomainCode,
    DocumentDomainError,
    DocumentStatus,
    SyntheticDocumentAuthority,
    SyntheticDocumentDescriptor,
    SyntheticDocumentState,
    SyntheticIdempotencyKey,
    SyntheticOwnerScope,
    SyntheticRepresentation,
    SyntheticSha256,
    SyntheticValidationDecision,
    SyntheticValidationDisposition,
    create_synthetic_document_state,
)
from app.modules.documents.processing import AttemptStatus
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def descriptor(**changes: object) -> SyntheticDocumentDescriptor:
    values: dict[str, object] = {
        "document_id": oid(1),
        "source": SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
        "owner_scope": SyntheticOwnerScope("SYNTHETIC_OWNER_ALPHA"),
        "idempotency_key": SyntheticIdempotencyKey("SYNTHETIC_IDEMPOTENCY_ALPHA"),
        "sha256_claim": SyntheticSha256("a" * 64),
        "document_type": DocumentType.UNKNOWN,
        "representation": SyntheticRepresentation.SYNTHETIC_PDF,
        "byte_count_claim": 1024,
        "page_count_claim": 2,
        "metadata_version": 1,
        "generation": 1,
        "declared_at": NOW,
    }
    values.update(changes)
    return SyntheticDocumentDescriptor(**values)  # type: ignore[arg-type]


def decision(
    disposition: SyntheticValidationDisposition, *, at: datetime = NOW
) -> SyntheticValidationDecision:
    value = descriptor()
    return SyntheticValidationDecision(
        document_id=value.document_id,
        source=value.source,
        owner_scope=value.owner_scope,
        metadata_version=value.metadata_version,
        disposition=disposition,
        decided_at=at,
    )


def transition(
    state: SyntheticDocumentState, target: DocumentStatus, **extra: object
) -> SyntheticDocumentState:
    values: dict[str, object] = {
        "at": NOW,
        "expected_document_id": oid(1),
        "expected_state_version": state.state_version,
        "expected_metadata_version": 1,
        "expected_generation": state.generation,
    }
    values.update(extra)
    return state.transition(target, **values)  # type: ignore[arg-type]


def accepted_state() -> SyntheticDocumentState:
    uploaded = create_synthetic_document_state(descriptor())
    validating = transition(uploaded, DocumentStatus.VALIDATING)
    return transition(
        validating,
        DocumentStatus.ACCEPTED,
        decision=decision(SyntheticValidationDisposition.SYNTHETIC_COMPATIBLE),
    )


def test_descriptor_is_frozen_closed_bounded_and_utc_normalized() -> None:
    value = descriptor(
        declared_at=datetime(2026, 1, 2, 8, 34, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    )
    assert value.declared_at == NOW
    assert value.schema_version == DOCUMENT_METADATA_SCHEMA_VERSION
    assert value.authority is SyntheticDocumentAuthority.ENGINEERING_ONLY
    assert set(DocumentStatus) == {
        DocumentStatus.UPLOADED,
        DocumentStatus.VALIDATING,
        DocumentStatus.ACCEPTED,
        DocumentStatus.QUEUED,
        DocumentStatus.PROCESSING,
        DocumentStatus.NEEDS_REVIEW,
        DocumentStatus.SUCCEEDED,
        DocumentStatus.FAILED,
        DocumentStatus.REJECTED,
    }
    with pytest.raises(FrozenInstanceError):
        value.page_count_claim = 3  # type: ignore[misc]


@pytest.mark.parametrize(
    "field,bad",
    [
        ("document_id", UUID(int=1)),
        ("document_type", "UNKNOWN"),
        ("representation", "SYNTHETIC_PDF"),
        ("byte_count_claim", True),
        ("byte_count_claim", 1.0),
        ("page_count_claim", True),
        ("metadata_version", 1.0),
        ("generation", False),
        ("declared_at", NOW.replace(tzinfo=None)),
    ],
)
def test_descriptor_direct_constructor_rejects_type_lookalikes(field: str, bad: object) -> None:
    with pytest.raises(DocumentDomainError):
        descriptor(**{field: bad})


@pytest.mark.parametrize(
    "field,bad",
    [
        ("byte_count_claim", MAX_SYNTHETIC_BYTE_COUNT_CLAIM + 1),
        ("page_count_claim", MAX_SYNTHETIC_PAGE_COUNT_CLAIM + 1),
        ("metadata_version", 0),
        ("generation", 101),
        ("schema_version", "synthetic-document-metadata.v2"),
    ],
)
def test_descriptor_rejects_oversize_and_invalid_versions(field: str, bad: object) -> None:
    with pytest.raises(DocumentDomainError):
        descriptor(**{field: bad})


@pytest.mark.parametrize(
    "factory,value",
    [
        (SyntheticOwnerScope, "PATIENT_123"),
        (SyntheticIdempotencyKey, "SYNTHETIC_OWNER_ALPHA"),
        (SyntheticSha256, "A" * 64),
        (SyntheticSha256, "a" * 63),
    ],
)
def test_linkage_tokens_are_strict(factory: object, value: str) -> None:
    with pytest.raises(DocumentDomainError):
        factory(value)  # type: ignore[operator]


def test_sensitive_looking_values_are_hidden_from_repr_errors_and_traceback() -> None:
    value = descriptor()
    rendered = repr(value)
    for canary in (
        str(value.document_id),
        value.source.value,
        value.owner_scope.value,
        value.idempotency_key.value,
        value.sha256_claim.value,
    ):
        assert canary not in rendered
    canary = "private-canary-owner"
    with pytest.raises(DocumentDomainError) as raised:
        SyntheticOwnerScope(canary)
    formatted = "".join(traceback.format_exception(raised.value))
    assert canary not in str(raised.value)
    assert canary not in repr(raised.value)
    assert canary not in formatted


def test_all_canonical_edges_are_allowed_and_versions_are_monotonic() -> None:
    uploaded = create_synthetic_document_state(descriptor())
    validating = transition(uploaded, DocumentStatus.VALIDATING)
    accepted = transition(
        validating,
        DocumentStatus.ACCEPTED,
        decision=decision(SyntheticValidationDisposition.SYNTHETIC_COMPATIBLE),
    )
    queued = transition(accepted, DocumentStatus.QUEUED, new_attempt_id=oid(2))
    processing = transition(queued, DocumentStatus.PROCESSING)
    for target in (DocumentStatus.NEEDS_REVIEW, DocumentStatus.SUCCEEDED, DocumentStatus.FAILED):
        finished = transition(processing, target)
        requeued = transition(finished, DocumentStatus.QUEUED, new_attempt_id=oid(3))
        assert requeued.generation == 2
        assert requeued.attempt_ids == (oid(2), oid(3))
        assert requeued.state_version == finished.state_version + 1
    for origin in (validating, accepted, queued, processing):
        rejected = transition(
            origin,
            DocumentStatus.REJECTED,
            decision=decision(SyntheticValidationDisposition.REJECTED),
        )
        assert rejected.status is DocumentStatus.REJECTED
    assert [
        uploaded.state_version,
        validating.state_version,
        accepted.state_version,
        queued.state_version,
        processing.state_version,
    ] == [1, 2, 3, 4, 5]


def test_every_forbidden_edge_is_rejected() -> None:
    states = {DocumentStatus.UPLOADED: create_synthetic_document_state(descriptor())}
    states[DocumentStatus.VALIDATING] = transition(
        states[DocumentStatus.UPLOADED], DocumentStatus.VALIDATING
    )
    states[DocumentStatus.ACCEPTED] = transition(
        states[DocumentStatus.VALIDATING],
        DocumentStatus.ACCEPTED,
        decision=decision(SyntheticValidationDisposition.SYNTHETIC_COMPATIBLE),
    )
    states[DocumentStatus.QUEUED] = transition(
        states[DocumentStatus.ACCEPTED], DocumentStatus.QUEUED, new_attempt_id=oid(2)
    )
    states[DocumentStatus.PROCESSING] = transition(
        states[DocumentStatus.QUEUED], DocumentStatus.PROCESSING
    )
    for target in (DocumentStatus.NEEDS_REVIEW, DocumentStatus.SUCCEEDED, DocumentStatus.FAILED):
        states[target] = transition(states[DocumentStatus.PROCESSING], target)
    states[DocumentStatus.REJECTED] = transition(
        states[DocumentStatus.VALIDATING],
        DocumentStatus.REJECTED,
        decision=decision(SyntheticValidationDisposition.REJECTED),
    )
    allowed = {
        (DocumentStatus.UPLOADED, DocumentStatus.VALIDATING),
        (DocumentStatus.VALIDATING, DocumentStatus.ACCEPTED),
        (DocumentStatus.VALIDATING, DocumentStatus.REJECTED),
        (DocumentStatus.ACCEPTED, DocumentStatus.QUEUED),
        (DocumentStatus.ACCEPTED, DocumentStatus.REJECTED),
        (DocumentStatus.QUEUED, DocumentStatus.PROCESSING),
        (DocumentStatus.QUEUED, DocumentStatus.FAILED),
        (DocumentStatus.QUEUED, DocumentStatus.REJECTED),
        (DocumentStatus.PROCESSING, DocumentStatus.NEEDS_REVIEW),
        (DocumentStatus.PROCESSING, DocumentStatus.SUCCEEDED),
        (DocumentStatus.PROCESSING, DocumentStatus.FAILED),
        (DocumentStatus.PROCESSING, DocumentStatus.REJECTED),
        (DocumentStatus.FAILED, DocumentStatus.QUEUED),
        (DocumentStatus.NEEDS_REVIEW, DocumentStatus.QUEUED),
        (DocumentStatus.SUCCEEDED, DocumentStatus.QUEUED),
    }
    for origin in DocumentStatus:
        for target in DocumentStatus:
            if (origin, target) in allowed:
                continue
            with pytest.raises(DocumentDomainError) as raised:
                transition(states[origin], target)
            assert raised.value.code is DocumentDomainCode.INVALID_TRANSITION


def test_validation_acceptance_is_explicit_synthetic_and_unforgeable() -> None:
    validating = transition(
        create_synthetic_document_state(descriptor()), DocumentStatus.VALIDATING
    )
    with pytest.raises(DocumentDomainError):
        transition(validating, DocumentStatus.ACCEPTED)
    for forged in (
        "MALWARE_CLEARED",
        "APPROVED",
        "CONSENT_GRANTED",
        "CLINICIAN_CONFIRMED",
        "SIGNED",
    ):
        with pytest.raises(DocumentDomainError):
            SyntheticValidationDecision(
                document_id=oid(1),
                source=SyntheticSourceRef("SYNTHETIC_SOURCE_ALPHA"),
                owner_scope=SyntheticOwnerScope("SYNTHETIC_OWNER_ALPHA"),
                metadata_version=1,
                disposition=forged,  # type: ignore[arg-type]
                decided_at=NOW,
            )


def test_stale_cross_identity_chronology_and_attempt_replay_fail_closed() -> None:
    accepted = accepted_state()
    cases = (
        {"expected_document_id": oid(9)},
        {"expected_state_version": 2},
        {"expected_metadata_version": 2},
        {"expected_generation": 2},
        {"at": NOW - timedelta(seconds=1)},
    )
    for case in cases:
        with pytest.raises(DocumentDomainError):
            transition(accepted, DocumentStatus.QUEUED, new_attempt_id=oid(2), **case)
    queued = transition(accepted, DocumentStatus.QUEUED, new_attempt_id=oid(2))
    failed = transition(queued, DocumentStatus.FAILED)
    with pytest.raises(DocumentDomainError):
        transition(failed, DocumentStatus.QUEUED, new_attempt_id=oid(2))
    with pytest.raises(DocumentDomainError):
        transition(failed, DocumentStatus.QUEUED)


def test_direct_state_constructor_rejects_incoherent_or_mutable_nested_state() -> None:
    uploaded = create_synthetic_document_state(descriptor())
    with pytest.raises(DocumentDomainError):
        replace(uploaded, status=DocumentStatus.PROCESSING)
    with pytest.raises(DocumentDomainError):
        replace(uploaded, attempt_ids=[oid(2)])  # type: ignore[arg-type]
    with pytest.raises(DocumentDomainError):
        replace(uploaded, occurred_at=NOW - timedelta(seconds=1))


def test_document_attempt_ocr_and_job_statuses_are_distinct() -> None:
    status_types: tuple[type[object], ...] = (
        DocumentStatus,
        AttemptStatus,
        ResultStatus,
        JobStatus,
    )
    assert len(set(status_types)) == 4
    assert type(DocumentStatus.SUCCEEDED) is DocumentStatus
    assert type(AttemptStatus.SUCCEEDED) is AttemptStatus
    assert type(ResultStatus.SUCCEEDED) is ResultStatus
    assert type(JobStatus.SUCCEEDED) is JobStatus
