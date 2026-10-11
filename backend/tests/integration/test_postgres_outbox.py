"""Real PostgreSQL atomicity, locking, and outbox-dispatch verification."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, func, select, text

from app.config import DatabaseSettings
from app.events import EventEnvelope, EventType, InProcessEventPublisher
from app.events.dispatcher import OutboxDispatcher, RetryPolicy
from app.events.outbox import OutboxEventRecord, OutboxRepository, OutboxStatus
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres
PROBE_TABLE = "p3b_atomicity_probe"
T0 = datetime(2026, 2, 3, 4, 5, tzinfo=UTC)


class MutableClock:
    """Deterministic timezone-aware integration-test clock."""

    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value


def synthetic_event(*, event_type: str = "SyntheticCreated") -> EventEnvelope:
    return EventEnvelope.create(
        event_type=event_type,
        event_version=1,
        occurred_at=T0 - timedelta(minutes=1),
        correlation_id="correlation-1",
        causation_id="causation-1",
        actor_ref="opaque-actor-1",
        payload={"value": "example"},
    )


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    """Use only the explicit test URL and clean synthetic/outbox rows per test."""
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    async with runtime.engine.begin() as connection:
        await connection.execute(
            text(f"CREATE TABLE IF NOT EXISTS {PROBE_TABLE} (value TEXT PRIMARY KEY)")
        )
        await connection.execute(text(f"TRUNCATE TABLE {PROBE_TABLE}"))
        await connection.execute(delete(OutboxEventRecord))
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(delete(OutboxEventRecord))
            await connection.execute(text(f"DROP TABLE IF EXISTS {PROBE_TABLE}"))
        await runtime.dispose()


async def outbox_count(runtime: DatabaseRuntime) -> int:
    async with runtime.session_factory() as session:
        return int(await session.scalar(select(func.count()).select_from(OutboxEventRecord)) or 0)


async def read_record(runtime: DatabaseRuntime, envelope: EventEnvelope) -> OutboxEventRecord:
    async with runtime.session_factory() as session:
        record = await session.get(OutboxEventRecord, envelope.event_id.value)
        assert record is not None
        return record


async def test_probe_and_outbox_commit_atomically_and_round_trip(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    envelope = synthetic_event()
    async with database_runtime.transaction() as session:
        await session.execute(
            text(f"INSERT INTO {PROBE_TABLE} (value) VALUES (:value)"),
            {"value": "committed"},
        )
        await repository.enqueue(session, envelope, created_at=T0)

    async with database_runtime.session_factory() as session:
        probe = await session.scalar(text(f"SELECT value FROM {PROBE_TABLE}"))
        record = await repository.get_by_event_id(session, envelope.event_id)
    assert probe == "committed"
    assert record is not None
    assert record.to_envelope() == envelope
    assert record.created_at == T0
    assert record.occurred_at == T0 - timedelta(minutes=1)


async def test_probe_and_outbox_roll_back_atomically(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    with pytest.raises(RuntimeError, match="synthetic rollback"):
        async with database_runtime.transaction() as session:
            await session.execute(
                text(f"INSERT INTO {PROBE_TABLE} (value) VALUES (:value)"),
                {"value": "rolled-back"},
            )
            await repository.enqueue(session, synthetic_event(), created_at=T0)
            raise RuntimeError("synthetic rollback")

    async with database_runtime.session_factory() as session:
        probe_count = await session.scalar(text(f"SELECT count(*) FROM {PROBE_TABLE}"))
    assert probe_count == 0
    assert await outbox_count(database_runtime) == 0


async def test_due_selection_uses_skip_locked_and_excludes_future_rows(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    due = synthetic_event()
    future = synthetic_event(event_type="ExampleChanged")
    async with database_runtime.transaction() as session:
        await repository.enqueue(session, due, created_at=T0)
        await repository.enqueue(
            session,
            future,
            created_at=T0,
            available_at=T0 + timedelta(hours=1),
        )

    async with database_runtime.session_factory() as first_session, first_session.begin():
        first = await repository.load_next_due(first_session, now=T0)
        assert first is not None and first.id == due.event_id.value
        async with database_runtime.session_factory() as second_session, second_session.begin():
            second = await repository.load_next_due(second_session, now=T0)
            assert second is None


async def test_dispatch_success_persists_status_timestamp_and_attempt(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    envelope = synthetic_event()
    delivered: list[EventEnvelope] = []

    async def handler(event: EventEnvelope) -> None:
        delivered.append(event)

    async with database_runtime.transaction() as session:
        await repository.enqueue(session, envelope, created_at=T0)
    dispatcher = OutboxDispatcher(
        runtime=database_runtime,
        repository=repository,
        publisher=InProcessEventPublisher({EventType("SyntheticCreated"): (handler,)}),
        clock=MutableClock(T0),
    )

    result = await dispatcher.dispatch_batch(batch_size=5)
    record = await read_record(database_runtime, envelope)

    assert result.selected == result.dispatched == 1
    assert result.retried == result.failed == 0
    assert delivered == [envelope]
    assert record.status == OutboxStatus.DISPATCHED.value
    assert record.attempt_count == 1
    assert record.dispatched_at == T0
    assert record.last_error_code is None


async def test_future_event_waits_and_no_handler_is_successful(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    envelope = synthetic_event()
    clock = MutableClock(T0)
    async with database_runtime.transaction() as session:
        await repository.enqueue(
            session,
            envelope,
            created_at=T0,
            available_at=T0 + timedelta(minutes=1),
        )
    dispatcher = OutboxDispatcher(
        runtime=database_runtime,
        repository=repository,
        publisher=InProcessEventPublisher({}),
        clock=clock,
    )

    early = await dispatcher.dispatch_batch(batch_size=5)
    pending = await read_record(database_runtime, envelope)
    assert early.selected == 0
    assert pending.status == OutboxStatus.PENDING.value
    assert pending.attempt_count == 0

    clock.value = T0 + timedelta(minutes=1)
    due = await dispatcher.dispatch_batch(batch_size=5)
    dispatched = await read_record(database_runtime, envelope)
    assert due.selected == due.dispatched == 1
    assert dispatched.status == OutboxStatus.DISPATCHED.value
    assert dispatched.attempt_count == 1


async def test_dispatch_failure_schedules_retry_then_clears_error_on_success(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    envelope = synthetic_event()
    clock = MutableClock(T0)
    calls = 0

    async def fail_once(event: EventEnvelope) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("private-synthetic-payload-marker")

    async with database_runtime.transaction() as session:
        await repository.enqueue(session, envelope, created_at=T0)
    dispatcher = OutboxDispatcher(
        runtime=database_runtime,
        repository=repository,
        publisher=InProcessEventPublisher({EventType("SyntheticCreated"): (fail_once,)}),
        retry_policy=RetryPolicy(
            max_attempts=3,
            base_delay=timedelta(seconds=5),
            maximum_delay=timedelta(seconds=5),
        ),
        clock=clock,
    )

    first = await dispatcher.dispatch_batch(batch_size=5)
    retry = await read_record(database_runtime, envelope)
    assert first.retried == 1
    assert retry.status == OutboxStatus.PENDING.value
    assert retry.attempt_count == 1
    assert retry.available_at == T0 + timedelta(seconds=5)
    assert retry.last_error_code == "EVENT_DELIVERY_FAILED"
    assert "private-synthetic-payload-marker" not in retry.last_error_code

    clock.value = T0 + timedelta(seconds=5)
    second = await dispatcher.dispatch_batch(batch_size=5)
    delivered = await read_record(database_runtime, envelope)
    assert second.dispatched == 1
    assert delivered.status == OutboxStatus.DISPATCHED.value
    assert delivered.attempt_count == 2
    assert delivered.last_error_code is None
    assert delivered.occurred_at == envelope.occurred_at


async def test_terminal_failure_is_not_selected_again_and_batch_continues(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = OutboxRepository()
    failing = synthetic_event()
    succeeding = synthetic_event(event_type="ExampleChanged")
    clock = MutableClock(T0)

    async def always_fail(event: EventEnvelope) -> None:
        raise RuntimeError("synthetic failure")

    async def succeed(event: EventEnvelope) -> None:
        return None

    async with database_runtime.transaction() as session:
        await repository.enqueue(session, failing, created_at=T0)
        await repository.enqueue(session, succeeding, created_at=T0)
    dispatcher = OutboxDispatcher(
        runtime=database_runtime,
        repository=repository,
        publisher=InProcessEventPublisher(
            {
                EventType("SyntheticCreated"): (always_fail,),
                EventType("ExampleChanged"): (succeed,),
            }
        ),
        retry_policy=RetryPolicy(
            max_attempts=2,
            base_delay=timedelta(seconds=1),
            maximum_delay=timedelta(seconds=1),
        ),
        clock=clock,
    )

    first = await dispatcher.dispatch_batch(batch_size=5)
    retry_record = await read_record(database_runtime, failing)
    succeeded_record = await read_record(database_runtime, succeeding)
    clock.value = T0 + timedelta(seconds=1)
    second = await dispatcher.dispatch_batch(batch_size=5)
    failed_record = await read_record(database_runtime, failing)
    empty = await dispatcher.dispatch_batch(batch_size=5)

    assert first.selected == 2
    assert first.retried == first.dispatched == 1
    assert retry_record.status == OutboxStatus.PENDING.value
    assert retry_record.attempt_count == 1
    assert second.selected == second.failed == 1
    assert failed_record.status == OutboxStatus.FAILED.value
    assert failed_record.attempt_count == 2
    assert succeeded_record.status == OutboxStatus.DISPATCHED.value
    assert empty.selected == 0
