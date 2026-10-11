"""Explicit consent module composition boundary and capability keys."""

from collections.abc import Callable
from datetime import datetime

from fastapi import APIRouter

from app.events import OutboxRepository
from app.modules.consent.api import build_consent_router
from app.modules.consent.application import ConsentService
from app.modules.consent.contracts import (
    CheckConsentCapability,
    GrantConsentCapability,
    ListConsentCapability,
    ReadConsentCapability,
    RevokeConsentCapability,
)
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now

CONSENT_GRANT = CapabilityKey[GrantConsentCapability](CapabilityIdentifier("consent.grant"))
CONSENT_READ = CapabilityKey[ReadConsentCapability](CapabilityIdentifier("consent.read"))
CONSENT_LIST = CapabilityKey[ListConsentCapability](CapabilityIdentifier("consent.list"))
CONSENT_REVOKE = CapabilityKey[RevokeConsentCapability](CapabilityIdentifier("consent.revoke"))
CONSENT_CHECK = CapabilityKey[CheckConsentCapability](CapabilityIdentifier("consent.check"))

CONSENT_MANIFEST = ModuleManifest(
    module_id=ModuleId("consent"),
    version=1,
    provided_capabilities=frozenset(
        {
            CONSENT_GRANT.identifier,
            CONSENT_READ.identifier,
            CONSENT_LIST.identifier,
            CONSENT_REVOKE.identifier,
            CONSENT_CHECK.identifier,
        }
    ),
    required_capabilities=frozenset({SESSIONS_VALIDATE.identifier}),
    api_prefixes=("/consents",),
    events_published=("ConsentGranted", "ConsentRevoked"),
    data_ownership=("consent_records",),
)


def build_consent_registration(
    *,
    database: DatabaseRuntime | None,
    clock: Callable[[], datetime] = utc_now,
) -> ModuleRegistration[APIRouter]:
    service = ConsentService(
        database=database,
        outbox=OutboxRepository(),
        clock=clock,
    )
    router = build_consent_router(
        grant=service,
        reader=service,
        listing=service,
        revoke=service,
    )
    return ModuleRegistration(
        manifest=CONSENT_MANIFEST,
        routers=(router,),
        capability_bindings=(
            CONSENT_GRANT.bind(service),
            CONSENT_READ.bind(service),
            CONSENT_LIST.bind(service),
            CONSENT_REVOKE.bind(service),
            CONSENT_CHECK.bind(service),
        ),
    )


__all__ = [
    "CONSENT_CHECK",
    "CONSENT_GRANT",
    "CONSENT_LIST",
    "CONSENT_MANIFEST",
    "CONSENT_READ",
    "CONSENT_REVOKE",
    "build_consent_registration",
]
