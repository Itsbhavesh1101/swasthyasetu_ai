"""Consent application capability contracts."""

from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.shared.types import OpaqueId


class ConsentRepository(Protocol):
    async def create(
        self,
        session: AsyncSession,
        *,
        consent_id: OpaqueId,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        actor_id: OpaqueId | None,
        purpose: ConsentPurpose,
        scope: ConsentScope,
        notice_version: NoticeVersion,
        granted_at: datetime,
        expires_at: datetime | None,
    ) -> object: ...

    async def get(self, session: AsyncSession, consent_id: OpaqueId) -> object | None: ...

    async def get_for_update(
        self, session: AsyncSession, consent_id: OpaqueId
    ) -> object | None: ...

    async def list_for_subject(
        self,
        session: AsyncSession,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose | None,
        status: ConsentStatus | None,
    ) -> tuple[object, ...]: ...

    async def find_granted_matching(
        self,
        session: AsyncSession,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
    ) -> tuple[object, ...]: ...

    def revoke(
        self,
        record: object,
        *,
        revoked_at: datetime,
        reason: RevocationReason,
    ) -> ConsentRecord: ...

    def to_domain(self, record: object) -> ConsentRecord: ...


class GrantConsentCapability(Protocol):
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
    ) -> ConsentRecord: ...


class ReadConsentCapability(Protocol):
    async def get_consent(self, consent_id: OpaqueId) -> ConsentRecord: ...


class ListConsentCapability(Protocol):
    async def list_consents(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose | None = None,
        status: ConsentStatus | None = None,
    ) -> tuple[ConsentRecord, ...]: ...


class RevokeConsentCapability(Protocol):
    async def revoke_consent(
        self, *, consent_id: OpaqueId, reason: RevocationReason
    ) -> ConsentRecord: ...


class CheckConsentCapability(Protocol):
    async def has_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
        required_scope: ConsentScope,
    ) -> bool: ...

    async def require_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
        required_scope: ConsentScope,
    ) -> None: ...
