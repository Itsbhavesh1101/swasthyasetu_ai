"""Trusted patient bearer authentication for FastAPI routes."""

from dataclasses import replace
from typing import Annotated, Protocol

from fastapi import Header, Request

from app.api.security.bearer import parse_bearer
from app.shared.security import ActorContext


class PatientAuthenticator(Protocol):
    async def authenticate(self, token: str) -> ActorContext: ...


async def authenticate_patient(
    request: Request,
    authorization: Annotated[str | None, Header()],
    *,
    authenticator: PatientAuthenticator,
) -> ActorContext:
    """Authenticate an exact bearer and install only its trusted actor context."""
    context = await authenticator.authenticate(parse_bearer(authorization))
    trusted = replace(context, request_id=getattr(request.state, "request_id", None))
    request.state.actor_context = trusted
    return trusted


__all__ = ["PatientAuthenticator", "authenticate_patient"]
