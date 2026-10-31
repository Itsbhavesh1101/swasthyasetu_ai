"""Cross-boundary, synthetic-only P22 security regression evidence."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.resilience import (
    DependencyOutcomeState,
    KillSwitchReason,
    OptionalCapability,
    OptionalCapabilitySwitchboard,
    OptionalDependencyExecutor,
    ResilienceFailureCode,
    RetryPolicy,
)
from app.retention import (
    PolicyCode,
    PolicyVersion,
    PurgeAuthorization,
    PurgeAuthorizationDecision,
    PurgeCoordinator,
    PurgePlan,
    PurgeRunStatus,
    PurgeTarget,
    PurgeTargetIdentity,
    PurgeTargetKind,
    PurgeTargetOutcome,
    PurgeTargetReceipt,
    PurgeTombstone,
    RestoreDisposition,
    RestoredTarget,
    RestoreReconciler,
)
from app.shared.rate_limits import RateLimitDecision, RateLimitSubject
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
FAST_POLICY = RetryPolicy(
    attempt_timeout_seconds=0.1,
    total_timeout_seconds=0.2,
    retry_budget=0,
    idempotent=False,
)


def opaque(value: int) -> OpaqueId:
    return OpaqueId(UUID(int=value))


def purge_target(*, locator: str = "synthetic/opaque/locator") -> PurgeTarget:
    return PurgeTarget(
        identity=PurgeTargetIdentity(
            kind=PurgeTargetKind.DATABASE_RECORD,
            target_id=opaque(1),
        ),
        generation=2,
        locator=locator,
    )


def purge_plan(
    decision: PurgeAuthorizationDecision,
    *,
    holds: tuple[str, ...] = (),
    locator: str = "synthetic/opaque/locator",
) -> PurgePlan:
    return PurgePlan(
        plan_id=opaque(2),
        subject_id=opaque(3),
        requested_at=NOW,
        authorization=PurgeAuthorization(
            decision=decision,
            policy_code=PolicyCode("platform.retention"),
            policy_version=PolicyVersion("synthetic-v1"),
            evaluated_at=NOW,
            hold_references=holds,
        ),
        targets=(purge_target(locator=locator),),
    )


class FailingLimiter:
    def __init__(self, marker: str) -> None:
        self.marker = marker
        self.calls = 0

    async def check(self, subjects: Sequence[RateLimitSubject]) -> RateLimitDecision:
        self.calls += 1
        raise RuntimeError(self.marker)


class RecordingPurgeAdapter:
    kind = PurgeTargetKind.DATABASE_RECORD

    def __init__(self, *, failure_marker: str | None = None) -> None:
        self.failure_marker = failure_marker
        self.calls = 0

    async def purge(self, target: PurgeTarget) -> PurgeTargetReceipt:
        self.calls += 1
        if self.failure_marker is not None:
            raise RuntimeError(self.failure_marker)
        return PurgeTargetReceipt(target=target, outcome=PurgeTargetOutcome.DELETED)


@pytest.mark.asyncio
async def test_abuse_control_failure_blocks_route_work_and_sanitizes_response() -> None:
    marker = "synthetic-sensitive-limiter-canary"
    limiter = FailingLimiter(marker)
    route_calls = 0
    router = APIRouter()

    @router.post("/synthetic-sensitive-operation")
    async def synthetic_sensitive_operation() -> dict[str, bool]:
        nonlocal route_calls
        route_calls += 1
        return {"executed": True}

    application = create_app(
        Settings(_env_file=None),
        api_v1_routers=(router,),
        module_registrations=(),
        rate_limiter=limiter,
    )
    async with AsyncClient(
        transport=ASGITransport(app=application),
        base_url="https://test",
    ) as client:
        response = await client.post("/api/v1/synthetic-sensitive-operation")

    assert limiter.calls == 1
    assert route_calls == 0
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "PROCESSING_FAILED"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"].startswith("default-src 'none'")
    assert marker not in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("decision", "holds"),
    [
        (PurgeAuthorizationDecision.NOT_AUTHORIZED, ()),
        (PurgeAuthorizationDecision.BLOCKED_BY_HOLD, ("synthetic-hold",)),
    ],
)
async def test_control_planes_do_not_cross_authorize_downstream_work(
    decision: PurgeAuthorizationDecision,
    holds: tuple[str, ...],
) -> None:
    adapter = RecordingPurgeAdapter()
    board = OptionalCapabilitySwitchboard(available=(OptionalCapability.LLM_GENERATION,))

    purge_result = await PurgeCoordinator(adapters=(adapter,)).execute(
        purge_plan(decision, holds=holds)
    )
    optional_calls = 0

    async def disabled_operation() -> str:
        nonlocal optional_calls
        optional_calls += 1
        return "must-not-run"

    dependency_result = await OptionalDependencyExecutor(switchboard=board).execute(
        OptionalCapability.OCR_PROCESSING,
        policy=FAST_POLICY,
        operation=disabled_operation,
    )

    assert purge_result.status is PurgeRunStatus.BLOCKED
    assert adapter.calls == 0
    assert dependency_result.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert dependency_result.failure_code is ResilienceFailureCode.SWITCH_DISABLED
    assert optional_calls == 0


@pytest.mark.asyncio
async def test_authorized_purge_does_not_enable_optional_capability() -> None:
    adapter = RecordingPurgeAdapter()
    board = OptionalCapabilitySwitchboard()
    dependency_calls = 0

    async def dependency_operation() -> str:
        nonlocal dependency_calls
        dependency_calls += 1
        return "must-not-run"

    purge_result = await PurgeCoordinator(adapters=(adapter,)).execute(
        purge_plan(PurgeAuthorizationDecision.AUTHORIZED)
    )
    dependency_result = await OptionalDependencyExecutor(switchboard=board).execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=dependency_operation,
    )

    assert purge_result.status is PurgeRunStatus.COMPLETED
    assert adapter.calls == 1
    assert dependency_result.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert dependency_calls == 0


@pytest.mark.asyncio
async def test_trip_discards_late_result_while_restore_stays_reblocked() -> None:
    board = OptionalCapabilitySwitchboard(available=(OptionalCapability.OCR_PROCESSING,))
    started = asyncio.Event()
    release = asyncio.Event()
    marker = "synthetic-sensitive-late-result"

    async def operation() -> str:
        started.set()
        await release.wait()
        return marker

    task = asyncio.create_task(
        OptionalDependencyExecutor(switchboard=board).execute(
            OptionalCapability.OCR_PROCESSING,
            policy=FAST_POLICY,
            operation=operation,
        )
    )
    await started.wait()
    board.trip(
        OptionalCapability.OCR_PROCESSING,
        reason=KillSwitchReason.INCIDENT,
        tripped_at=NOW,
    )
    release.set()
    dependency_result = await task

    target = purge_target()
    restore_result = RestoreReconciler(
        tombstones=(
            PurgeTombstone(
                identity=target.identity,
                purged_through_generation=target.generation,
                purged_at=NOW,
                policy_code=PolicyCode("platform.retention"),
                policy_version=PolicyVersion("synthetic-v1"),
            ),
        )
    ).classify(
        RestoredTarget(
            identity=target.identity,
            generation=target.generation,
            restored_at=NOW,
        )
    )

    assert dependency_result.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert dependency_result.value is None
    assert marker not in repr(dependency_result)
    assert restore_result.disposition is RestoreDisposition.REBLOCK_AND_REPURGE


@pytest.mark.asyncio
async def test_cross_boundary_failures_expose_only_closed_safe_values() -> None:
    purge_marker = "synthetic-sensitive-purge-exception"
    locator_marker = "synthetic-sensitive-purge-locator"
    dependency_marker = "synthetic-sensitive-dependency-exception"
    adapter = RecordingPurgeAdapter(failure_marker=purge_marker)

    purge_result = await PurgeCoordinator(adapters=(adapter,)).execute(
        purge_plan(
            PurgeAuthorizationDecision.AUTHORIZED,
            locator=locator_marker,
        )
    )

    async def broken_dependency() -> str:
        raise RuntimeError(dependency_marker)

    dependency_result = await OptionalDependencyExecutor(
        switchboard=OptionalCapabilitySwitchboard(available=(OptionalCapability.REFERRAL_DELIVERY,))
    ).execute(
        OptionalCapability.REFERRAL_DELIVERY,
        policy=FAST_POLICY,
        operation=broken_dependency,
    )

    surfaces = repr((purge_result, dependency_result))
    assert purge_result.status is PurgeRunStatus.FAILED
    assert purge_result.receipts[0].error_code == "PURGE_TARGET_FAILED"
    assert dependency_result.failure_code is ResilienceFailureCode.DEPENDENCY_UNKNOWN
    assert purge_marker not in surfaces
    assert locator_marker not in surfaces
    assert dependency_marker not in surfaces


def test_p22_foundations_add_no_automatic_runtime_or_reenable_surface() -> None:
    application = create_app(Settings(_env_file=None), module_registrations=())
    board = OptionalCapabilitySwitchboard()
    coordinator = PurgeCoordinator(adapters=())
    paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }
    module_ids = set(application.state.module_registry.module_ids)

    assert "retention" not in module_ids
    assert "resilience" not in module_ids
    assert all("purge" not in path and "kill-switch" not in path for path in paths)
    assert not hasattr(board, "reset")
    assert not hasattr(board, "enable")
    assert not hasattr(coordinator, "schedule")
    assert not hasattr(coordinator, "start")
