"""Consent application-service lifecycle and centralized-check tests."""

from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pytest

from app.events import EventEnvelope
from app.modules.consent.application import ConsentService
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 11, 8, tzinfo=UTC)


class FakeDatabase:
    def __init__(self) -> None:
        self.transactions = 0

    @asynccontextmanager
    async def transaction(self) -> Any:
        self.transactions += 1
        yield object()


class FakeConsentRepository:
    def __init__(self, records: tuple[ConsentRecord, ...] = ()) -> None:
        self.records = {record.consent_id: record for record in records}
        self.created = 0
        self.locked = 0

    async def create(self, session: object, **values: object) -> ConsentRecord:
        self.created += 1
        record = ConsentRecord(
            consent_id=values["consent_id"],  # type: ignore[arg-type]
            subject_type=values["subject_type"],  # type: ignore[arg-type]
            subject_id=values["subject_id"],  # type: ignore[arg-type]
            actor_id=values["actor_id"],  # type: ignore[arg-type]
            purpose=values["purpose"],  # type: ignore[arg-type]
            scope=values["scope"],  # type: ignore[arg-type]
            notice_version=values["notice_version"],  # type: ignore[arg-type]
            status=ConsentStatus.GRANTED,
            granted_at=values["granted_at"],  # type: ignore[arg-type]
            revoked_at=None,
            revocation_reason=None,
            expires_at=values["expires_at"],  # type: ignore[arg-type]
            metadata=None,
            created_at=values["granted_at"],  # type: ignore[arg-type]
            updated_at=values["granted_at"],  # type: ignore[arg-type]
        )
        self.records[record.consent_id] = record
        return record

    async def get(self, session: object, consent_id: OpaqueId) -> ConsentRecord | None:
        return self.records.get(consent_id)

    async def get_for_update(self, session: object, consent_id: OpaqueId) -> ConsentRecord | None:
        self.locked += 1
        return self.records.get(consent_id)

    async def list_for_subject(
        self,
        session: object,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose | None,
        status: ConsentStatus | None,
    ) -> tuple[ConsentRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.subject_type is subject_type
            and record.subject_id == subject_id
            and (purpose is None or record.purpose is purpose)
            and (status is None or record.status is status)
        )

    async def find_granted_matching(
        self,
        session: object,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
    ) -> tuple[ConsentRecord, ...]:
        return tuple(
            record
            for record in self.records.values()
            if record.subject_type is subject_type
            and record.subject_id == subject_id
            and record.purpose is purpose
        )

    def revoke(
        self,
        record: object,
        *,
        revoked_at: datetime,
        reason: RevocationReason,
    ) -> ConsentRecord:
        assert isinstance(record, ConsentRecord)
        revoked = ConsentRecord(
            consent_id=record.consent_id,
            subject_type=record.subject_type,
            subject_id=record.subject_id,
            actor_id=record.actor_id,
            purpose=record.purpose,
            scope=record.scope,
            notice_version=record.notice_version,
            status=ConsentStatus.REVOKED,
            granted_at=record.granted_at,
            revoked_at=revoked_at,
            revocation_reason=reason,
            expires_at=record.expires_at,
            metadata=record.metadata,
            created_at=record.created_at,
            updated_at=revoked_at,
        )
        self.records[record.consent_id] = revoked
        return revoked

    def to_domain(self, record: object) -> ConsentRecord:
        assert isinstance(record, ConsentRecord)
        return record


class CapturingOutbox:
    def __init__(self) -> None:
        self.enqueued: list[tuple[EventEnvelope, str | None, OpaqueId | None]] = []

    async def enqueue(
        self,
        session: object,
        event: EventEnvelope,
        *,
        aggregate_type: str | None = None,
        aggregate_id: OpaqueId | None = None,
        **_: object,
    ) -> object:
        self.enqueued.append((event, aggregate_type, aggregate_id))
        return object()


def _record(
    *,
    subject_id: OpaqueId,
    purpose: ConsentPurpose = ConsentPurpose.GENERAL_PRODUCT_USE,
    scope: tuple[str, ...] = ("clinical_intake",),
    status: ConsentStatus = ConsentStatus.GRANTED,
    expires_at: datetime | None = None,
) -> ConsentRecord:
    revoked = status is ConsentStatus.REVOKED
    return ConsentRecord(
        consent_id=OpaqueId.new(),
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=purpose,
        scope=ConsentScope(scope),
        notice_version=NoticeVersion("privacy-v1"),
        status=status,
        granted_at=NOW - timedelta(hours=1),
        revoked_at=NOW - timedelta(minutes=1) if revoked else None,
        revocation_reason=RevocationReason("user_requested") if revoked else None,
        expires_at=expires_at,
        metadata=None,
        created_at=NOW - timedelta(hours=1),
        updated_at=NOW - timedelta(minutes=1) if revoked else NOW - timedelta(hours=1),
    )


