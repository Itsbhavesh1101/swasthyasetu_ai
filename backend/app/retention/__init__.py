"""Provider-neutral retention/purge engineering foundation."""

from app.retention.contracts import (
    PolicyCode,
    PolicyVersion,
    PurgeAuthorization,
    PurgeAuthorizationDecision,
    PurgeObserver,
    PurgePlan,
    PurgeRunResult,
    PurgeRunStatus,
    PurgeTarget,
    PurgeTargetAdapter,
    PurgeTargetIdentity,
    PurgeTargetKind,
    PurgeTargetOutcome,
    PurgeTargetReceipt,
)
from app.retention.coordinator import PurgeCoordinator
from app.retention.restore import (
    PurgeTombstone,
    RestoreDecision,
    RestoreDisposition,
    RestoredTarget,
    RestoreReconciler,
)
from app.retention.telemetry import PURGE_FAILURES, PURGE_TARGET_OUTCOMES, PurgeTelemetry

__all__ = [
    "PURGE_FAILURES",
    "PURGE_TARGET_OUTCOMES",
    "PolicyCode",
    "PolicyVersion",
    "PurgeAuthorization",
    "PurgeAuthorizationDecision",
    "PurgeCoordinator",
    "PurgeObserver",
    "PurgePlan",
    "PurgeRunResult",
    "PurgeRunStatus",
    "PurgeTarget",
    "PurgeTargetAdapter",
    "PurgeTargetIdentity",
    "PurgeTargetKind",
    "PurgeTargetOutcome",
    "PurgeTargetReceipt",
    "PurgeTelemetry",
    "PurgeTombstone",
    "RestoreDecision",
    "RestoreDisposition",
    "RestoreReconciler",
    "RestoredTarget",
]
