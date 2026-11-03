"""Authenticated patient API for consent-gated wellness guidance."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.api.security.authorization import get_actor_context
from app.api.security.patient_authentication import PatientAuthenticator, authenticate_patient
from app.modules.consent.application import ConsentService
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.self_care.guidance_contracts import GuidanceOutcome, GuidanceQuestion
from app.modules.self_care.guidance_service import GuidanceService
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

_SCOPE = ConsentScope(("ayurvedic_guidance",))
_NOTICE = NoticeVersion("external-ai-v1")


class GuidanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=1_000)


class CitationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    url: str


class GuidanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome: GuidanceOutcome
    answer: str | None
    citations: tuple[CitationResponse, ...]
    retrieved_at: datetime | None


class GuidanceConsentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active: bool
    notice_version: str = str(_NOTICE)
    scope: tuple[str, ...] = _SCOPE.values


def build_guidance_router(
    *,
    service: GuidanceService,
    consent: ConsentService,
    authenticator: PatientAuthenticator,
) -> APIRouter:
    async def require_patient(
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> None:
        await authenticate_patient(request, authorization, authenticator=authenticator)

    router = APIRouter(
        prefix="/guidance",
        tags=["wellness-guidance"],
        dependencies=[Depends(require_patient)],
    )

    def actor_id(request: Request) -> OpaqueId:
        actor = get_actor_context(request)
        if not actor.is_authenticated or actor.actor_id is None:
            raise ApplicationError(
                code=ErrorCode.AUTHENTICATION_REQUIRED,
                message="A valid patient account is required.",
            )
        return actor.actor_id

    async def active(request: Request) -> bool:
        return await consent.has_active_consent(
            subject_type=ConsentSubjectType.ACTOR,
            subject_id=actor_id(request),
            purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
            required_scope=_SCOPE,
            notice_version=_NOTICE,
        )

    @router.get("/consent", response_model=GuidanceConsentResponse)
    async def consent_status(request: Request, response: Response) -> GuidanceConsentResponse:
        response.headers["Cache-Control"] = "no-store"
        return GuidanceConsentResponse(active=await active(request))

    @router.post(
        "/consent",
        response_model=GuidanceConsentResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def grant_guidance_consent(
        request: Request, response: Response
    ) -> GuidanceConsentResponse:
        response.headers["Cache-Control"] = "no-store"
        subject_id = actor_id(request)
        if not await active(request):
            await consent.grant_consent(
                subject_type=ConsentSubjectType.ACTOR,
                subject_id=subject_id,
                actor_id=subject_id,
                purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
                scope=_SCOPE,
                notice_version=_NOTICE,
            )
        return GuidanceConsentResponse(active=True)

    @router.delete(
        "/consent",
        response_model=GuidanceConsentResponse,
    )
    async def revoke_guidance_consent(
        request: Request, response: Response
    ) -> GuidanceConsentResponse:
        response.headers["Cache-Control"] = "no-store"
        subject_id = actor_id(request)
        records = await consent.list_consents(
            subject_type=ConsentSubjectType.ACTOR,
            subject_id=subject_id,
            purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
            status=ConsentStatus.GRANTED,
        )
        for record in records:
            if record.notice_version == _NOTICE and record.scope.covers(_SCOPE):
                await consent.revoke_consent(
                    consent_id=record.consent_id,
                    reason=RevocationReason("user_requested"),
                )
        return GuidanceConsentResponse(active=False)

    @router.post("/ayurveda", response_model=GuidanceResponse)
    async def answer_guidance(
        request: Request,
        response: Response,
    ) -> GuidanceResponse:
        response.headers["Cache-Control"] = "no-store"
        try:
            payload = GuidanceRequest.model_validate(await request.json())
        except ValueError as exc:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The guidance request is invalid.",
                cause=exc,
            ) from exc
        answer = await service.answer(
            GuidanceQuestion(text=payload.question), get_actor_context(request)
        )
        return GuidanceResponse(
            outcome=answer.outcome,
            answer=answer.answer,
            citations=tuple(
                CitationResponse(title=citation.title, url=citation.url)
                for citation in answer.citations
            ),
            retrieved_at=answer.retrieved_at,
        )

    return router


__all__ = ["build_guidance_router"]
