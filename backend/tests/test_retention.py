from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

import pytest
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from app.config import ObservabilitySettings
from app.retention import (
    PURGE_FAILURES,
    PURGE_TARGET_OUTCOMES,
    PolicyCode,
    PolicyVersion,
    PurgeAuthorization,
    PurgeAuthorizationDecision,
    PurgeCoordinator,
    PurgePlan,
    PurgeRunResult,
    PurgeRunStatus,
    PurgeTarget,
    PurgeTargetAdapter,
    PurgeTargetIdentity,
    PurgeTargetKind,
    PurgeTargetOutcome,
    PurgeTargetReceipt,
    PurgeTelemetry,
    PurgeTombstone,
    RestoreDecision,
    RestoreDisposition,
    RestoredTarget,
    RestoreReconciler,
)
from app.shared.observability import create_observability_runtime
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 30, 12, 0, tzinfo=UTC)


def opaque(value: int) -> OpaqueId:
    return OpaqueId(UUID(int=value))


def authorization(
    decision: PurgeAuthorizationDecision = PurgeAuthorizationDecision.AUTHORIZED,
    *,
    holds: tuple[str, ...] = (),
) -> PurgeAuthorization:
    return PurgeAuthorization(
        decision=decision,
        policy_code=PolicyCode("platform.retention"),
        policy_version=PolicyVersion("2026-10-30.1"),
        evaluated_at=NOW,
        hold_references=holds,
    )


def target(
    value: int = 1,
    *,
    kind: PurgeTargetKind = PurgeTargetKind.DATABASE_RECORD,
    generation: int = 1,
    locator: str = "synthetic/internal/locator",
) -> PurgeTarget:
    return PurgeTarget(
        identity=PurgeTargetIdentity(kind=kind, target_id=opaque(value)),
        generation=generation,
        locator=locator,
    )


def plan(
    *targets: PurgeTarget,
    decision: PurgeAuthorizationDecision = PurgeAuthorizationDecision.AUTHORIZED,
    holds: tuple[str, ...] = (),
) -> PurgePlan:
    return PurgePlan(
        plan_id=opaque(100),
        subject_id=opaque(200),
        requested_at=NOW,
        authorization=authorization(decision, holds=holds),
        targets=targets,
    )


