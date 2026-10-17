"""Stable public exports and explicit composition for encounters."""

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.modules.encounters.contracts import (
    CreateEncounterCapability,
    EncounterCursor,
    EncounterPage,
    FindOrCreateGeneralIntakeEncounterCapability,
    ListEncountersCapability,
    ReadEncounterCapability,
    TransitionEncounterCapability,
)
from app.modules.encounters.domain import (
    Encounter,
    EncounterId,
    EncounterStatus,
    EncounterType,
    InvalidEncounterTransitionError,
)
from app.modules.patients.public import PATIENTS_READ, ReadPatientCapability
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime

if TYPE_CHECKING:
    from app.modules.encounters.application import EncounterService

ENCOUNTERS_CREATE = CapabilityKey[CreateEncounterCapability](
    CapabilityIdentifier("encounters.create")
)
ENCOUNTERS_FIND_OR_CREATE_GENERAL_INTAKE = CapabilityKey[
    FindOrCreateGeneralIntakeEncounterCapability
](CapabilityIdentifier("encounters.find_or_create_general_intake"))
ENCOUNTERS_READ = CapabilityKey[ReadEncounterCapability](CapabilityIdentifier("encounters.read"))
ENCOUNTERS_LIST = CapabilityKey[ListEncountersCapability](CapabilityIdentifier("encounters.list"))
ENCOUNTERS_TRANSITION = CapabilityKey[TransitionEncounterCapability](
    CapabilityIdentifier("encounters.transition")
)

ENCOUNTERS_MANIFEST = ModuleManifest(
    module_id=ModuleId("encounters"),
    version=1,
    provided_capabilities=frozenset(
        key.identifier
        for key in (
            ENCOUNTERS_CREATE,
            ENCOUNTERS_FIND_OR_CREATE_GENERAL_INTAKE,
            ENCOUNTERS_READ,
            ENCOUNTERS_LIST,
            ENCOUNTERS_TRANSITION,
        )
    ),
    required_capabilities=frozenset({PATIENTS_READ.identifier}),
    api_prefixes=("/encounters",),
    required_permissions=("encounter:read:self", "encounter:write:self"),
    data_ownership=("encounters",),
)


def build_encounter_service(
    *,
    database: DatabaseRuntime | None,
    patients: ReadPatientCapability,
    clock: Callable[[], datetime] | None = None,
) -> "EncounterService":
    from app.modules.encounters.application import EncounterService
    from app.modules.encounters.infrastructure import PostgresEncounterRepository

    kwargs = {} if clock is None else {"clock": clock}
    return EncounterService(
        database=database, repository=PostgresEncounterRepository(), patients=patients, **kwargs
    )


def build_encounters_registration(*, service: "EncounterService") -> ModuleRegistration[APIRouter]:
    from app.modules.encounters.api import build_encounters_router

    return ModuleRegistration(
        manifest=ENCOUNTERS_MANIFEST,
        routers=(
            build_encounters_router(
                creator=service,
                general_intake=service,
                reader=service,
                transitions=service,
            ),
        ),
        capability_bindings=(
            ENCOUNTERS_CREATE.bind(service),
            ENCOUNTERS_FIND_OR_CREATE_GENERAL_INTAKE.bind(service),
            ENCOUNTERS_READ.bind(service),
            ENCOUNTERS_LIST.bind(service),
            ENCOUNTERS_TRANSITION.bind(service),
        ),
    )


__all__ = [
    "Encounter",
    "CreateEncounterCapability",
    "EncounterCursor",
    "EncounterId",
    "EncounterStatus",
    "EncounterType",
    "EncounterPage",
    "ListEncountersCapability",
    "ReadEncounterCapability",
    "TransitionEncounterCapability",
    "ENCOUNTERS_CREATE",
    "ENCOUNTERS_FIND_OR_CREATE_GENERAL_INTAKE",
    "ENCOUNTERS_LIST",
    "ENCOUNTERS_MANIFEST",
    "ENCOUNTERS_READ",
    "ENCOUNTERS_TRANSITION",
    "build_encounter_service",
    "build_encounters_registration",
    "InvalidEncounterTransitionError",
]
