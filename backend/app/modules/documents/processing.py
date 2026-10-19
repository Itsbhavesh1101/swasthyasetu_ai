"""Pure synthetic processing-attempt and generic job-intent mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum

from app.jobs.contracts import JobRequest
from app.shared.types import OpaqueId

MAX_GENERATION = 100
MAX_RETRY_BUDGET = 3
_TOKEN = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")


class ProcessingGuardCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_STATE = "INVALID_STATE"
    STALE_GENERATION = "STALE_GENERATION"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    RETRY_NOT_ALLOWED = "RETRY_NOT_ALLOWED"


class ProcessingGuardError(ValueError):
    """Content-free processing guard failure."""

    def __init__(self, code: ProcessingGuardCode) -> None:
        self.code = code
        super().__init__(code.value)


class AttemptStage(StrEnum):
    QUEUED = "QUEUED"
    RECOGNIZING = "RECOGNIZING"
    COMPLETED = "COMPLETED"


class AttemptStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    CANCELLED = "CANCELLED"


class AttemptFailureCode(StrEnum):
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"
    ENGINE_UNAVAILABLE = "ENGINE_UNAVAILABLE"
    REFUSED = "REFUSED"
    MALFORMED_RESULT = "MALFORMED_RESULT"
    STALE_RESULT = "STALE_RESULT"


class RetryClassification(StrEnum):
    NONE = "NONE"
    RETRYABLE = "RETRYABLE"
    TERMINAL = "TERMINAL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


def _error(code: ProcessingGuardCode) -> ProcessingGuardError:
    return ProcessingGuardError(code)


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise _error(ProcessingGuardCode.INVALID_TYPE)
    if value.tzinfo is None or value.utcoffset() is None:
        raise _error(ProcessingGuardCode.INVALID_VALUE)
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessingAttempt:
    """In-memory attempt state, distinct from document lifecycle and generic job state."""

    attempt_id: OpaqueId
    document_id: OpaqueId
    request_id: OpaqueId
    generation: int
    source_version: str
    routing_version: str
    idempotency_ref: str
    stage: AttemptStage
    status: AttemptStatus
    created_at: datetime
    deadline_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    failure_code: AttemptFailureCode | None
    retry_classification: RetryClassification
    retry_budget: int

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, OpaqueId)
            for value in (self.attempt_id, self.document_id, self.request_id)
        ):
            raise _error(ProcessingGuardCode.INVALID_TYPE)
        if len({self.attempt_id, self.document_id, self.request_id}) != 3:
            raise _error(ProcessingGuardCode.DUPLICATE_IDENTITY)
        if type(self.generation) is not int or not 1 <= self.generation <= MAX_GENERATION:
            raise _error(ProcessingGuardCode.INVALID_VALUE)
        if type(self.retry_budget) is not int or not 0 <= self.retry_budget <= MAX_RETRY_BUDGET:
            raise _error(ProcessingGuardCode.INVALID_VALUE)
        if any(
            not isinstance(value, str) or _TOKEN.fullmatch(value) is None
            for value in (self.source_version, self.routing_version, self.idempotency_ref)
        ):
            raise _error(ProcessingGuardCode.INVALID_VALUE)
        if (
            not isinstance(self.stage, AttemptStage)
            or not isinstance(self.status, AttemptStatus)
            or not isinstance(self.retry_classification, RetryClassification)
        ):
            raise _error(ProcessingGuardCode.INVALID_TYPE)
        created = _utc(self.created_at)
        deadline = _utc(self.deadline_at)
        started = None if self.started_at is None else _utc(self.started_at)
        completed = None if self.completed_at is None else _utc(self.completed_at)
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "deadline_at", deadline)
        object.__setattr__(self, "started_at", started)
        object.__setattr__(self, "completed_at", completed)
        if (
            deadline <= created
            or (started is not None and not created <= started <= deadline)
            or (completed is not None and (started is None or completed < started))
        ):
            raise _error(ProcessingGuardCode.INVALID_VALUE)
        if self.status is AttemptStatus.QUEUED:
            valid = (
                self.stage is AttemptStage.QUEUED
                and started is None
                and completed is None
                and self.failure_code is None
                and self.retry_classification is RetryClassification.NONE
            )
        elif self.status is AttemptStatus.RUNNING:
            valid = (
                self.stage is AttemptStage.RECOGNIZING
                and started is not None
                and completed is None
                and self.failure_code is None
                and self.retry_classification is RetryClassification.NONE
            )
        elif self.status is AttemptStatus.SUCCEEDED:
            valid = (
                self.stage is AttemptStage.COMPLETED
                and started is not None
                and completed is not None
                and self.failure_code is None
                and self.retry_classification is RetryClassification.NONE
            )
        else:
            valid = (
                self.stage is AttemptStage.COMPLETED
                and started is not None
                and completed is not None
                and self.failure_code is not None
                and self.retry_classification is not RetryClassification.NONE
            )
        if not valid:
            raise _error(ProcessingGuardCode.INVALID_STATE)

    def _check(self, generation: int) -> None:
        if generation != self.generation:
            raise _error(ProcessingGuardCode.STALE_GENERATION)

    def start(self, *, at: datetime, generation: int) -> ProcessingAttempt:
        self._check(generation)
        moment = _utc(at)
        if self.status is not AttemptStatus.QUEUED:
            raise _error(ProcessingGuardCode.INVALID_STATE)
        if moment > self.deadline_at:
            raise _error(ProcessingGuardCode.DEADLINE_EXCEEDED)
        return replace(
            self, stage=AttemptStage.RECOGNIZING, status=AttemptStatus.RUNNING, started_at=moment
        )

    def succeed(self, *, at: datetime, generation: int) -> ProcessingAttempt:
        self._check(generation)
        moment = _utc(at)
        if self.status is not AttemptStatus.RUNNING or moment > self.deadline_at:
            raise _error(ProcessingGuardCode.INVALID_STATE)
        return replace(
            self, stage=AttemptStage.COMPLETED, status=AttemptStatus.SUCCEEDED, completed_at=moment
        )

    def fail(
        self,
        *,
        at: datetime,
        generation: int,
        code: AttemptFailureCode,
        classification: RetryClassification,
    ) -> ProcessingAttempt:
        self._check(generation)
        if (
            self.status is not AttemptStatus.RUNNING
            or not isinstance(code, AttemptFailureCode)
            or classification in {RetryClassification.NONE}
        ):
            raise _error(ProcessingGuardCode.INVALID_STATE)
        status = (
            AttemptStatus.NEEDS_REVIEW
            if classification is RetryClassification.NEEDS_REVIEW
            else AttemptStatus.FAILED
        )
        return replace(
            self,
            stage=AttemptStage.COMPLETED,
            status=status,
            completed_at=_utc(at),
            failure_code=code,
            retry_classification=classification,
        )

    def retry(
        self,
        *,
        attempt_id: OpaqueId,
        idempotency_ref: str,
        created_at: datetime,
        deadline_at: datetime,
    ) -> ProcessingAttempt:
        if (
            self.status not in {AttemptStatus.FAILED, AttemptStatus.NEEDS_REVIEW}
            or self.retry_classification is not RetryClassification.RETRYABLE
            or self.retry_budget == 0
        ):
            raise _error(ProcessingGuardCode.RETRY_NOT_ALLOWED)
        if attempt_id == self.attempt_id:
            raise _error(ProcessingGuardCode.DUPLICATE_IDENTITY)
        created = _utc(created_at)
        if idempotency_ref == self.idempotency_ref or (
            self.completed_at is not None and created < self.completed_at
        ):
            raise _error(ProcessingGuardCode.DUPLICATE_IDENTITY)
        return ProcessingAttempt(
            attempt_id=attempt_id,
            document_id=self.document_id,
            request_id=self.request_id,
            generation=self.generation + 1,
            source_version=self.source_version,
            routing_version=self.routing_version,
            idempotency_ref=idempotency_ref,
            stage=AttemptStage.QUEUED,
            status=AttemptStatus.QUEUED,
            created_at=created,
            deadline_at=deadline_at,
            started_at=None,
            completed_at=None,
            failure_code=None,
            retry_classification=RetryClassification.NONE,
            retry_budget=self.retry_budget - 1,
        )


def build_job_intent(attempt: ProcessingAttempt, *, job_id: OpaqueId) -> JobRequest:
    """Compose the existing volatile job contract with content-free metadata only."""
    if attempt.status is not AttemptStatus.QUEUED:
        raise _error(ProcessingGuardCode.INVALID_STATE)
    return JobRequest.create(
        job_id=job_id,
        job_type="documents.synthetic_process",
        created_at=attempt.created_at,
        scheduled_at=attempt.created_at,
        correlation_id=None,
        payload={
            "attempt_id": str(attempt.attempt_id),
            "document_id": str(attempt.document_id),
            "generation": attempt.generation,
            "routing_version": attempt.routing_version,
        },
    )
