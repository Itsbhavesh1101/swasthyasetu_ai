"""Post-commit isolation evidence for the synthetic ABDM test boundary."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta

import pytest
from abdm_support.mock_adapter import (
    DeterministicMockABDMAdapter,
    MockABDMError,
    MockABDMScenario,
)
from sqlalchemy import text

from app.config import DatabaseSettings, Environment
from app.modules.clinical_intake.contracts import (
    AnswerType,
    IntakeAnswer,
    IntakeAnswerSourceType,
    ResponseDisposition,
)
from app.modules.clinical_intake.domain import ClinicalIntake, ClinicalIntakeStatus
from app.modules.clinical_intake.infrastructure import (
    PostgresClinicalIntakeRepository,
    PostgresIntakeAnswerRepository,
)
from app.modules.encounters.infrastructure import EncounterRecord
from app.modules.interoperability.abdm.contracts import (
    ABDMIntegrationMode,
    SyntheticABDMArtifactReference,
    SyntheticABDMOperation,
    SyntheticABDMRequest,
    SyntheticABDMResultState,
    synthetic_abdm_request_fingerprint,
)
from app.modules.sessions.infrastructure import SessionRecord
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 10, 31, 8, tzinfo=UTC)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    truncate = text(
        "TRUNCATE TABLE intake_answers, questionnaire_instances, clinical_intakes, "
        "observations, allergies, medications, clinical_fact_provenance, clinical_facts, "
        "encounters, patient_identifiers, patient_demographics, patients, consent_records, "
        "sessions, actor_roles, actors, outbox_events CASCADE"
    )
    async with runtime.engine.begin() as connection:
        await connection.execute(truncate)
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(truncate)
        await runtime.dispose()


async def _encounter(runtime: DatabaseRuntime) -> OpaqueId:
    session_id = OpaqueId.new()
    encounter_id = OpaqueId.new()
    async with runtime.transaction() as session:
        session.add(
            SessionRecord(
                id=session_id.value,
                session_type="PSEUDONYMOUS",
                actor_id=None,
                patient_id=None,
                language_preference="en",
                status="ACTIVE",
                token_hash=session_id.value.hex,
                recovery_token_hash=None,
                created_at=NOW,
                expires_at=NOW + timedelta(hours=1),
                closed_at=None,
                updated_at=NOW,
            )
        )
        await session.flush()
        session.add(
            EncounterRecord(
                id=encounter_id.value,
                patient_id=None,
                session_id=session_id.value,
                encounter_type="GENERAL_INTAKE",
                status="IN_PROGRESS",
                institution_id=None,
                language_context=None,
                started_at=NOW,
                completed_at=None,
                created_by=None,
                created_at=NOW,
                updated_at=NOW,
                version=1,
            )
        )
    return encounter_id


async def _persist_local_state(
    runtime: DatabaseRuntime,
) -> tuple[ClinicalIntake, IntakeAnswer]:
    intake = ClinicalIntake(
        intake_id=OpaqueId.new(),
        encounter_id=await _encounter(runtime),
        status=ClinicalIntakeStatus.IN_PROGRESS,
        started_at=NOW,
        version=1,
    )
    answer = IntakeAnswer(
        answer_id=OpaqueId.new(),
        intake_id=intake.intake_id,
        question_id="synthetic.optional",
        question_version="1.0.0",
        answer_type=AnswerType.TEXT,
        value=None,
        response_disposition=ResponseDisposition.SKIPPED,
        language_code="en",
        source_type=IntakeAnswerSourceType.PATIENT_TOUCH,
        answered_at=NOW,
        created_at=NOW,
    )
    async with runtime.transaction() as session:
        await PostgresClinicalIntakeRepository().add(session, intake)
        await PostgresIntakeAnswerRepository().add(session, answer)
    return intake, answer


def _request() -> SyntheticABDMRequest:
    return SyntheticABDMRequest(
        request_id="syn_abdm_request_alpha",
        mode=ABDMIntegrationMode.SYNTHETIC_OFFLINE_MOCK,
        operation=SyntheticABDMOperation.ALPHA,
        artifact=SyntheticABDMArtifactReference(
            artifact_id="syn_abdm_artifact_alpha",
            artifact_version="engineering.v1",
            content_hash="a" * 64,
        ),
        idempotency_key="b" * 64,
        created_at=NOW + timedelta(minutes=1),
    )


def _adapter(
    request: SyntheticABDMRequest,
    scenario: MockABDMScenario,
    *,
    clock: Callable[[], datetime] = lambda: NOW + timedelta(minutes=2),
) -> DeterministicMockABDMAdapter:
    return DeterministicMockABDMAdapter(
        fixtures={synthetic_abdm_request_fingerprint(request): scenario},
        environment=Environment.TEST,
        clock=clock,
    )


async def _assert_preserved_then_complete(
    runtime: DatabaseRuntime,
    intake: ClinicalIntake,
    answer: IntakeAnswer,
) -> None:
    intake_repository = PostgresClinicalIntakeRepository()
    answer_repository = PostgresIntakeAnswerRepository()
    async with runtime.session_factory() as session:
        assert await intake_repository.get(session, intake.intake_id) == intake
        assert await answer_repository.list_for_intake(session, intake.intake_id) == (answer,)

    completed_at = NOW + timedelta(minutes=3)
    completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=completed_at)
    async with runtime.transaction() as session:
        saved = await intake_repository.save(
            session,
            completed,
            expected_version=1,
            updated_at=completed_at,
        )

    async with runtime.session_factory() as session:
        assert await intake_repository.get(session, intake.intake_id) == saved
        assert saved.status is ClinicalIntakeStatus.COMPLETED
        assert saved.version == 2
        assert await answer_repository.list_for_intake(session, intake.intake_id) == (answer,)


@pytest.mark.parametrize(
    ("scenario", "expected_state"),
    [
        (MockABDMScenario.REJECTED, SyntheticABDMResultState.SYNTHETIC_REJECTED),
        (MockABDMScenario.UNAVAILABLE, SyntheticABDMResultState.SYNTHETIC_UNAVAILABLE),
    ],
)
async def test_committed_intake_survives_synthetic_abdm_failure_result(
    database_runtime: DatabaseRuntime,
    scenario: MockABDMScenario,
    expected_state: SyntheticABDMResultState,
) -> None:
    intake, answer = await _persist_local_state(database_runtime)
    request = _request()

    result = _adapter(request, scenario).execute(request)

    assert result.state is expected_state
    await _assert_preserved_then_complete(database_runtime, intake, answer)


async def test_committed_intake_survives_synthetic_abdm_adapter_exception(
    database_runtime: DatabaseRuntime,
) -> None:
    intake, answer = await _persist_local_state(database_runtime)
    request = _request()

    def failing_clock() -> datetime:
        raise RuntimeError("private-canary")

    with pytest.raises(MockABDMError) as error:
        _adapter(request, MockABDMScenario.ACCEPTED, clock=failing_clock).execute(request)

    assert "private-canary" not in str(error.value)
    await _assert_preserved_then_complete(database_runtime, intake, answer)
