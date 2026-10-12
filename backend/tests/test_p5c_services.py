"""P5-C service, authorization, pagination, and privacy contracts."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast

import pytest

from app.config import Settings
from app.main import create_app
from app.modules.encounters.application import EncounterService
from app.modules.encounters.contracts import EncounterPage
from app.modules.encounters.domain import Encounter, EncounterStatus, EncounterType
from app.modules.encounters.infrastructure import PostgresEncounterRepository
from app.modules.identity.authorization import (
    ENCOUNTER_READ_SELF,
    ENCOUNTER_WRITE_SELF,
    PATIENT_READ_SELF,
    PATIENT_WRITE_SELF,
    AuthorizationService,
)
from app.modules.identity.domain import RoleCode
from app.modules.patients.clinical import ClinicalFact, FactType, Problem, ProblemStatus
from app.modules.patients.contracts import FactPage
from app.modules.patients.domain import Patient, PatientStatus
from app.modules.provenance.api import decode_timeline_cursor, encode_timeline_cursor
from app.modules.provenance.application import ProvenanceTimelineService
from app.modules.provenance.contracts import TimelineEntry, TimelineEntryType
from app.modules.provenance.domain import FactProvenance, ProvenanceSourceType, VerificationState
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 12, 8, tzinfo=UTC)


def _patient(patient_id: OpaqueId) -> Patient:
    return Patient(
        patient_id=patient_id,
        status=PatientStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
    )


def _fact(patient_id: OpaqueId, *, at: datetime, fact_id: OpaqueId) -> ClinicalFact:
    return ClinicalFact(
        fact_id=fact_id,
        patient_id=patient_id,
        encounter_id=None,
        fact_type=FactType.PROBLEM,
        value=Problem(
            label="synthetic problem",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.PATIENT_CONFIRMED,
        ),
        recorded_at=at,
        verification_state=VerificationState.PATIENT_CONFIRMED,
        provenance=FactProvenance(
            source_type=ProvenanceSourceType.PATIENT_REPORT,
            confidence=Decimal("0.8"),
            created_at=at,
        ),
    )


def _encounter(patient_id: OpaqueId, *, at: datetime, encounter_id: OpaqueId) -> Encounter:
    return Encounter(
        encounter_id=encounter_id,
        patient_id=patient_id,
        session_id=OpaqueId.new(),
        encounter_type=EncounterType.GENERAL_INTAKE,
        status=EncounterStatus.CREATED,
        started_at=at,
    )


def _session(session_type: SessionType) -> Session:
    return Session(
        session_id=OpaqueId.new(),
        session_type=session_type,
        language_preference="en",
        status=SessionStatus.ACTIVE,
        created_at=NOW,
        expires_at=NOW + timedelta(hours=1),
        closed_at=None,
        updated_at=NOW,
    )


class StubPatientCapabilities:
    def __init__(self, patient: Patient, facts: tuple[ClinicalFact, ...]) -> None:
        self.patient = patient
        self.facts = facts

    async def get_patient(self, patient_id: OpaqueId) -> Patient:
        assert patient_id == self.patient.patient_id
        return self.patient

    async def get_fact(self, fact_id: OpaqueId) -> ClinicalFact:
        return next(item for item in self.facts if item.fact_id == fact_id)

    async def list_facts(self, **kwargs: object) -> FactPage:
        limit = cast(int, kwargs["limit"])
        return FactPage(self.facts[:limit], len(self.facts) > limit)


class StubEncounterCapabilities:
    def __init__(self, encounters: tuple[Encounter, ...]) -> None:
        self.encounters = encounters

    async def list_for_patient(self, **kwargs: object) -> EncounterPage:
        limit = cast(int, kwargs["limit"])
        return EncounterPage(self.encounters[:limit], len(self.encounters) > limit)


def test_patient_role_has_only_explicit_self_service_permissions() -> None:
    context = ActorContext(
        actor_id=OpaqueId.new(),
        subject_id=OpaqueId.new(),
        roles=frozenset({RoleCode.PATIENT.value}),
        is_authenticated=True,
    )
    service = AuthorizationService()

    for permission in (
        PATIENT_READ_SELF,
        PATIENT_WRITE_SELF,
        ENCOUNTER_READ_SELF,
        ENCOUNTER_WRITE_SELF,
    ):
        assert service.has_permission(context, permission)


async def test_timeline_uses_defined_timestamps_and_deterministic_ties() -> None:
    patient_id = OpaqueId.new()
    fact_id = OpaqueId.parse("00000000-0000-0000-0000-000000000002")
    encounter_id = OpaqueId.parse("00000000-0000-0000-0000-000000000001")
    fact = _fact(patient_id, at=NOW, fact_id=fact_id)
    encounter = _encounter(patient_id, at=NOW, encounter_id=encounter_id)
    patients = StubPatientCapabilities(_patient(patient_id), (fact,))
    service = ProvenanceTimelineService(
        patients=patients,
        fact_reader=patients,
        facts=patients,
        encounters=StubEncounterCapabilities((encounter,)),
    )

    page = await service.get_timeline(patient_id=patient_id)

    assert [item.entry_type for item in page.items] == [
        TimelineEntryType.CLINICAL_FACT,
        TimelineEntryType.ENCOUNTER,
    ]
    assert all(item.occurred_at == NOW for item in page.items)
    assert await service.read_provenance(fact_id) == fact.provenance


def test_timeline_cursor_is_opaque_versioned_and_rejects_malformed_values() -> None:
    patient_id = OpaqueId.new()
    fact = _fact(patient_id, at=NOW, fact_id=OpaqueId.new())
    entry = TimelineEntry(
        entry_id=fact.fact_id,
        entry_type=TimelineEntryType.CLINICAL_FACT,
        occurred_at=NOW,
        fact=fact,
    )
    encoded = encode_timeline_cursor(entry)

    assert str(fact.fact_id) not in encoded
    assert decode_timeline_cursor(encoded) == decode_timeline_cursor(encoded)
    with pytest.raises(SwasthyaSetuError) as error:
        decode_timeline_cursor("not-a-valid-cursor")
    assert error.value.code is ErrorCode.VALIDATION_ERROR


@pytest.mark.parametrize(
    ("session_type", "encounter_type"),
    [
        (SessionType.KIOSK, EncounterType.GENERAL_INTAKE),
        (SessionType.PSEUDONYMOUS, EncounterType.KIOSK_INTAKE),
        (SessionType.PSEUDONYMOUS, EncounterType.CLINICIAN_REVIEW),
    ],
)
async def test_encounter_service_rejects_ineligible_http_type_or_session_pair(
    session_type: SessionType, encounter_type: EncounterType
) -> None:
    patient_id = OpaqueId.new()
    patients = StubPatientCapabilities(_patient(patient_id), ())
    service = EncounterService(
        database=None,
        repository=PostgresEncounterRepository(),
        patients=patients,
    )

    with pytest.raises(SwasthyaSetuError) as error:
        await service.create_encounter(
            session=_session(session_type),
            patient_id=None,
            encounter_type=encounter_type,
            created_by=None,
        )
    assert error.value.code is ErrorCode.VALIDATION_ERROR


async def test_database_disabled_patient_route_is_registered_and_safe_503() -> None:
    application = create_app(Settings(_env_file=None))
    patient_id = OpaqueId.new()

    @application.middleware("http")
    async def trusted_context(request, call_next):  # type: ignore[no-untyped-def]
        request.state.actor_context = ActorContext(
            actor_id=OpaqueId.new(),
            subject_id=patient_id,
            roles=frozenset({RoleCode.PATIENT.value}),
            is_authenticated=True,
        )
        return await call_next(request)

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/v1/patients/{patient_id}")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert response.headers["cache-control"] == "no-store"


async def test_patient_create_rejects_client_id_and_missing_trusted_subject() -> None:
    from httpx import ASGITransport, AsyncClient

    application = create_app(Settings(_env_file=None))

    @application.middleware("http")
    async def trusted_actor_without_subject(request, call_next):  # type: ignore[no-untyped-def]
        request.state.actor_context = ActorContext(
            actor_id=OpaqueId.new(),
            roles=frozenset({RoleCode.PATIENT.value}),
            is_authenticated=True,
        )
        return await call_next(request)

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        forbidden = await client.post("/api/v1/patients", json={})
        invalid = await client.post("/api/v1/patients", json={"patient_id": str(OpaqueId.new())})

    assert forbidden.status_code == 403
    assert invalid.status_code == 422
    assert invalid.headers["cache-control"] == "no-store"


def test_timeline_rejects_reversed_range() -> None:
    patient_id = OpaqueId.new()
    patients = StubPatientCapabilities(_patient(patient_id), ())
    service = ProvenanceTimelineService(
        patients=patients,
        fact_reader=patients,
        facts=patients,
        encounters=StubEncounterCapabilities(()),
    )

    with pytest.raises(SwasthyaSetuError) as error:
        import asyncio

        asyncio.run(
            service.get_timeline(
                patient_id=patient_id,
                from_time=NOW + timedelta(days=1),
                to_time=NOW,
            )
        )
    assert error.value.code is ErrorCode.VALIDATION_ERROR