@pytest.mark.parametrize(
    ("factory", "error"),
    [
        (lambda: PolicyCode("Platform.Retention"), ValueError),
        (lambda: PolicyCode(" platform.retention"), ValueError),
        (lambda: PolicyVersion(""), ValueError),
        (
            lambda: PurgeTargetIdentity(
                kind="DATABASE_RECORD",  # type: ignore[arg-type]
                target_id=opaque(1),
            ),
            TypeError,
        ),
        (
            lambda: PurgeTargetIdentity(
                kind=PurgeTargetKind.DATABASE_RECORD,
                target_id="not-an-id",  # type: ignore[arg-type]
            ),
            TypeError,
        ),
        (lambda: target(generation=0), ValueError),
        (lambda: target(locator=""), ValueError),
        (lambda: target(locator=" leading"), ValueError),
        (
            lambda: PurgeAuthorization(
                decision=PurgeAuthorizationDecision.AUTHORIZED,
                policy_code=PolicyCode("platform.retention"),
                policy_version=PolicyVersion("v1"),
                evaluated_at=datetime(2026, 1, 1),
            ),
            ValueError,
        ),
        (
            lambda: authorization(PurgeAuthorizationDecision.AUTHORIZED, holds=("hold-1",)),
            ValueError,
        ),
        (
            lambda: authorization(PurgeAuthorizationDecision.BLOCKED_BY_HOLD),
            ValueError,
        ),
        (
            lambda: PurgeTargetReceipt(
                target=target(),
                outcome=PurgeTargetOutcome.DELETED,
                error_code="PURGE_FAILED",
            ),
            ValueError,
        ),
        (
            lambda: PurgeTargetReceipt(
                target=target(),
                outcome=PurgeTargetOutcome.FAILED,
                error_code=None,
            ),
            ValueError,
        ),
    ],
)
def test_direct_constructors_reject_invalid_values(
    factory: Callable[[], object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        factory()


def test_timestamps_normalize_to_utc_and_sensitive_values_are_not_represented() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    sensitive_locator = "synthetic-sensitive-locator"
    item = target(locator=sensitive_locator)
    auth = PurgeAuthorization(
        decision=PurgeAuthorizationDecision.NOT_AUTHORIZED,
        policy_code=PolicyCode("platform.retention"),
        policy_version=PolicyVersion("v1"),
        evaluated_at=NOW.astimezone(offset),
    )
    purge_plan = PurgePlan(
        plan_id=opaque(100),
        subject_id=opaque(200),
        requested_at=NOW.astimezone(offset),
        authorization=auth,
        targets=(item,),
    )

    assert auth.evaluated_at.tzinfo is UTC
    assert purge_plan.requested_at.tzinfo is UTC
    assert sensitive_locator not in repr(item)
    assert str(purge_plan.subject_id) not in repr(purge_plan)


def test_plan_rejects_duplicate_target_identity_even_across_generations() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        plan(target(generation=1), target(generation=2))


@pytest.mark.parametrize(
    ("status", "receipts"),
    [
        (PurgeRunStatus.BLOCKED, (PurgeTargetReceipt(target(), PurgeTargetOutcome.DELETED),)),
        (PurgeRunStatus.COMPLETED, ()),
        (
            PurgeRunStatus.COMPLETED,
            (PurgeTargetReceipt(target(), PurgeTargetOutcome.FAILED, "PURGE_FAILED"),),
        ),
        (
            PurgeRunStatus.PARTIAL_FAILURE,
            (PurgeTargetReceipt(target(), PurgeTargetOutcome.DELETED),),
        ),
        (
            PurgeRunStatus.FAILED,
            (PurgeTargetReceipt(target(), PurgeTargetOutcome.DELETED),),
        ),
    ],
)
def test_run_result_direct_constructor_rejects_inconsistent_aggregates(
    status: PurgeRunStatus, receipts: tuple[PurgeTargetReceipt, ...]
) -> None:
    with pytest.raises(ValueError):
        PurgeRunResult(plan_id=opaque(100), status=status, receipts=receipts)


class SyntheticAdapter:
    def __init__(
        self,
        kind: PurgeTargetKind,
        *,
        fail: bool = False,
        mismatched_receipt: bool = False,
    ) -> None:
        self.kind = kind
        self.fail = fail
        self.mismatched_receipt = mismatched_receipt
        self.calls: list[PurgeTarget] = []
        self._deleted: set[tuple[PurgeTargetIdentity, int]] = set()

    async def purge(self, item: PurgeTarget) -> PurgeTargetReceipt:
        self.calls.append(item)
        if self.fail:
            raise RuntimeError("synthetic-sensitive-adapter-detail")
        if self.mismatched_receipt:
            return PurgeTargetReceipt(
                target=target(999, kind=self.kind),
                outcome=PurgeTargetOutcome.DELETED,
            )
        key = (item.identity, item.generation)
        outcome = (
            PurgeTargetOutcome.ALREADY_ABSENT
            if key in self._deleted
            else PurgeTargetOutcome.DELETED
        )
        self._deleted.add(key)
        return PurgeTargetReceipt(target=item, outcome=outcome)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("decision", "holds"),
    [
        (PurgeAuthorizationDecision.NOT_AUTHORIZED, ()),
        (PurgeAuthorizationDecision.BLOCKED_BY_HOLD, ("synthetic-hold-reference",)),
    ],
)
async def test_blocked_plans_never_call_adapters(
    decision: PurgeAuthorizationDecision, holds: tuple[str, ...]
) -> None:
    adapter = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    coordinator = PurgeCoordinator(adapters=(adapter,))

    result = await coordinator.execute(plan(target(), decision=decision, holds=holds))

    assert result.status is PurgeRunStatus.BLOCKED
    assert result.receipts == ()
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_authorized_multi_target_plan_is_complete_and_idempotent_on_retry() -> None:
    database = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    objects = SyntheticAdapter(PurgeTargetKind.OBJECT_STORAGE_OBJECT)
    coordinator = PurgeCoordinator(adapters=(database, objects))
    purge_plan = plan(
        target(1),
        target(2, kind=PurgeTargetKind.OBJECT_STORAGE_OBJECT),
    )

    first = await coordinator.execute(purge_plan)
    second = await coordinator.execute(purge_plan)

    assert first.status is PurgeRunStatus.COMPLETED
    assert [receipt.outcome for receipt in first.receipts] == [
        PurgeTargetOutcome.DELETED,
        PurgeTargetOutcome.DELETED,
    ]
    assert second.status is PurgeRunStatus.COMPLETED
    assert all(receipt.outcome is PurgeTargetOutcome.ALREADY_ABSENT for receipt in second.receipts)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["missing", "exception", "mismatch"])
async def test_adapter_failures_are_generic_and_make_result_partial(mode: str) -> None:
    marker = "synthetic-sensitive-adapter-detail"
    if mode == "missing":
        adapters: tuple[PurgeTargetAdapter, ...] = ()
    else:
        adapters = cast(
            tuple[PurgeTargetAdapter, ...],
            (
                SyntheticAdapter(
                    PurgeTargetKind.DATABASE_RECORD,
                    fail=mode == "exception",
                    mismatched_receipt=mode == "mismatch",
                ),
            ),
        )
    coordinator = PurgeCoordinator(adapters=adapters)

    result = await coordinator.execute(plan(target(locator=marker)))

    assert result.status is PurgeRunStatus.FAILED
    assert result.receipts[0].outcome is PurgeTargetOutcome.FAILED
    assert result.receipts[0].error_code in {
        "PURGE_ADAPTER_UNAVAILABLE",
        "PURGE_TARGET_FAILED",
        "PURGE_RECEIPT_INVALID",
    }
    assert marker not in repr(result)


