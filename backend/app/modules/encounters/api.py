"""Session-bound and self-authorized encounter HTTP APIs."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Request, Response, status
from pydantic import BaseModel, ConfigDict

from app.api.security.authorization import get_actor_context
from app.api.security.bearer import parse_bearer
from app.modules.encounters.contracts import (
    CreateEncounterCapability,
    ReadEncounterCapability,
    TransitionEncounterCapability,
)
from app.modules.encounters.domain import Encounter, EncounterStatus, EncounterType
from app.modules.identity.authorization import ENCOUNTER_READ_SELF, ENCOUNTER_WRITE_SELF
from app.modules.identity.domain import PermissionCode
from app.modules.identity.public import IDENTITY_AUTHORIZE
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId


class CreateEncounterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: UUID
    patient_id: UUID | None
    encounter_type: EncounterType


class EncounterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    encounter_id: UUID
    patient_id: UUID | None
    session_id: UUID
    encounter_type: EncounterType
    status: EncounterStatus
    started_at: datetime
    completed_at: datetime | None
    language_context: str | None


def encounter_view(value: Encounter) -> EncounterResponse:
    return EncounterResponse(
        encounter_id=value.encounter_id.value,
        patient_id=None if value.patient_id is None else value.patient_id.value,
        session_id=value.session_id.value,
        encounter_type=value.encounter_type,
        status=value.status,
        started_at=value.started_at,
        completed_at=value.completed_at,
        language_context=value.language_context,
    )


async def _authorize_existing(
    request: Request,
    encounter: Encounter,
    *,
    permission: PermissionCode,
    authorization_header: str | None,
) -> None:
    if encounter.patient_id is not None:
        service = request.app.state.capability_registry.resolve(IDENTITY_AUTHORIZE)
        service.require_self_subject(get_actor_context(request), permission, encounter.patient_id)
        return
    token = parse_bearer(authorization_header)
    sessions = request.app.state.capability_registry.resolve(SESSIONS_VALIDATE)
    await sessions.validate_session(session_id=encounter.session_id, session_token=token)


def build_encounters_router(
    *,
    creator: CreateEncounterCapability,
    reader: ReadEncounterCapability,
    transitions: TransitionEncounterCapability,
) -> APIRouter:
    router = APIRouter(prefix="/encounters", tags=["encounters"])

    @router.post("", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
    async def create_encounter(
        payload: CreateEncounterRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> EncounterResponse:
        response.headers["Cache-Control"] = "no-store"
        token = parse_bearer(authorization)
        sessions = request.app.state.capability_registry.resolve(SESSIONS_VALIDATE)
        session_id = OpaqueId(payload.session_id)
        session = await sessions.validate_session(session_id=session_id, session_token=token)
        patient_id = None if payload.patient_id is None else OpaqueId(payload.patient_id)
        context = get_actor_context(request)
        created_by = None
        if patient_id is not None:
            policy = request.app.state.capability_registry.resolve(IDENTITY_AUTHORIZE)
            policy.require_self_subject(context, ENCOUNTER_WRITE_SELF, patient_id)
            if context.actor_id is None:
                raise ApplicationError(
                    code=ErrorCode.AUTHORIZATION_DENIED,
                    message="The authenticated actor has no trusted actor identifier.",
                )
            created_by = context.actor_id
        return encounter_view(
            await creator.create_encounter(
                session=session,
                patient_id=patient_id,
                encounter_type=payload.encounter_type,
                created_by=created_by,
            )
        )

    @router.get("/{encounter_id}", response_model=EncounterResponse)
    async def get_encounter(
        encounter_id: UUID,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> EncounterResponse:
        response.headers["Cache-Control"] = "no-store"
        encounter = await reader.get_encounter(OpaqueId(encounter_id))
        await _authorize_existing(
            request,
            encounter,
            permission=ENCOUNTER_READ_SELF,
            authorization_header=authorization,
        )
        return encounter_view(encounter)

    async def transition(
        encounter_id: UUID,
        target: EncounterStatus,
        request: Request,
        authorization: str | None,
    ) -> EncounterResponse:
        encounter = await reader.get_encounter(OpaqueId(encounter_id))
        await _authorize_existing(
            request,
            encounter,
            permission=ENCOUNTER_WRITE_SELF,
            authorization_header=authorization,
        )
        return encounter_view(
            await transitions.transition_encounter(
                encounter_id=encounter.encounter_id, target=target
            )
        )

    @router.post("/{encounter_id}/complete", response_model=EncounterResponse)
    async def complete_encounter(
        encounter_id: UUID,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> EncounterResponse:
        response.headers["Cache-Control"] = "no-store"
        return await transition(encounter_id, EncounterStatus.COMPLETED, request, authorization)

    @router.post("/{encounter_id}/abandon", response_model=EncounterResponse)
    async def abandon_encounter(
        encounter_id: UUID,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> EncounterResponse:
        response.headers["Cache-Control"] = "no-store"
        return await transition(encounter_id, EncounterStatus.ABANDONED, request, authorization)

    return router
