"""Versioned HTTP transport for the sessions module."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.security.bearer import parse_bearer
from app.modules.sessions.contracts import (
    CloseSessionCapability,
    CreateSessionCapability,
    ReadSessionCapability,
)
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.types import OpaqueId


class CreatableSessionType(StrEnum):
    """Session modes activated in P4-A."""

    PSEUDONYMOUS = "PSEUDONYMOUS"
    KIOSK = "KIOSK"


class CreateSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_type: CreatableSessionType
    language_preference: str | None = Field(default=None, min_length=2, max_length=35)

    @field_validator("language_preference")
    @classmethod
    def normalize_language_preference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized or not all(
            part.isalnum() and 2 <= len(part) <= 8 for part in normalized.split("-")
        ):
            raise ValueError("language preference must be a bounded language tag")
        return normalized


class CreateSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID
    session_token: str
    session_type: SessionType
    status: SessionStatus
    expires_at: datetime


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID
    session_type: SessionType
    status: SessionStatus
    language_preference: str | None
    created_at: datetime
    expires_at: datetime
    closed_at: datetime | None


def _view(session: Session) -> SessionResponse:
    return SessionResponse(
        session_id=session.session_id.value,
        session_type=session.session_type,
        status=session.status,
        language_preference=session.language_preference,
        created_at=session.created_at,
        expires_at=session.expires_at,
        closed_at=session.closed_at,
    )


def build_sessions_router(
    *,
    creator: CreateSessionCapability,
    reader: ReadSessionCapability,
    closer: CloseSessionCapability,
) -> APIRouter:
    """Build thin routes around explicitly supplied capabilities."""
    router = APIRouter(prefix="/sessions", tags=["sessions"])

    @router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_session(
        payload: CreateSessionRequest, response: Response
    ) -> CreateSessionResponse:
        response.headers["Cache-Control"] = "no-store"
        result = await creator.create_session(
            session_type=SessionType(payload.session_type.value),
            language_preference=payload.language_preference,
        )
        return CreateSessionResponse(
            session_id=result.session.session_id.value,
            session_token=result.session_token,
            session_type=result.session.session_type,
            status=result.session.status,
            expires_at=result.session.expires_at,
        )

    @router.get("/{session_id}", response_model=SessionResponse)
    async def get_session(
        session_id: UUID,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> SessionResponse:
        response.headers["Cache-Control"] = "no-store"
        session = await reader.get_session(
            session_id=OpaqueId(session_id), session_token=parse_bearer(authorization)
        )
        return _view(session)

    @router.post("/{session_id}/close", response_model=SessionResponse)
    async def close_session(
        session_id: UUID,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> SessionResponse:
        response.headers["Cache-Control"] = "no-store"
        session = await closer.close_session(
            session_id=OpaqueId(session_id), session_token=parse_bearer(authorization)
        )
        return _view(session)

    return router
