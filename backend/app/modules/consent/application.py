"""Consent lifecycle and centralized consent-check application service."""

from collections.abc import Callable
from datetime import datetime

from app.events import OutboxRepository
from app.modules.consent.contracts import ConsentRepository
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
    normalize_utc,
)
from app.modules.consent.events import consent_granted_event, consent_revoked_event
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId, utc_now

type Clock = Callable[[], datetime]


class ConsentService:
    """Own consent persistence, lifecycle transitions, checks, and outbox writes."""

    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        repository: ConsentRepository | None = None,
        outbox: OutboxRepository | None = None,
        clock: Clock = utc_now,
    ) -> None:
        if repository is None:
            from app.modules.consent.infrastructure import PostgresConsentRepository

            repository = PostgresConsentRepository()
        self._database = database
        self._repository = repository
        self._outbox = outbox or OutboxRepository()
        self._clock = clock

    async def grant_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        actor_id: OpaqueId | None,
        purpose: ConsentPurpose,
        scope: ConsentScope,
        notice_version: NoticeVersion,
        expires_at: datetime | None = None,
    ) -> ConsentRecord:
        database = self._require_database()
        now = self._now()
        normalized_expiry = None if expires_at is None else normalize_utc("expires_at", expires_at)
        if normalized_expiry is not None and normalized_expiry <= now:
            raise ValueError("expires_at must be after granted_at")
        async with database.transaction() as transaction:
            stored = await self._repository.create(
                transaction,
                consent_id=OpaqueId.new(),
                subject_type=subject_type,
                subject_id=subject_id,
                actor_id=actor_id,
                purpose=purpose,
                scope=scope,
                notice_version=notice_version,
                granted_at=now,
                expires_at=normalized_expiry,
            )
            record = self._repository.to_domain(stored)
            await self._outbox.enqueue(
                transaction,
                consent_granted_event(record),
                aggregate_type="consent",
                aggregate_id=record.consent_id,
                created_at=now,
            )
            return record

    async def get_consent(self, consent_id: OpaqueId) -> ConsentRecord:
        database = self._require_database()
        async with database.transaction() as transaction:
            record = await self._repository.get(transaction, consent_id)
            if record is None:
                raise self._not_found()
            return self._repository.to_domain(record)

    async def list_consents(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose | None = None,
        status: ConsentStatus | None = None,
    ) -> tuple[ConsentRecord, ...]:
        database = self._require_database()
        async with database.transaction() as transaction:
            records = await self._repository.list_for_subject(
                transaction,
                subject_type=subject_type,
                subject_id=subject_id,
                purpose=purpose,
                status=status,
            )
            return tuple(self._repository.to_domain(record) for record in records)

    async def revoke_consent(
        self, *, consent_id: OpaqueId, reason: RevocationReason
    ) -> ConsentRecord:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            stored = await self._repository.get_for_update(transaction, consent_id)
            if stored is None:
                raise self._not_found()
            current = self._repository.to_domain(stored)
            if current.status is not ConsentStatus.GRANTED or (
                current.expires_at is not None and now >= current.expires_at
            ):
                raise ApplicationError(
                    code=ErrorCode.INVALID_STATE_TRANSITION,
                    message="The consent cannot be revoked from its current state.",
                )
            revoked = self._repository.revoke(stored, revoked_at=now, reason=reason)
            await self._outbox.enqueue(
                transaction,
                consent_revoked_event(revoked),
                aggregate_type="consent",
                aggregate_id=revoked.consent_id,
                created_at=now,
            )
            return revoked

    async def has_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
        required_scope: ConsentScope,
    ) -> bool:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            candidates = await self._repository.find_granted_matching(
                transaction,
                subject_type=subject_type,
                subject_id=subject_id,
                purpose=purpose,
            )
            return any(
                (record := self._repository.to_domain(candidate)).status is ConsentStatus.GRANTED
                and (record.expires_at is None or now < record.expires_at)
                and record.scope.covers(required_scope)
                for candidate in candidates
            )

    async def require_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
        required_scope: ConsentScope,
    ) -> None:
        if not await self.has_consent(
            subject_type=subject_type,
            subject_id=subject_id,
            purpose=purpose,
            required_scope=required_scope,
        ):
            raise ApplicationError(
                code=ErrorCode.CONSENT_REQUIRED,
                message="Consent is required for this action.",
            )

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Consent persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        return normalize_utc("consent clock", self._clock())

    @staticmethod
    def _not_found() -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message="The requested consent record was not found.",
        )
