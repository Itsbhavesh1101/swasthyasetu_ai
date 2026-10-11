"""Explicit manual transactional outbox dispatcher foundation."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.events.outbox import OutboxRepository
from app.events.publisher import EventPublisher
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now

DELIVERY_FAILURE_CODE = "EVENT_DELIVERY_FAILED"
MAX_BATCH_SIZE = 100


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Deterministic capped exponential retry policy."""

    max_attempts: int = 5
    base_delay: timedelta = timedelta(seconds=1)
    maximum_delay: timedelta = timedelta(minutes=5)

    def __post_init__(self) -> None:
        if isinstance(self.max_attempts, bool) or self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if self.base_delay < timedelta(0):
            raise ValueError("base_delay must not be negative")
        if self.maximum_delay < self.base_delay:
            raise ValueError("maximum_delay must be at least base_delay")

    def delay_after_failure(self, attempt_count: int) -> timedelta:
        """Return the capped delay after a positive failed attempt number."""
        if attempt_count < 1:
            raise ValueError("attempt_count must be positive")
        delay = self.base_delay
        for _ in range(min(attempt_count - 1, 64)):
            if delay >= self.maximum_delay / 2:
                return self.maximum_delay
            delay *= 2
        return min(delay, self.maximum_delay)


@dataclass(frozen=True, slots=True)
class DispatchBatchResult:
    """Payload-free operational counts for one manual dispatch request."""

    selected: int = 0
    dispatched: int = 0
    retried: int = 0
    failed: int = 0


class OutboxDispatcher:
    """Deliver bounded due rows one transaction at a time when explicitly called."""

    def __init__(
        self,
        *,
        runtime: DatabaseRuntime,
        repository: OutboxRepository,
        publisher: EventPublisher,
        retry_policy: RetryPolicy | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._runtime = runtime
        self._repository = repository
        self._publisher = publisher
        self._retry_policy = retry_policy or RetryPolicy()
        self._clock = clock

    @staticmethod
    def validate_batch_size(batch_size: int) -> int:
        """Reject empty or operationally unbounded requests."""
        if isinstance(batch_size, bool) or not 1 <= batch_size <= MAX_BATCH_SIZE:
            raise ValueError(f"batch_size must be between 1 and {MAX_BATCH_SIZE}")
        return batch_size

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("dispatcher clock must return a timezone-aware datetime")
        return value.astimezone(UTC)

    async def dispatch_batch(self, *, batch_size: int = 25) -> DispatchBatchResult:
        """Attempt due rows sequentially and persist each outcome independently."""
        limit = self.validate_batch_size(batch_size)
        selected = dispatched = retried = failed = 0
        for _ in range(limit):
            async with self._runtime.transaction() as session:
                record = await self._repository.load_next_due(session, now=self._now())
                if record is None:
                    break
                selected += 1
                try:
                    await self._publisher.publish(record.to_envelope())
                except Exception:  # noqa: BLE001 - details must not cross this boundary
                    failure_time = self._now()
                    next_attempt = record.attempt_count + 1
                    if next_attempt >= self._retry_policy.max_attempts:
                        self._repository.mark_failed(
                            record,
                            failed_at=failure_time,
                            error_code=DELIVERY_FAILURE_CODE,
                        )
                        failed += 1
                    else:
                        self._repository.schedule_retry(
                            record,
                            failed_at=failure_time,
                            delay=self._retry_policy.delay_after_failure(next_attempt),
                            error_code=DELIVERY_FAILURE_CODE,
                        )
                        retried += 1
                else:
                    self._repository.mark_dispatched(record, dispatched_at=self._now())
                    dispatched += 1
        return DispatchBatchResult(
            selected=selected,
            dispatched=dispatched,
            retried=retried,
            failed=failed,
        )
