"""Versioned HTTP transport and subject authorization for consent."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.security.authorization import get_actor_context
from app.api.security.bearer import parse_bearer
from app.modules.consent.contracts import (
    GrantConsentCapability,
    ListConsentCapability,
    ReadConsentCapability,
    RevokeConsentCapability,
)
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId


class GrantConsentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_type: ConsentSubjectType
    subject_id: UUID
    purpose: ConsentPurpose
    scope: tuple[str, ...] = Field(min_length=1, max_length=32)
    notice_version: str = Field(min_length=1, max_length=64)

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return ConsentScope(value).values

    @field_validator("notice_version")
    @classmethod
    def validate_notice_version(cls, value: str) -> str:
        return str(NoticeVersion(value))


class RevokeConsentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1, max_length=64)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        return str(RevocationReason(value))


class ConsentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_id: UUID
    subject_type: ConsentSubjectType
    subject_id: UUID
    purpose: ConsentPurpose
    scope: tuple[str, ...]
    notice_version: str
    status: ConsentStatus
    granted_at: datetime
    revoked_at: datetime | None
    revocation_reason: str | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


def _view(record: ConsentRecord) -> ConsentResponse:
    return ConsentResponse(
        consent_id=record.consent_id.value,
        subject_type=record.subject_type,
        subject_id=record.subject_id.value,
        purpose=record.purpose,
        scope=record.scope.values,
        notice_version=str(record.notice_version),
        status=record.status,
        granted_at=record.granted_at,
        revoked_at=record.revoked_at,
        revocation_reason=(
            None if record.revocation_reason is None else str(record.revocation_reason)
        ),
        expires_at=record.expires_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


async def _authorize_subject(
    request: Request,
    *,
    subject_type: ConsentSubjectType,
    subject_id: OpaqueId,
    authorization: str | None,
) -> OpaqueId | None:
    if subject_type is ConsentSubjectType.PATIENT:
        raise ApplicationError(
            code=ErrorCode.VALIDATION_ERROR,
            message="Patient consent management is not available until patient linkage exists.",
        )
    actor_context = get_actor_context(request)
    if subject_type is ConsentSubjectType.SESSION:
        token = parse_bearer(authorization)
        validator = request.app.state.capability_registry.resolve(SESSIONS_VALIDATE)
        await validator.validate_session(session_id=subject_id, session_token=token)
        return actor_context.actor_id if actor_context.is_authenticated else None
    if not actor_context.is_authenticated or actor_context.actor_id is None:
        raise ApplicationError(
            code=ErrorCode.AUTHENTICATION_REQUIRED,
            message="A valid authenticated actor is required.",
        )
    if actor_context.actor_id != subject_id:
        raise ApplicationError(
            code=ErrorCode.AUTHORIZATION_DENIED,
            message="The authenticated actor is not permitted to access this subject.",
        )
    return actor_context.actor_id


def build_consent_router(
    *,
    grant: GrantConsentCapability,
    reader: ReadConsentCapability,
    listing: ListConsentCapability,
    revoke: RevokeConsentCapability,
) -> APIRouter:
    router = APIRouter(prefix="/consents", tags=["consent"])

    @router.post("", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
    async def grant_consent(
        payload: GrantConsentRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> ConsentResponse:
        response.headers["Cache-Control"] = "no-store"
        subject_id = OpaqueId(payload.subject_id)
        actor_id = await _authorize_subject(
            request,
            subject_type=payload.subject_type,
            subject_id=subject_id,
            authorization=authorization,
        )
        record = await grant.grant_consent(
            subject_type=payload.subject_type,
            subject_id=subject_id,
            actor_id=actor_id,
            purpose=payload.purpose,
            scope=ConsentScope(payload.scope),
            notice_version=NoticeVersion(payload.notice_version),
        )
        return _view(record)

    @router.post("/{consent_id}/revoke", response_model=ConsentResponse)
    async def revoke_consent(
        consent_id: UUID,
        payload: RevokeConsentRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> ConsentResponse:
        response.headers["Cache-Control"] = "no-store"
        current = await reader.get_consent(OpaqueId(consent_id))
        await _authorize_subject(
            request,
            subject_type=current.subject_type,
            subject_id=current.subject_id,
            authorization=authorization,
        )
        return _view(
            await revoke.revoke_consent(
                consent_id=current.consent_id,
                reason=RevocationReason(payload.reason),
            )
        )

    @router.get("", response_model=list[ConsentResponse])
    async def list_consents(
        request: Request,
        response: Response,
        subject_type: Annotated[ConsentSubjectType, Query()],
        subject_id: Annotated[UUID, Query()],
        purpose: Annotated[ConsentPurpose | None, Query()] = None,
        consent_status: Annotated[ConsentStatus | None, Query(alias="status")] = None,
        authorization: Annotated[str | None, Header()] = None,
    ) -> list[ConsentResponse]:
        response.headers["Cache-Control"] = "no-store"
        opaque_subject_id = OpaqueId(subject_id)
        await _authorize_subject(
            request,
            subject_type=subject_type,
            subject_id=opaque_subject_id,
            authorization=authorization,
        )
        records = await listing.list_consents(
            subject_type=subject_type,
            subject_id=opaque_subject_id,
            purpose=purpose,
            status=consent_status,
        )
        return [_view(record) for record in records]

    return router
