"""P5-A encounter domain and lifecycle tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.encounters.public import (
    Encounter,
    EncounterStatus,
    EncounterType,
    InvalidEncounterTransitionError,
)
from app.shared.types import OpaqueId


def _encounter(status: EncounterStatus = EncounterStatus.CREATED) -> Encounter:
    completed_at = (
        datetime(2026, 10, 12, 9, tzinfo=UTC) if status is EncounterStatus.COMPLETED else None
    )
    return Encounter(
        encounter_id=OpaqueId.new(),
        patient_id=None,
        session_id=OpaqueId.new(),
        encounter_type=EncounterType.GENERAL_INTAKE,
        status=status,
        started_at=datetime(2026, 10, 12, 8, tzinfo=UTC),
        completed_at=completed_at,
        institution_id=None,
        language_context="hi-Latn",
        created_by=None,
    )


def test_encounter_enum_values_are_canonical() -> None:
    assert {value.value for value in EncounterType} == {
        "GENERAL_INTAKE",
        "MENTAL_HEALTH",
        "KIOSK_INTAKE",
        "CLINICIAN_REVIEW",
        "DOCUMENT_REVIEW",
        "RESEARCH_ONLY",
    }
    assert {value.value for value in EncounterStatus} == {
        "CREATED",
        "IN_PROGRESS",
        "AWAITING_REVIEW",
        "COMPLETED",
        "ABANDONED",
        "CANCELLED",
    }


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (EncounterStatus.CREATED, EncounterStatus.IN_PROGRESS),
        (EncounterStatus.CREATED, EncounterStatus.ABANDONED),
        (EncounterStatus.CREATED, EncounterStatus.CANCELLED),
        (EncounterStatus.IN_PROGRESS, EncounterStatus.AWAITING_REVIEW),
        (EncounterStatus.IN_PROGRESS, EncounterStatus.COMPLETED),
        (EncounterStatus.IN_PROGRESS, EncounterStatus.ABANDONED),
        (EncounterStatus.IN_PROGRESS, EncounterStatus.CANCELLED),
        (EncounterStatus.AWAITING_REVIEW, EncounterStatus.IN_PROGRESS),
        (EncounterStatus.AWAITING_REVIEW, EncounterStatus.COMPLETED),
        (EncounterStatus.AWAITING_REVIEW, EncounterStatus.ABANDONED),
        (EncounterStatus.AWAITING_REVIEW, EncounterStatus.CANCELLED),
    ],
)
def test_encounter_allows_only_documented_nonterminal_transitions(
    source: EncounterStatus, target: EncounterStatus
) -> None:
    encounter = _encounter(source)
    completed_at = (
        datetime(2026, 10, 12, 10, tzinfo=UTC) if target is EncounterStatus.COMPLETED else None
    )

    assert encounter.can_transition_to(target) is True
    transitioned = encounter.transition_to(target, at=completed_at)

    assert transitioned.status is target
    assert transitioned.completed_at == completed_at
    assert encounter.status is source
    assert encounter is not transitioned


@pytest.mark.parametrize(
    "terminal",
    [EncounterStatus.COMPLETED, EncounterStatus.ABANDONED, EncounterStatus.CANCELLED],
)
@pytest.mark.parametrize("target", list(EncounterStatus))
def test_terminal_encounters_reject_every_transition(
    terminal: EncounterStatus, target: EncounterStatus
) -> None:
    encounter = _encounter(terminal)

    assert encounter.can_transition_to(target) is False
    with pytest.raises(InvalidEncounterTransitionError):
        encounter.transition_to(target, at=datetime(2026, 10, 12, 10, tzinfo=UTC))
    assert encounter.status is terminal


def test_invalid_nonterminal_transition_preserves_original_entity() -> None:
    encounter = _encounter()

    with pytest.raises(InvalidEncounterTransitionError):
        encounter.transition_to(
            EncounterStatus.COMPLETED,
            at=datetime(2026, 10, 12, 9, tzinfo=UTC),
        )

    assert encounter.status is EncounterStatus.CREATED
    assert encounter.completed_at is None


def test_encounter_rejects_naive_start_and_normalizes_offset_times() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        Encounter(
            encounter_id=OpaqueId.new(),
            patient_id=None,
            session_id=OpaqueId.new(),
            encounter_type=EncounterType.KIOSK_INTAKE,
            status=EncounterStatus.CREATED,
            started_at=datetime(2026, 10, 12, 8),
        )

    offset = timezone(timedelta(hours=5, minutes=30))
    encounter = Encounter(
        encounter_id=OpaqueId.new(),
        patient_id=None,
        session_id=OpaqueId.new(),
        encounter_type=EncounterType.KIOSK_INTAKE,
        status=EncounterStatus.IN_PROGRESS,
        started_at=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
    )
    completed = encounter.transition_to(
        EncounterStatus.COMPLETED,
        at=datetime(2026, 10, 12, 15, 30, tzinfo=offset),
    )

    assert encounter.started_at == datetime(2026, 10, 12, 8, tzinfo=UTC)
    assert completed.completed_at == datetime(2026, 10, 12, 10, tzinfo=UTC)


def test_completion_requires_time_and_rejects_time_before_start() -> None:
    encounter = _encounter(EncounterStatus.IN_PROGRESS)

    with pytest.raises(ValueError, match="required"):
        encounter.transition_to(EncounterStatus.COMPLETED)
    with pytest.raises(ValueError, match="started_at"):
        encounter.transition_to(
            EncounterStatus.COMPLETED,
            at=datetime(2026, 10, 12, 7, tzinfo=UTC),
        )


def test_noncompleted_encounter_never_accepts_completed_at() -> None:
    with pytest.raises(ValueError, match="COMPLETED"):
        Encounter(
            encounter_id=OpaqueId.new(),
            patient_id=None,
            session_id=OpaqueId.new(),
            encounter_type=EncounterType.RESEARCH_ONLY,
            status=EncounterStatus.ABANDONED,
            started_at=datetime(2026, 10, 12, 8, tzinfo=UTC),
            completed_at=datetime(2026, 10, 12, 9, tzinfo=UTC),
        )


def test_abandoned_and_cancelled_do_not_set_completion_time() -> None:
    encounter = _encounter(EncounterStatus.IN_PROGRESS)

    for target in (EncounterStatus.ABANDONED, EncounterStatus.CANCELLED):
        transitioned = encounter.transition_to(target)
        assert transitioned.completed_at is None


def test_pseudonymous_encounter_requires_session_but_not_patient_or_actor() -> None:
    encounter = _encounter()

    assert encounter.session_id is not None
    assert encounter.patient_id is None
    assert encounter.created_by is None
    with pytest.raises(FrozenInstanceError):
        encounter.status = EncounterStatus.IN_PROGRESS  # type: ignore[misc]
