"""Explicit sessions composition boundary and public capability keys."""

from collections.abc import Callable
from datetime import datetime

from fastapi import APIRouter

from app.config import SessionsSettings
from app.modules.sessions.api import build_sessions_router
from app.modules.sessions.application import SessionService, TokenFactory
from app.modules.sessions.contracts import (
    CloseSessionCapability,
    CreateSessionCapability,
    ReadSessionCapability,
    ValidateSessionCapability,
)
from app.modules.sessions.infrastructure import PostgresSessionRepository
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now

SESSIONS_CREATE = CapabilityKey[CreateSessionCapability](CapabilityIdentifier("sessions.create"))
SESSIONS_READ = CapabilityKey[ReadSessionCapability](CapabilityIdentifier("sessions.read"))
SESSIONS_CLOSE = CapabilityKey[CloseSessionCapability](CapabilityIdentifier("sessions.close"))
SESSIONS_VALIDATE = CapabilityKey[ValidateSessionCapability](
    CapabilityIdentifier("sessions.validate")
)

SESSIONS_MANIFEST = ModuleManifest(
    module_id=ModuleId("sessions"),
    version=1,
    provided_capabilities=frozenset(
        {
            SESSIONS_CREATE.identifier,
            SESSIONS_READ.identifier,
            SESSIONS_CLOSE.identifier,
            SESSIONS_VALIDATE.identifier,
        }
    ),
    api_prefixes=("/sessions",),
    configuration_keys=("sessions",),
    data_ownership=("sessions",),
)


def build_sessions_registration(
    *,
    settings: SessionsSettings,
    database: DatabaseRuntime | None,
    clock: Callable[[], datetime] = utc_now,
    token_factory: TokenFactory | None = None,
) -> ModuleRegistration[APIRouter]:
    """Build one explicit, per-application sessions registration."""
    repository = PostgresSessionRepository()
    if token_factory is None:
        service = SessionService(
            database=database,
            settings=settings,
            repository=repository,
            clock=clock,
        )
    else:
        service = SessionService(
            database=database,
            settings=settings,
            repository=repository,
            clock=clock,
            token_factory=token_factory,
        )
    router = build_sessions_router(creator=service, reader=service, closer=service)
    return ModuleRegistration(
        manifest=SESSIONS_MANIFEST,
        routers=(router,),
        capability_bindings=(
            SESSIONS_CREATE.bind(service),
            SESSIONS_READ.bind(service),
            SESSIONS_CLOSE.bind(service),
            SESSIONS_VALIDATE.bind(service),
        ),
    )


__all__ = [
    "SESSIONS_CLOSE",
    "SESSIONS_CREATE",
    "SESSIONS_MANIFEST",
    "SESSIONS_READ",
    "SESSIONS_VALIDATE",
    "CloseSessionCapability",
    "CreateSessionCapability",
    "ReadSessionCapability",
    "ValidateSessionCapability",
    "build_sessions_registration",
]
