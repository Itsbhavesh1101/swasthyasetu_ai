"""Network-free transactional outbox contract tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy import Table

from app.events import EventEnvelope
from app.events.dispatcher import DispatchBatchResult, OutboxDispatcher, RetryPolicy
from app.events.outbox import OutboxEventRecord, OutboxRepository, OutboxStatus
from app.shared.persistence import Base

NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)


def event() -> EventEnvelope:
    return EventEnvelope.create(
        event_type="SyntheticCreated",
        event_version=2,
        occurred_at=NOW - timedelta(minutes=1),
        correlation_id="correlation-1",
        causation_id="causation-1",
        actor_ref="opaque-actor-1",
        payload={"value": "example"},
    )


def test_outbox_has_required_schema_alongside_registered_module_tables() -> None:
    table = OutboxEventRecord.__table__
    assert isinstance(table, Table)

    assert set(Base.metadata.tables) == {
        "outbox_events",
        "sessions",
        "actors",
        "actor_roles",
        "consent_records",
    }
    assert tuple(table.columns) == tuple(
        table.c[name]
        for name in (
            "id",
            "event_type",
            "event_version",
            "aggregate_type",
            "aggregate_id",
            "correlation_id",
            "causation_id",
            "actor_ref",
            "occurred_at",
            "payload",
            "status",
            "attempt_count",
            "available_at",
            "dispatched_at",
            "last_error_code",
            "created_at",
        )
    )
    assert {index.name for index in table.indexes} == {
        "ix_outbox_events_status_available_at",
        "ix_outbox_events_event_type",
        "ix_outbox_events_aggregate_id",
    }
    assert {constraint.name for constraint in table.constraints if constraint.name is not None} >= {
        "pk_outbox_events",
        "ck_outbox_events_event_version_positive",
        "ck_outbox_events_attempt_count_nonnegative",
        "ck_outbox_events_status_supported",
    }


async def test_enqueue_uses_caller_session_without_committing() -> None:
    session = MagicMock()
    repository = OutboxRepository()
    envelope = event()

    record = await repository.enqueue(
        session,
        envelope,
        aggregate_type="SyntheticAggregate",
        created_at=NOW,
    )

    session.add.assert_called_once_with(record)
    session.commit.assert_not_called()
    assert record.id == envelope.event_id.value
    assert record.event_type == "SyntheticCreated"
    assert record.status == OutboxStatus.PENDING.value
    assert record.attempt_count == 0
    assert record.occurred_at == NOW - timedelta(minutes=1)
    assert record.created_at == NOW
    assert record.available_at == NOW


def test_outbox_record_reconstructs_envelope_without_metadata_loss() -> None:
    envelope = event()
    record = OutboxRepository().build_record(envelope, created_at=NOW)

    assert record.to_envelope() == envelope
    assert "example" not in repr(record)


def test_retry_policy_is_immutable_validated_and_capped() -> None:
    policy = RetryPolicy(
        max_attempts=4,
        base_delay=timedelta(seconds=2),
        maximum_delay=timedelta(seconds=5),
    )

    assert policy.delay_after_failure(1) == timedelta(seconds=2)
    assert policy.delay_after_failure(2) == timedelta(seconds=4)
    assert policy.delay_after_failure(3) == timedelta(seconds=5)
    assert policy.delay_after_failure(10_000) == timedelta(seconds=5)
    with pytest.raises(FrozenInstanceError):
        policy.max_attempts = 5  # type: ignore[misc]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_attempts": 0}, "max_attempts"),
        ({"base_delay": timedelta(seconds=-1)}, "base_delay"),
        (
            {"base_delay": timedelta(seconds=2), "maximum_delay": timedelta(seconds=1)},
            "maximum_delay",
        ),
    ],
)
def test_retry_policy_rejects_invalid_configuration(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        RetryPolicy(**kwargs)  # type: ignore[arg-type]


def test_outbox_status_mutations_follow_attempt_semantics() -> None:
    repository = OutboxRepository()
    record = repository.build_record(event(), created_at=NOW)

    repository.schedule_retry(
        record,
        failed_at=NOW,
        delay=timedelta(seconds=7),
        error_code="EVENT_DELIVERY_FAILED",
    )
    assert record.status == OutboxStatus.PENDING.value
    assert record.attempt_count == 1
    assert record.available_at == NOW + timedelta(seconds=7)
    assert record.dispatched_at is None

    repository.mark_dispatched(record, dispatched_at=NOW + timedelta(seconds=7))
    assert record.status == OutboxStatus.DISPATCHED.value
    assert record.attempt_count == 2
    assert record.last_error_code is None

    terminal = repository.build_record(event(), created_at=NOW)
    repository.mark_failed(terminal, failed_at=NOW, error_code="EVENT_DELIVERY_FAILED")
    assert terminal.status == OutboxStatus.FAILED.value
    assert terminal.attempt_count == 1
    assert terminal.dispatched_at is None


def test_outbox_rejects_raw_exception_text_as_failure_metadata() -> None:
    record = OutboxRepository().build_record(event(), created_at=NOW)

    with pytest.raises(ValueError, match="machine-readable code"):
        OutboxRepository().mark_failed(
            record,
            failed_at=NOW,
            error_code="private exception details",
        )
    assert record.status == OutboxStatus.PENDING.value
    assert record.attempt_count == 0
    assert record.last_error_code is None


def test_dispatch_result_contains_only_safe_counts() -> None:
    result = DispatchBatchResult(selected=4, dispatched=2, retried=1, failed=1)

    assert result.selected == 4
    assert "payload" not in repr(result).lower()


@pytest.mark.parametrize("batch_size", [0, -1, 101])
def test_dispatcher_rejects_unbounded_batch_sizes(batch_size: int) -> None:
    with pytest.raises(ValueError, match="batch_size"):
        OutboxDispatcher.validate_batch_size(batch_size)


def test_dispatcher_accepts_reasonable_batch_size() -> None:
    assert OutboxDispatcher.validate_batch_size(25) == 25
