"""Real PostgreSQL verification for the P7-A intake foundation."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import IntegrityError

from app.config import DatabaseSettings
from app.modules.clinical_intake.contracts import (
    AnswerReference,
    AnswerType,
    ClinicalIntakeAlreadyExistsError,
    ClinicalIntakeIdentityError,
    IntakeAnswer,
    IntakeAnswerSourceType,
    QuestionnaireInstance,
    QuestionnaireInstanceIdentityError,
    QuestionnaireResponses,
    QuestionnaireStatus,
    ResponseDisposition,
    StaleClinicalIntakeWriteError,
)
from app.modules.clinical_intake.domain import (
    ChiefComplaint,
    ClinicalIntake,
    ClinicalIntakeStatus,
    DurationValue,
    HistoryOfPresentIllness,
    InvalidClinicalIntakeTransitionError,
)
from app.modules.clinical_intake.infrastructure import (
    ClinicalIntakeRecord,
    IntakeAnswerRecord,
    PostgresClinicalIntakeRepository,
    PostgresIntakeAnswerRepository,
    PostgresQuestionnaireInstanceRepository,
    QuestionnaireInstanceRecord,
)
from app.modules.encounters.infrastructure import EncounterRecord
from app.modules.sessions.infrastructure import SessionRecord
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 10, 17, 8, tzinfo=UTC)


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


def _intake(encounter_id: OpaqueId) -> ClinicalIntake:
    answer_id = OpaqueId.new()
    return ClinicalIntake(
        intake_id=OpaqueId.new(),
        encounter_id=encounter_id,
        status=ClinicalIntakeStatus.IN_PROGRESS,
        chief_complaint=ChiefComplaint(
            patient_wording="Synthetic concern",
            display_key="chief.synthetic",
            source_answer_id=answer_id,
        ),
        hpi=HistoryOfPresentIllness(duration=DurationValue(Decimal("2.5"), "day", answer_id)),
        started_at=NOW,
        version=1,
    )


def _answer(
    intake_id: OpaqueId, *, at: datetime, answer_id: OpaqueId | None = None
) -> IntakeAnswer:
    return IntakeAnswer(
        answer_id=answer_id or OpaqueId.new(),
        intake_id=intake_id,
        question_id="synthetic.duration",
        question_version="1.0.0",
        answer_type=AnswerType.DURATION,
        value=Decimal("2.5"),
        unit="day",
        response_disposition=ResponseDisposition.ANSWERED,
        language_code="en",
        source_type=IntakeAnswerSourceType.PATIENT_TOUCH,
        answered_at=at,
        created_at=at,
    )


def _questionnaire(encounter_id: OpaqueId, answer_id: OpaqueId) -> QuestionnaireInstance:
    return QuestionnaireInstance(
        instance_id=OpaqueId.new(),
        encounter_id=encounter_id,
        questionnaire_id="synthetic.core",
        questionnaire_version="1.0.0",
        status=QuestionnaireStatus.ACTIVE,
        responses=QuestionnaireResponses(
            pack_id="synthetic.core",
            pack_version="1.0.0",
            answer_refs=(AnswerReference("synthetic.duration", "1.0.0", answer_id),),
            skipped_question_refs=(),
            last_selected_question_id="synthetic.duration",
            engine_version="structural-only.v1",
        ),
        started_at=NOW,
    )


async def test_intake_answer_and_questionnaire_round_trip(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    answer = _answer(intake.intake_id, at=NOW)
    questionnaire = _questionnaire(encounter_id, answer.answer_id)
    async with database_runtime.transaction() as session:
        await PostgresClinicalIntakeRepository().add(session, intake)
        await PostgresIntakeAnswerRepository().add(session, answer)
        await PostgresQuestionnaireInstanceRepository().add(session, questionnaire)
    async with database_runtime.session_factory() as session:
        assert await PostgresClinicalIntakeRepository().get(session, intake.intake_id) == intake
        assert await PostgresIntakeAnswerRepository().list_for_intake(
            session, intake.intake_id
        ) == (answer,)
        assert (
            await PostgresQuestionnaireInstanceRepository().get(session, questionnaire.instance_id)
            == questionnaire
        )


async def test_encounter_uniqueness_is_translated_and_missing_fk_is_rejected(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    repository = PostgresClinicalIntakeRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, _intake(encounter_id))
    with pytest.raises(ClinicalIntakeAlreadyExistsError):
        async with database_runtime.transaction() as session:
            await repository.add(session, _intake(encounter_id))
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            await repository.add(session, _intake(OpaqueId.new()))


async def test_answers_are_append_only_and_deterministically_ordered(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    later_low_id = _answer(
        intake.intake_id,
        at=NOW + timedelta(minutes=1),
        answer_id=OpaqueId.parse("00000000-0000-4000-8000-000000000001"),
    )
    later_high_id = _answer(
        intake.intake_id,
        at=NOW + timedelta(minutes=1),
        answer_id=OpaqueId.parse("00000000-0000-4000-8000-000000000002"),
    )
    first = _answer(intake.intake_id, at=NOW)
    async with database_runtime.transaction() as session:
        await PostgresClinicalIntakeRepository().add(session, intake)
        repository = PostgresIntakeAnswerRepository()
        for answer in (later_high_id, first, later_low_id):
            await repository.add(session, answer)
    async with database_runtime.session_factory() as session:
        assert await PostgresIntakeAnswerRepository().list_for_intake(
            session, intake.intake_id
        ) == (first, later_low_id, later_high_id)


async def test_optimistic_save_increments_once_and_rejects_stale_write(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
    completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=NOW + timedelta(minutes=5))
    async with database_runtime.transaction() as session:
        saved = await repository.save(
            session,
            completed,
            expected_version=1,
            updated_at=NOW + timedelta(minutes=5),
        )
    assert saved.version == 2
    with pytest.raises(StaleClinicalIntakeWriteError):
        async with database_runtime.transaction() as session:
            await repository.save(
                session,
                completed,
                expected_version=1,
                updated_at=NOW + timedelta(minutes=6),
            )


@pytest.mark.parametrize(
    ("persisted_status", "requested_status"),
    [
        (ClinicalIntakeStatus.ABANDONED, ClinicalIntakeStatus.COMPLETED),
        (ClinicalIntakeStatus.ABANDONED, ClinicalIntakeStatus.IN_PROGRESS),
        (ClinicalIntakeStatus.COMPLETED, ClinicalIntakeStatus.IN_PROGRESS),
        (ClinicalIntakeStatus.COMPLETED, ClinicalIntakeStatus.ABANDONED),
    ],
)
async def test_save_rejects_transition_from_authoritative_terminal_status(
    database_runtime: DatabaseRuntime,
    persisted_status: ClinicalIntakeStatus,
    requested_status: ClinicalIntakeStatus,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    terminal = intake.transition_to(
        persisted_status,
        at=NOW + timedelta(minutes=5)
        if persisted_status is ClinicalIntakeStatus.COMPLETED
        else None,
    )
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
        persisted = await repository.save(
            session,
            terminal,
            expected_version=1,
            updated_at=NOW + timedelta(minutes=5),
        )

    requested = replace(
        persisted,
        status=requested_status,
        completed_at=(
            NOW + timedelta(minutes=10)
            if requested_status is ClinicalIntakeStatus.COMPLETED
            else None
        ),
    )
    with pytest.raises(InvalidClinicalIntakeTransitionError):
        async with database_runtime.transaction() as session:
            await repository.save(
                session,
                requested,
                expected_version=2,
                updated_at=NOW + timedelta(minutes=10),
            )

    async with database_runtime.session_factory() as session:
        assert await repository.get(session, intake.intake_id) == persisted


@pytest.mark.parametrize(
    "terminal_status",
    [ClinicalIntakeStatus.COMPLETED, ClinicalIntakeStatus.ABANDONED],
)
async def test_save_rejects_structured_mutation_while_reusing_terminal_status(
    database_runtime: DatabaseRuntime,
    terminal_status: ClinicalIntakeStatus,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    terminal = intake.transition_to(
        terminal_status,
        at=NOW + timedelta(minutes=5)
        if terminal_status is ClinicalIntakeStatus.COMPLETED
        else None,
    )
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
        persisted = await repository.save(
            session,
            terminal,
            expected_version=1,
            updated_at=NOW + timedelta(minutes=5),
        )

    assert persisted.chief_complaint is not None
    changed = replace(
        persisted,
        chief_complaint=replace(
            persisted.chief_complaint,
            display_key="chief.changed",
        ),
    )
    with pytest.raises(InvalidClinicalIntakeTransitionError):
        async with database_runtime.transaction() as session:
            await repository.save(
                session,
                changed,
                expected_version=2,
                updated_at=NOW + timedelta(minutes=10),
            )

    async with database_runtime.session_factory() as session:
        stored = await repository.get(session, intake.intake_id)
    assert stored == persisted
    assert stored is not None
    assert stored.status is terminal_status
    assert stored.chief_complaint == terminal.chief_complaint
    assert stored.completed_at == terminal.completed_at
    assert stored.version == 2


@pytest.mark.parametrize(
    "requested_status",
    [
        ClinicalIntakeStatus.IN_PROGRESS,
        ClinicalIntakeStatus.COMPLETED,
        ClinicalIntakeStatus.ABANDONED,
    ],
)
async def test_save_allows_canonical_mutation_from_in_progress_once(
    database_runtime: DatabaseRuntime,
    requested_status: ClinicalIntakeStatus,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    assert intake.chief_complaint is not None
    requested = (
        replace(
            intake,
            chief_complaint=replace(intake.chief_complaint, display_key="chief.edited"),
        )
        if requested_status is ClinicalIntakeStatus.IN_PROGRESS
        else intake.transition_to(
            requested_status,
            at=NOW + timedelta(minutes=5)
            if requested_status is ClinicalIntakeStatus.COMPLETED
            else None,
        )
    )
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
        saved = await repository.save(
            session,
            requested,
            expected_version=1,
            updated_at=NOW + timedelta(minutes=5),
        )

    assert saved.version == 2
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, intake.intake_id) == saved


async def test_invalid_save_timestamp_does_not_mutate_persisted_intake(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
    completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=NOW + timedelta(minutes=5))
    with pytest.raises(ValueError, match="timezone-aware"):
        async with database_runtime.transaction() as session:
            await repository.save(
                session,
                completed,
                expected_version=1,
                updated_at=datetime(2026, 10, 17, 8),
            )
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, intake.intake_id) == intake


async def test_caller_rollback_removes_all_three_writes(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    answer = _answer(intake.intake_id, at=NOW)
    questionnaire = _questionnaire(encounter_id, answer.answer_id)
    with pytest.raises(RuntimeError, match="synthetic rollback"):
        async with database_runtime.transaction() as session:
            await PostgresClinicalIntakeRepository().add(session, intake)
            await PostgresQuestionnaireInstanceRepository().add(session, questionnaire)
            await PostgresIntakeAnswerRepository().add(session, answer)
            raise RuntimeError("synthetic rollback")
    async with database_runtime.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ClinicalIntakeRecord)) == 0
        assert await session.scalar(select(func.count()).select_from(IntakeAnswerRecord)) == 0
        assert (
            await session.scalar(select(func.count()).select_from(QuestionnaireInstanceRecord)) == 0
        )


async def test_malformed_stored_json_fails_with_safe_error(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
        await session.execute(
            update(ClinicalIntakeRecord)
            .where(ClinicalIntakeRecord.id == intake.intake_id.value)
            .values(chief_complaint={"schema_version": "unsupported", "private": "do-not-echo"})
        )
    async with database_runtime.session_factory() as session:
        with pytest.raises(ValueError) as raised:
            await repository.get(session, intake.intake_id)
    assert str(raised.value) == "clinical intake persistence shape is invalid"
    assert "do-not-echo" not in str(raised.value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "INVALID"),
        ("status", "COMPLETED"),
        ("version", 0),
        ("chief_complaint", []),
        ("hpi", []),
        ("history_sections", []),
        ("missing_information", {}),
        ("contradictions", {}),
    ],
)
async def test_database_constraints_reject_invalid_intake_values(
    database_runtime: DatabaseRuntime, field: str, value: object
) -> None:
    encounter_id = await _encounter(database_runtime)
    values: dict[str, object] = {
        "id": OpaqueId.new().value,
        "encounter_id": encounter_id.value,
        "status": "IN_PROGRESS",
        "chief_complaint": None,
        "hpi": None,
        "history_sections": {"schema_version": "history-sections.v1"},
        "missing_information": [],
        "contradictions": [],
        "started_at": NOW,
        "completed_at": None,
        "created_at": NOW,
        "updated_at": NOW,
        "version": 1,
    }
    values[field] = value
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            session.add(ClinicalIntakeRecord(**values))
            await session.flush()


@pytest.mark.parametrize(
    ("source_type", "payload"),
    [("INVALID", {"schema_version": "intake-answer.v1"}), ("PATIENT_TEXT", [])],
)
async def test_database_constraints_reject_invalid_answer_values(
    database_runtime: DatabaseRuntime, source_type: str, payload: object
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    async with database_runtime.transaction() as session:
        await PostgresClinicalIntakeRepository().add(session, intake)
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            session.add(
                IntakeAnswerRecord(
                    id=OpaqueId.new().value,
                    intake_id=intake.intake_id.value,
                    question_id="synthetic.question",
                    question_version="1.0.0",
                    answer=payload,
                    source_type=source_type,
                    answered_at=NOW,
                    created_at=NOW,
                )
            )
            await session.flush()


@pytest.mark.parametrize(
    ("status", "responses", "completed_at"),
    [
        ("INVALID", {"schema_version": "questionnaire-responses.v1"}, None),
        ("ACTIVE", [], None),
        ("COMPLETED", {"schema_version": "questionnaire-responses.v1"}, None),
    ],
)
async def test_database_constraints_reject_invalid_questionnaire_values(
    database_runtime: DatabaseRuntime,
    status: str,
    responses: object,
    completed_at: datetime | None,
) -> None:
    encounter_id = await _encounter(database_runtime)
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            session.add(
                QuestionnaireInstanceRecord(
                    id=OpaqueId.new().value,
                    encounter_id=encounter_id.value,
                    questionnaire_id="synthetic.core",
                    questionnaire_version="1.0.0",
                    status=status,
                    responses=responses,
                    started_at=NOW,
                    completed_at=completed_at,
                )
            )
            await session.flush()


async def test_repository_never_commits_caller_session(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    async with database_runtime.session_factory() as session, session.begin():
        await PostgresClinicalIntakeRepository().add(session, intake)
        await session.rollback()
    async with database_runtime.session_factory() as session:
        assert await session.get(ClinicalIntakeRecord, intake.intake_id.value) is None


async def test_repository_rejects_creation_version_jump(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    with pytest.raises(ValueError, match="version must be 1"):
        async with database_runtime.transaction() as session:
            await PostgresClinicalIntakeRepository().add(
                session, replace(_intake(encounter_id), version=5)
            )
    async with database_runtime.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ClinicalIntakeRecord)) == 0


async def test_intake_save_rejects_immutable_encounter_identity_change(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    intake = _intake(encounter_id)
    repository = PostgresClinicalIntakeRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, intake)
    with pytest.raises(ClinicalIntakeIdentityError):
        async with database_runtime.transaction() as session:
            await repository.save(
                session,
                replace(intake, encounter_id=OpaqueId.new()),
                expected_version=1,
                updated_at=NOW + timedelta(minutes=1),
            )
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, intake.intake_id) == intake


async def test_questionnaire_save_rejects_immutable_identity_change(
    database_runtime: DatabaseRuntime,
) -> None:
    encounter_id = await _encounter(database_runtime)
    answer_id = OpaqueId.new()
    instance = _questionnaire(encounter_id, answer_id)
    repository = PostgresQuestionnaireInstanceRepository()
    async with database_runtime.transaction() as session:
        await repository.add(session, instance)
    with pytest.raises(QuestionnaireInstanceIdentityError):
        async with database_runtime.transaction() as session:
            changed_responses = replace(instance.responses, pack_id="synthetic.other")
            await repository.save(
                session,
                replace(
                    instance,
                    questionnaire_id="synthetic.other",
                    responses=changed_responses,
                ),
            )
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, instance.instance_id) == instance
