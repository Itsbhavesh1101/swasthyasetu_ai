"""Non-durable, process-local job queue for development and tests only."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime

from app.jobs.contracts import (
    DuplicateJobError,
    JobHandle,
    JobRequest,
    JobSnapshot,
    JobStatus,
    UnknownJobError,
)
from app.shared.types import OpaqueId

JOB_HANDLER_NOT_FOUND = "JOB_HANDLER_NOT_FOUND"
JOB_EXECUTION_FAILED = "JOB_EXECUTION_FAILED"
_FAILURE_CODES = frozenset({JOB_HANDLER_NOT_FOUND, JOB_EXECUTION_FAILED})


def _aware_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(slots=True)
class _JobRecord:
    request: JobRequest
    status: JobStatus = JobStatus.QUEUED
    error_code: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class InProcessJobBackend:
    """Shared volatile state; lost on restart and never shared across processes."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._queue: deque[OpaqueId] = deque()
        self._records: dict[OpaqueId, _JobRecord] = {}

    async def enqueue(self, job: JobRequest) -> JobHandle:
        """Store a request as QUEUED without executing any handler."""
        async with self._lock:
            if job.job_id in self._records:
                raise DuplicateJobError("job ID already exists")
            self._records[job.job_id] = _JobRecord(request=job)
            self._queue.append(job.job_id)
        return JobHandle(job.job_id)

    async def claim_first_due(self, now: datetime) -> JobRequest | None:
        """Claim the first due queued request while preserving FIFO among due jobs."""
        normalized_now = _aware_utc("now", now)
        async with self._lock:
            for job_id in self._queue:
                record = self._records[job_id]
                if (
                    record.status is JobStatus.QUEUED
                    and record.request.scheduled_at <= normalized_now
                ):
                    record.status = JobStatus.RUNNING
                    record.started_at = normalized_now
                    return record.request
        return None

    async def mark_succeeded(self, job_id: OpaqueId, completed_at: datetime) -> None:
        normalized_completed_at = _aware_utc("completed_at", completed_at)
        async with self._lock:
            record = self._records[job_id]
            record.status = JobStatus.SUCCEEDED
            record.error_code = None
            record.completed_at = normalized_completed_at

    async def mark_failed(
        self, job_id: OpaqueId, completed_at: datetime, *, error_code: str
    ) -> None:
        normalized_completed_at = _aware_utc("completed_at", completed_at)
        if error_code not in _FAILURE_CODES:
            raise ValueError("error_code must be an approved safe job failure code")
        async with self._lock:
            record = self._records[job_id]
            record.status = JobStatus.FAILED
            record.error_code = error_code
            record.completed_at = normalized_completed_at

    async def inspect(self, handle: JobHandle) -> JobSnapshot:
        """Return only safe immutable metadata for a known process-local job."""
        async with self._lock:
            record = self._records.get(handle.job_id)
            if record is None:
                raise UnknownJobError("job is unknown")
            request = record.request
            return JobSnapshot(
                job_id=request.job_id,
                job_type=request.job_type,
                status=record.status,
                error_code=record.error_code,
                created_at=request.created_at,
                scheduled_at=request.scheduled_at,
                started_at=record.started_at,
                completed_at=record.completed_at,
            )


class InProcessJobDispatcher:
    """Provider implementation that only enqueues into process-local memory."""

    def __init__(self, backend: InProcessJobBackend) -> None:
        self._backend = backend

    async def enqueue(self, job: JobRequest) -> JobHandle:
        return await self._backend.enqueue(job)
