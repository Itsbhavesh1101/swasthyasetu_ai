"""Trusted authenticated-session encounter bindings."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.encounters.application import EncounterService
from app.modules.encounters.domain import Encounter, EncounterType
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


class Database:
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        yield cast(AsyncSession, object())


class Patients:
    def __init__(self) -> None:
        self.reads: list[OpaqueId] = []

    async def get_patient(self, patient_id: OpaqueId) -> object:
        self.reads.append(patient_id)
        return object()


class Encounters:
    def __init__(self) -> None:
        self.by_session: dict[OpaqueId, Encounter] = {}

    async def acquire_session_start_lock(self, session: AsyncSession, session_id: OpaqueId) -> None:
        return None

    async def get_resumable_for_session(
        self, session: AsyncSession, session_id: OpaqueId
    ) -> Encounter | None:
        return self.by_session.get(session_id)

    async def add(self, session: AsyncSession, encounter: Encounter) -> object:
        self.by_session[encounter.session_id] = encounter
        return encounter


def session(kind: SessionType) -> Session:
    authenticated = kind is SessionType.AUTHENTICATED
    return Session(
        session_id=OpaqueId.new(),
        session_type=kind,
        language_preference="en",
        status=SessionStatus.ACTIVE,
        created_at=NOW,
        expires_at=NOW + timedelta(hours=1),
        closed_at=None,
        updated_at=NOW,
        actor_id=OpaqueId.new() if authenticated else None,
        patient_id=OpaqueId.new() if authenticated else None,
    )


def service(repository: Encounters, patients: Patients) -> EncounterService:
    return EncounterService(
        database=cast(DatabaseRuntime, Database()),
        repository=repository,  # type: ignore[arg-type]
        patients=patients,  # type: ignore[arg-type]
        clock=lambda: NOW,
    )


async def test_authenticated_general_intake_uses_only_session_bindings_and_resumes() -> None:
    current = session(SessionType.AUTHENTICATED)
    repository = Encounters()
    patients = Patients()
    encounters = service(repository, patients)

    created = await encounters.find_or_create_general_intake(session=current)
    resumed = await encounters.find_or_create_general_intake(session=current)

    assert resumed == created
    assert created.patient_id == current.patient_id
    assert created.created_by == current.actor_id
    assert patients.reads == [current.patient_id, current.patient_id]


async def test_payload_cannot_substitute_another_patient_or_actor() -> None:
    current = session(SessionType.AUTHENTICATED)
    encounters = service(Encounters(), Patients())

    with pytest.raises(ApplicationError) as captured:
        await encounters.create_encounter(
            session=current,
            patient_id=OpaqueId.new(),
            encounter_type=EncounterType.GENERAL_INTAKE,
            created_by=current.actor_id,
        )
    assert captured.value.code is ErrorCode.AUTHORIZATION_DENIED


async def test_pseudonymous_general_intake_remains_unlinked() -> None:
    created = await service(Encounters(), Patients()).find_or_create_general_intake(
        session=session(SessionType.PSEUDONYMOUS)
    )
    assert created.patient_id is None
    assert created.created_by is None


def test_authenticated_session_requires_both_identity_bindings() -> None:
    with pytest.raises(ValueError, match="actor and patient"):
        Session(
            session_id=OpaqueId.new(),
            session_type=SessionType.AUTHENTICATED,
            language_preference="en",
            status=SessionStatus.ACTIVE,
            created_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            closed_at=None,
            updated_at=NOW,
        )
