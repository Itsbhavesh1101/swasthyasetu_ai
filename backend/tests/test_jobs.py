"""Provider-neutral process-local job contract tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest

from app.jobs import (
    DuplicateJobError,
    InProcessJobBackend,
    InProcessJobDispatcher,
    InProcessWorker,
    JobHandler,
    JobRequest,
    JobStatus,
    JobType,
    UnknownJobError,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)


def job(**overrides: object) -> JobRequest:
    """Build one deterministic synthetic job."""
    values: dict[str, object] = {
        "job_id": OpaqueId.parse("00000000-0000-4000-8000-000000000001"),
        "job_type": "synthetic.echo",
        "payload": {"value": "example", "nested": {"enabled": True}},
        "correlation_id": "correlation-1",
        "created_at": NOW,
        "scheduled_at": NOW,
    }
    values.update(overrides)
    return JobRequest.create(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    ["", " ", "Synthetic.echo", "synthetic", ".synthetic", "synthetic.", "a..b", "a-b", "x" * 129],
)
def test_job_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        JobType(value)


def test_job_request_is_immutable_copy_protected_and_payload_private() -> None:
    source = {"value": "synthetic-private-worker-detail", "items": [1, 2]}
    request = job(payload=source)
    source["value"] = "changed"
    cast(list[int], source["items"]).append(3)

    assert request.payload == {"value": "synthetic-private-worker-detail", "items": (1, 2)}
    assert "synthetic-private-worker-detail" not in repr(request)
    with pytest.raises(TypeError):
        request.payload["value"] = "changed"
    with pytest.raises(FrozenInstanceError):
        request.correlation_id = "changed"  # type: ignore[misc]


def test_job_request_rejects_non_json_payload_and_validates_time() -> None:
    with pytest.raises(ValueError, match="JSON-compatible"):
        job(payload={"invalid": object()})
    with pytest.raises(ValueError, match="timezone-aware"):
        job(created_at=datetime(2026, 1, 2, 3, 4))

    offset = datetime.fromisoformat("2026-01-02T08:34:00+05:30")
    assert job(created_at=offset, scheduled_at=offset).created_at == NOW


async def test_worker_smoke_separates_enqueue_from_execution() -> None:
    backend = InProcessJobBackend()
    dispatcher = InProcessJobDispatcher(backend)
    received: list[JobRequest] = []

    async def handler(request: JobRequest) -> None:
        received.append(request)

    handlers: dict[JobType | str, JobHandler] = {JobType("synthetic.echo"): handler}
    worker = InProcessWorker(backend, handlers, clock=lambda: NOW)
    handlers.clear()
    request = job()
    handle = await dispatcher.enqueue(request)

    assert received == []
    assert (await backend.inspect(handle)).status is JobStatus.QUEUED
    assert await worker.run_once() == handle
    assert received == [request]
    assert received[0].correlation_id == "correlation-1"
    assert (await backend.inspect(handle)).status is JobStatus.SUCCEEDED


async def test_duplicate_id_and_unknown_handle_fail_deterministically() -> None:
    backend = InProcessJobBackend()
    dispatcher = InProcessJobDispatcher(backend)
    handle = await dispatcher.enqueue(job())

    with pytest.raises(DuplicateJobError):
        await dispatcher.enqueue(job(payload={"value": "other"}))
    with pytest.raises(UnknownJobError):
        await backend.inspect(type(handle)(OpaqueId.new()))


async def test_future_job_is_not_run_early_and_fifo_is_preserved() -> None:
    backend = InProcessJobBackend()
    dispatcher = InProcessJobDispatcher(backend)
    calls: list[str] = []
    clock = [NOW]

    async def handler(request: JobRequest) -> None:
        calls.append(request.correlation_id or "")

    worker = InProcessWorker(backend, {"synthetic.echo": handler}, clock=lambda: clock[0])
    future = job(correlation_id="future", scheduled_at=NOW + timedelta(seconds=1))
    due = job(
        job_id=OpaqueId.parse("00000000-0000-4000-8000-000000000002"),
        correlation_id="due",
    )
    await dispatcher.enqueue(future)
    await dispatcher.enqueue(due)

    assert await worker.run_once() is not None
    assert calls == ["due"]
    clock[0] += timedelta(seconds=1)
    assert await worker.run_once() is not None
    assert calls == ["due", "future"]
    assert await worker.run_once() is None


async def test_backend_rejects_non_generic_failure_details() -> None:
    backend = InProcessJobBackend()
    handle = await InProcessJobDispatcher(backend).enqueue(job())
    await backend.claim_first_due(NOW)

    with pytest.raises(ValueError, match="approved safe"):
        await backend.mark_failed(
            handle.job_id,
            NOW,
            error_code="synthetic-private-worker-detail",
        )
    assert (await backend.inspect(handle)).status is JobStatus.RUNNING


async def test_missing_handler_records_only_safe_failure_code() -> None:
    backend = InProcessJobBackend()
    handle = await InProcessJobDispatcher(backend).enqueue(job())

    assert await InProcessWorker(backend, {}, clock=lambda: NOW).run_once() == handle
    snapshot = await backend.inspect(handle)
    assert snapshot.status is JobStatus.FAILED
    assert snapshot.error_code == "JOB_HANDLER_NOT_FOUND"
    assert "payload" not in repr(snapshot).lower()


async def test_handler_exception_is_private_and_worker_processes_later_job() -> None:
    marker = "synthetic-private-worker-detail"
    backend = InProcessJobBackend()
    dispatcher = InProcessJobDispatcher(backend)
    calls = 0

    async def handler(request: JobRequest) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError(marker)

    worker = InProcessWorker(backend, {"synthetic.echo": handler}, clock=lambda: NOW)
    first = await dispatcher.enqueue(job())
    second = await dispatcher.enqueue(
        job(job_id=OpaqueId.parse("00000000-0000-4000-8000-000000000002"))
    )

    assert await worker.run_once() == first
    failed = await backend.inspect(first)
    assert failed.status is JobStatus.FAILED
    assert failed.error_code == "JOB_EXECUTION_FAILED"
    assert marker not in repr(failed)
    assert await worker.run_once() == second
    assert (await backend.inspect(second)).status is JobStatus.SUCCEEDED
    assert await worker.run_once() is None
