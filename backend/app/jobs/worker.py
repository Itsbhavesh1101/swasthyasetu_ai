"""Explicit deterministic worker for the process-local job backend."""

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from types import MappingProxyType

from app.jobs.contracts import JobHandle, JobHandler, JobType
from app.jobs.in_process import (
    JOB_EXECUTION_FAILED,
    JOB_HANDLER_NOT_FOUND,
    InProcessJobBackend,
)
from app.shared.types import utc_now


class InProcessWorker:
    """Run at most one due job when explicitly called; never starts a daemon."""

    def __init__(
        self,
        backend: InProcessJobBackend,
        handlers: Mapping[JobType | str, JobHandler],
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._backend = backend
        self._handlers: Mapping[JobType, JobHandler] = MappingProxyType(
            {JobType(job_type): handler for job_type, handler in handlers.items()}
        )
        self._clock = clock

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("worker clock must return a timezone-aware datetime")
        return value.astimezone(UTC)

    async def run_once(self) -> JobHandle | None:
        """Process the first due job and retain only generic failure codes."""
        request = await self._backend.claim_first_due(self._now())
        if request is None:
            return None

        handle = JobHandle(request.job_id)
        handler = self._handlers.get(request.job_type)
        if handler is None:
            await self._backend.mark_failed(
                request.job_id,
                self._now(),
                error_code=JOB_HANDLER_NOT_FOUND,
            )
            return handle

        try:
            await handler(request)
        except Exception:
            await self._backend.mark_failed(
                request.job_id,
                self._now(),
                error_code=JOB_EXECUTION_FAILED,
            )
        else:
            await self._backend.mark_succeeded(request.job_id, self._now())
        return handle
