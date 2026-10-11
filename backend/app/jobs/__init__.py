"""Provider-neutral job contracts and an explicit process-local scaffold."""

from app.jobs.contracts import (
    DuplicateJobError,
    JobDispatcher,
    JobError,
    JobHandle,
    JobHandler,
    JobRequest,
    JobSnapshot,
    JobStatus,
    JobType,
    UnknownJobError,
)
from app.jobs.in_process import InProcessJobBackend, InProcessJobDispatcher
from app.jobs.worker import InProcessWorker

__all__ = [
    "DuplicateJobError",
    "InProcessJobBackend",
    "InProcessJobDispatcher",
    "InProcessWorker",
    "JobDispatcher",
    "JobError",
    "JobHandle",
    "JobHandler",
    "JobRequest",
    "JobSnapshot",
    "JobStatus",
    "JobType",
    "UnknownJobError",
]
