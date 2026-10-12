"""Public encounter application and persistence contracts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.encounters.domain import Encounter, EncounterStatus, EncounterType
from app.modules.patients.contracts import ReadPatientCapability
from app.modules.sessions.domain import Session
from app.shared.types import OpaqueId


class StaleEncounterWriteError(RuntimeError):
    """Raised when an encounter save does not match its expected version."""


@dataclass(frozen=True, slots=True)
class EncounterCursor:
    started_at: datetime
    encounter_id: OpaqueId


@dataclass(frozen=True, slots=True)
class EncounterPage:
    items: tuple[Encounter, ...]
    has_more: bool


class CreateEncounterCapability(Protocol):
    async def create_encounter(
        self,
        *,
        session: Session,
        patient_id: OpaqueId | None,
        encounter_type: EncounterType,
        created_by: OpaqueId | None,
    ) -> Encounter: ...


class ReadEncounterCapability(Protocol):
    async def get_encounter(self, encounter_id: OpaqueId) -> Encounter: ...


class ListEncountersCapability(Protocol):
    async def list_for_patient(
        self,
        *,
        patient_id: OpaqueId,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        cursor: EncounterCursor | None = None,
        limit: int = 50,
    ) -> EncounterPage: ...


class TransitionEncounterCapability(Protocol):
    async def transition_encounter(
        self, *, encounter_id: OpaqueId, target: EncounterStatus
    ) -> Encounter: ...


class EncounterRepository(Protocol):
    async def add(self, session: AsyncSession, encounter: Encounter) -> object: ...
    async def get(self, session: AsyncSession, encounter_id: OpaqueId) -> Encounter | None: ...
    async def get_with_version(
        self, session: AsyncSession, encounter_id: OpaqueId
    ) -> tuple[Encounter, int] | None: ...
    async def save(
        self,
        session: AsyncSession,
        encounter: Encounter,
        *,
        expected_version: int,
        updated_at: datetime,
    ) -> int: ...
    async def list_for_patient(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        from_time: datetime | None,
        to_time: datetime | None,
        cursor: EncounterCursor | None,
        limit: int,
    ) -> tuple[Encounter, ...]: ...


type PatientReader = ReadPatientCapability
