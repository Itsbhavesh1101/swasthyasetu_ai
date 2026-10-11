"""Immutable, framework-independent background-job contracts."""

from __future__ import annotations

import math
import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Protocol, cast

from app.shared.types import OpaqueId, utc_now

type JsonScalar = str | int | float | bool | None
type FrozenJsonValue = JsonScalar | tuple[FrozenJsonValue, ...] | Mapping[str, FrozenJsonValue]
type JobHandler = Callable[[JobRequest], Awaitable[None]]

MAX_JOB_TYPE_LENGTH = 128
MAX_CORRELATION_ID_LENGTH = 128
_JOB_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


class JobType(str):
    """Validated lowercase dotted job name."""

    def __new__(cls, value: str) -> JobType:
        if not isinstance(value, str):
            raise TypeError("job type must be a string")
        if len(value) > MAX_JOB_TYPE_LENGTH or _JOB_TYPE_PATTERN.fullmatch(value) is None:
            raise ValueError("job type must be a bounded lowercase dotted name")
        return super().__new__(cls, value)


class JobStatus(StrEnum):
    """Provider-neutral job lifecycle states."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    NEEDS_REVIEW = "NEEDS_REVIEW"


def _aware_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _freeze_json(value: object) -> FrozenJsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("job payload must be JSON-compatible")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("job payload must be JSON-compatible")
            frozen[key] = _freeze_json(item)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    raise ValueError("job payload must be JSON-compatible")


def _correlation_id(value: str | None) -> str | None:
    if value is None:
        return None
    if value != value.strip() or not value or len(value) > MAX_CORRELATION_ID_LENGTH:
        raise ValueError("correlation_id must be non-empty and at most 128 characters")
    if not value.isprintable():
        raise ValueError("correlation_id must contain only printable characters")
    return value


@dataclass(frozen=True, slots=True)
class JobRequest:
    """Immutable job instruction with a recursively protected JSON payload."""

    job_id: OpaqueId
    job_type: JobType
    created_at: datetime
    scheduled_at: datetime
    correlation_id: str | None = None
    payload: Mapping[str, FrozenJsonValue] = field(
        default_factory=lambda: MappingProxyType({}), repr=False
    )

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, OpaqueId):
            raise TypeError("job_id must be an OpaqueId")
        object.__setattr__(self, "job_type", JobType(self.job_type))
        object.__setattr__(self, "created_at", _aware_utc("created_at", self.created_at))
        object.__setattr__(self, "scheduled_at", _aware_utc("scheduled_at", self.scheduled_at))
        object.__setattr__(self, "correlation_id", _correlation_id(self.correlation_id))
        frozen_payload = _freeze_json(self.payload)
        if not isinstance(frozen_payload, Mapping):
            raise ValueError("job payload must be a JSON-compatible mapping")
        object.__setattr__(self, "payload", frozen_payload)

    @classmethod
    def create(
        cls,
        *,
        job_type: str | JobType,
        payload: Mapping[str, object],
        job_id: OpaqueId | None = None,
        correlation_id: str | None = None,
        created_at: datetime | None = None,
        scheduled_at: datetime | None = None,
    ) -> JobRequest:
        """Create a request while permitting deterministic caller-supplied values."""
        created = created_at or utc_now()
        return cls(
            job_id=job_id or OpaqueId.new(),
            job_type=JobType(job_type),
            payload=cast(Mapping[str, FrozenJsonValue], payload),
            correlation_id=correlation_id,
            created_at=created,
            scheduled_at=scheduled_at or created,
        )


@dataclass(frozen=True, slots=True)
class JobHandle:
    """Payload-free reference returned to an enqueue caller."""

    job_id: OpaqueId

    def __post_init__(self) -> None:
        if not isinstance(self.job_id, OpaqueId):
            raise TypeError("job_id must be an OpaqueId")


@dataclass(frozen=True, slots=True)
class JobSnapshot:
    """Immutable payload-free process-local job inspection state."""

    job_id: OpaqueId
    job_type: JobType
    status: JobStatus
    error_code: str | None
    created_at: datetime
    scheduled_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class JobDispatcher(Protocol):
    """Asynchronous provider-neutral job enqueue port."""

    async def enqueue(self, job: JobRequest) -> JobHandle: ...


class JobError(Exception):
    """Base error for provider-neutral job operations."""


class DuplicateJobError(JobError):
    """Raised when a process-local job ID is already registered."""


class UnknownJobError(JobError):
    """Raised when process-local inspection references an unknown job."""