async def test_grant_normalizes_clock_and_enqueues_minimal_event_in_one_transaction() -> None:
    database = FakeDatabase()
    repository = FakeConsentRepository()
    outbox = CapturingOutbox()
    offset = timezone(timedelta(hours=5, minutes=30))
    service = ConsentService(
        database=database,  # type: ignore[arg-type]
        repository=repository,
        outbox=outbox,  # type: ignore[arg-type]
        clock=lambda: datetime(2026, 10, 11, 13, 30, tzinfo=offset),
    )
    subject_id = OpaqueId.new()

    record = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("clinical_intake",)),
        notice_version=NoticeVersion("privacy-v1"),
    )

    assert record.granted_at == NOW
    assert database.transactions == repository.created == 1
    assert len(outbox.enqueued) == 1
    event, aggregate_type, aggregate_id = outbox.enqueued[0]
    assert event.to_dict()["event_type"] == "ConsentGranted"
    assert aggregate_type == "consent"
    assert aggregate_id == record.consent_id


async def test_naive_clock_is_rejected_before_transaction_or_mutation() -> None:
    database = FakeDatabase()
    repository = FakeConsentRepository()
    outbox = CapturingOutbox()
    service = ConsentService(
        database=database,  # type: ignore[arg-type]
        repository=repository,
        outbox=outbox,  # type: ignore[arg-type]
        clock=lambda: datetime(2026, 10, 11, 8),
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        await service.grant_consent(
            subject_type=ConsentSubjectType.SESSION,
            subject_id=OpaqueId.new(),
            actor_id=None,
            purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
            scope=ConsentScope(("clinical_intake",)),
            notice_version=NoticeVersion("privacy-v1"),
        )

    assert database.transactions == repository.created == 0
    assert outbox.enqueued == []


async def test_checker_requires_exact_purpose_subset_scope_granted_and_unexpired() -> None:
    subject_id = OpaqueId.new()
    records = (
        _record(subject_id=subject_id, scope=("clinical_intake", "document_upload")),
        _record(
            subject_id=subject_id,
            purpose=ConsentPurpose.REFERRAL_SHARING,
            scope=("referral_summary",),
        ),
        _record(subject_id=subject_id, status=ConsentStatus.REVOKED),
        _record(subject_id=subject_id, scope=("expired_scope",), expires_at=NOW),
    )
    service = ConsentService(
        database=FakeDatabase(),  # type: ignore[arg-type]
        repository=FakeConsentRepository(records),
        outbox=CapturingOutbox(),  # type: ignore[arg-type]
        clock=lambda: NOW,
    )

    assert await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        required_scope=ConsentScope(("clinical_intake",)),
    )
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        required_scope=ConsentScope(("referral_summary",)),
    )
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.REFERRAL_SHARING,
        required_scope=ConsentScope(("clinical_intake",)),
    )
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        required_scope=ConsentScope(("expired_scope",)),
    )

    with pytest.raises(SwasthyaSetuError) as error:
        await service.require_consent(
            subject_type=ConsentSubjectType.SESSION,
            subject_id=subject_id,
            purpose=ConsentPurpose.REFERRAL_SHARING,
            required_scope=ConsentScope(("clinical_intake",)),
        )
    assert error.value.code is ErrorCode.CONSENT_REQUIRED


async def test_revoke_locks_one_grant_and_failed_repeat_emits_no_second_event() -> None:
    subject_id = OpaqueId.new()
    granted = _record(subject_id=subject_id)
    repository = FakeConsentRepository((granted,))
    outbox = CapturingOutbox()
    service = ConsentService(
        database=FakeDatabase(),  # type: ignore[arg-type]
        repository=repository,
        outbox=outbox,  # type: ignore[arg-type]
        clock=lambda: NOW,
    )

    revoked = await service.revoke_consent(
        consent_id=granted.consent_id,
        reason=RevocationReason("user_requested"),
    )
    assert revoked.status is ConsentStatus.REVOKED
    assert revoked.revoked_at == NOW
    assert repository.locked == 1
    assert len(outbox.enqueued) == 1

    with pytest.raises(SwasthyaSetuError) as error:
        await service.revoke_consent(
            consent_id=granted.consent_id,
            reason=RevocationReason("user_requested"),
        )
    assert error.value.code is ErrorCode.INVALID_STATE_TRANSITION
    assert len(outbox.enqueued) == 1


@pytest.mark.parametrize(
    "status",
    [ConsentStatus.REVOKED, ConsentStatus.EXPIRED, ConsentStatus.SUPERSEDED],
)
async def test_checker_rejects_every_non_granted_status(status: ConsentStatus) -> None:
    subject_id = OpaqueId.new()
    record = _record(subject_id=subject_id, status=status)
    service = ConsentService(
        database=FakeDatabase(),  # type: ignore[arg-type]
        repository=FakeConsentRepository((record,)),
        outbox=CapturingOutbox(),  # type: ignore[arg-type]
        clock=lambda: NOW,
    )

    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        required_scope=ConsentScope(("clinical_intake",)),
    )


async def test_database_disabled_operations_fail_honestly() -> None:
    service = ConsentService(
        database=None,
        repository=FakeConsentRepository(),
        outbox=CapturingOutbox(),  # type: ignore[arg-type]
    )

    with pytest.raises(SwasthyaSetuError) as error:
        await service.list_consents(
            subject_type=ConsentSubjectType.SESSION,
            subject_id=OpaqueId.new(),
        )
    assert error.value.code is ErrorCode.DEPENDENCY_UNAVAILABLE