@pytest.mark.asyncio
async def test_mixed_target_outcomes_are_partial_failure() -> None:
    database = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    coordinator = PurgeCoordinator(adapters=(database,))

    result = await coordinator.execute(
        plan(target(1), target(2, kind=PurgeTargetKind.OBJECT_STORAGE_OBJECT))
    )

    assert result.status is PurgeRunStatus.PARTIAL_FAILURE
    assert [receipt.outcome for receipt in result.receipts] == [
        PurgeTargetOutcome.DELETED,
        PurgeTargetOutcome.FAILED,
    ]


def test_coordinator_rejects_duplicate_or_invalid_adapter_kinds() -> None:
    database = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    with pytest.raises(ValueError, match="unique"):
        PurgeCoordinator(adapters=(database, database))

    invalid = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    invalid.kind = cast(PurgeTargetKind, "DATABASE_RECORD")
    with pytest.raises(TypeError, match="kind"):
        PurgeCoordinator(adapters=(invalid,))

    with pytest.raises(TypeError, match="kind"):
        PurgeCoordinator(adapters=(cast(PurgeTargetAdapter, object()),))


def _metric_points(reader: InMemoryMetricReader, name: str) -> list[Any]:
    data = reader.get_metrics_data()
    assert data is not None
    return [
        point
        for resource_metrics in data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
        if metric.name == name
        for point in metric.data.data_points
    ]


@pytest.mark.asyncio
async def test_failure_telemetry_is_bounded_and_contains_no_identifiers_or_locator() -> None:
    marker = "synthetic-sensitive-locator"
    reader = InMemoryMetricReader()
    runtime = create_observability_runtime(ObservabilitySettings(), metric_reader=reader)
    telemetry = PurgeTelemetry.from_meter(runtime.meter)
    coordinator = PurgeCoordinator(adapters=(), observer=telemetry)

    result = await coordinator.execute(plan(target(locator=marker)))

    outcome_points = _metric_points(reader, PURGE_TARGET_OUTCOMES)
    failure_points = _metric_points(reader, PURGE_FAILURES)
    serialized = repr((outcome_points, failure_points))
    assert result.status is PurgeRunStatus.FAILED
    assert len(outcome_points) == 1
    assert len(failure_points) == 1
    assert marker not in serialized
    assert str(result.plan_id) not in serialized
    assert str(target().identity.target_id) not in serialized
    assert set(outcome_points[0].attributes) == {"target.kind", "purge.outcome"}
    assert set(failure_points[0].attributes) == {"target.kind", "error.code"}


@pytest.mark.asyncio
async def test_observer_failure_does_not_reclassify_completed_irreversible_work() -> None:
    class FailingObserver:
        def record(self, receipt: PurgeTargetReceipt) -> None:
            raise RuntimeError("synthetic-sensitive-observer-detail")

    adapter = SyntheticAdapter(PurgeTargetKind.DATABASE_RECORD)
    coordinator = PurgeCoordinator(adapters=(adapter,), observer=FailingObserver())

    result = await coordinator.execute(plan(target()))

    assert result.status is PurgeRunStatus.COMPLETED
    assert result.receipts[0].outcome is PurgeTargetOutcome.DELETED
    assert len(adapter.calls) == 1
    assert "synthetic-sensitive-observer-detail" not in repr(result)


def test_restore_reconciliation_reblocks_tombstoned_generations_and_reviews_others() -> None:
    identity = target().identity
    tombstone = PurgeTombstone(
        identity=identity,
        purged_through_generation=3,
        purged_at=NOW,
        policy_code=PolicyCode("platform.retention"),
        policy_version=PolicyVersion("v1"),
    )
    reconciler = RestoreReconciler(tombstones=(tombstone,))

    old = reconciler.classify(RestoredTarget(identity=identity, generation=2, restored_at=NOW))
    same = reconciler.classify(RestoredTarget(identity=identity, generation=3, restored_at=NOW))
    newer = reconciler.classify(RestoredTarget(identity=identity, generation=4, restored_at=NOW))
    unmatched = reconciler.classify(
        RestoredTarget(identity=target(9).identity, generation=1, restored_at=NOW)
    )

    assert old.disposition is RestoreDisposition.REBLOCK_AND_REPURGE
    assert same.disposition is RestoreDisposition.REBLOCK_AND_REPURGE
    assert newer.disposition is RestoreDisposition.REVIEW_REQUIRED
    assert unmatched.disposition is RestoreDisposition.REVIEW_REQUIRED


def test_restore_direct_constructors_reject_invalid_values() -> None:
    identity = target().identity
    with pytest.raises(ValueError, match="timezone-aware"):
        PurgeTombstone(
            identity=identity,
            purged_through_generation=1,
            purged_at=datetime(2026, 1, 1),
            policy_code=PolicyCode("platform.retention"),
            policy_version=PolicyVersion("v1"),
        )
    with pytest.raises(ValueError, match="positive"):
        RestoredTarget(identity=identity, generation=0, restored_at=NOW)
    with pytest.raises(TypeError, match="RestoreDisposition"):
        RestoreDecision(
            target=RestoredTarget(identity=identity, generation=1, restored_at=NOW),
            disposition="REVIEW_REQUIRED",  # type: ignore[arg-type]
        )
