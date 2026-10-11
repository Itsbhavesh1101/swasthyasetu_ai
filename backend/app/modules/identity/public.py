"""Explicit identity composition boundary and typed capability keys."""

from collections.abc import Callable
from datetime import datetime

from fastapi import APIRouter

from app.modules.identity.application import IdentityService
from app.modules.identity.authorization import AuthorizationService
from app.modules.identity.contracts import (
    AuthenticateCapability,
    AuthenticationProvider,
    AuthorizeCapability,
    CurrentActorCapability,
)
from app.modules.identity.infrastructure import PostgresActorRepository
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now

IDENTITY_AUTHENTICATE = CapabilityKey[AuthenticateCapability](
    CapabilityIdentifier("identity.authenticate")
)
IDENTITY_CURRENT_ACTOR = CapabilityKey[CurrentActorCapability](
    CapabilityIdentifier("identity.current_actor")
)
IDENTITY_AUTHORIZE = CapabilityKey[AuthorizeCapability](CapabilityIdentifier("identity.authorize"))

IDENTITY_MANIFEST = ModuleManifest(
    module_id=ModuleId("identity"),
    version=1,
    provided_capabilities=frozenset(
        {
            IDENTITY_AUTHENTICATE.identifier,
            IDENTITY_CURRENT_ACTOR.identifier,
            IDENTITY_AUTHORIZE.identifier,
        }
    ),
    data_ownership=("actors", "actor_roles"),
)


def build_identity_registration(
    *,
    database: DatabaseRuntime | None,
    authentication_provider: AuthenticationProvider | None = None,
    clock: Callable[[], datetime] = utc_now,
    authorization: AuthorizationService | None = None,
) -> ModuleRegistration[APIRouter]:
    identity = IdentityService(
        database=database,
        authentication_provider=authentication_provider,
        repository=PostgresActorRepository(),
        clock=clock,
    )
    authorization_service = authorization or AuthorizationService()
    return ModuleRegistration(
        manifest=IDENTITY_MANIFEST,
        routers=(),
        capability_bindings=(
            IDENTITY_AUTHENTICATE.bind(identity),
            IDENTITY_CURRENT_ACTOR.bind(identity),
            IDENTITY_AUTHORIZE.bind(authorization_service),
        ),
    )


__all__ = [
    "IDENTITY_AUTHENTICATE",
    "IDENTITY_AUTHORIZE",
    "IDENTITY_CURRENT_ACTOR",
    "IDENTITY_MANIFEST",
    "build_identity_registration",
]
