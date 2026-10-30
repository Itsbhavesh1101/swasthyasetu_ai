from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from app.config import ObservabilitySettings, Settings
from app.main import create_app
from app.resilience import (
    KILL_SWITCH_TRIPS,
    OPTIONAL_DEPENDENCY_OUTCOMES,
    CapabilityControlState,
    CapabilitySwitchSnapshot,
    DependencyFailure,
    DependencyFailureKind,
    DependencyOutcome,
    DependencyOutcomeState,
    KillSwitchReason,
    OptionalCapability,
    OptionalCapabilitySwitchboard,
    OptionalDependencyExecutor,
    ResilienceFailureCode,
    ResilienceTelemetry,
    RetryPolicy,
)
from app.shared.observability import create_observability_runtime

NOW = datetime(2026, 10, 30, 16, 0, tzinfo=UTC)
FAST_POLICY = RetryPolicy(
    attempt_timeout_seconds=0.1,
    total_timeout_seconds=0.3,
    retry_budget=0,
    idempotent=False,
)


def available_board(
    capability: OptionalCapability = OptionalCapability.LLM_GENERATION,
    *,
    observer: object | None = None,
) -> OptionalCapabilitySwitchboard:
    return OptionalCapabilitySwitchboard(
        available=(capability,),
        observer=cast(Any, observer),
    )


@pytest.mark.parametrize(
    ("factory", "error"),
    [
        (
            lambda: RetryPolicy(
                attempt_timeout_seconds=True,
                total_timeout_seconds=1,
            ),
            TypeError,
        ),
        (
            lambda: RetryPolicy(attempt_timeout_seconds=float("inf"), total_timeout_seconds=1),
            ValueError,
        ),
        (
            lambda: RetryPolicy(attempt_timeout_seconds=2, total_timeout_seconds=1),
            ValueError,
        ),
        (
            lambda: RetryPolicy(
                attempt_timeout_seconds=1,
                total_timeout_seconds=2,
                retry_budget=1,
                idempotent=False,
            ),
            ValueError,
        ),
        (
            lambda: CapabilitySwitchSnapshot(
                capability=OptionalCapability.LLM_GENERATION,
                state=CapabilityControlState.TRIPPED,
            ),
            ValueError,
        ),
        (
            lambda: CapabilitySwitchSnapshot(
                capability=OptionalCapability.LLM_GENERATION,
                state=CapabilityControlState.AVAILABLE,
                reason=KillSwitchReason.INCIDENT,
                tripped_at=NOW,
            ),
            ValueError,
        ),
        (
            lambda: DependencyOutcome(
                capability=OptionalCapability.LLM_GENERATION,
                state=DependencyOutcomeState.SUCCEEDED,
                attempts=1,
            ),
            ValueError,
        ),
        (
            lambda: DependencyOutcome(
                capability=OptionalCapability.LLM_GENERATION,
                state=DependencyOutcomeState.DEGRADED_FAILURE,
                attempts=1,
                failure_code=ResilienceFailureCode.SWITCH_DISABLED,
            ),
            ValueError,
        ),
        (
            lambda: DependencyOutcome(
                capability=OptionalCapability.LLM_GENERATION,
                state=DependencyOutcomeState.DEGRADED_DISABLED,
                attempts=0,
                failure_code=ResilienceFailureCode.DEPENDENCY_UNKNOWN,
            ),
            ValueError,
        ),
        (
            lambda: DependencyFailure(
                "TIMEOUT",  # type: ignore[arg-type]
                retryable=True,
            ),
            TypeError,
        ),
    ],
)
def test_direct_constructors_reject_invalid_state(
    factory: Callable[[], object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        factory()


def test_switch_timestamp_normalizes_to_utc_and_trip_is_idempotent() -> None:
    board = available_board()
    offset = timezone(timedelta(hours=5, minutes=30))

    first = board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.INCIDENT,
        tripped_at=NOW.astimezone(offset),
    )
    second = board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.MANUAL_SAFETY,
        tripped_at=NOW + timedelta(hours=1),
    )

    assert first is second
    assert first.reason is KillSwitchReason.INCIDENT
    assert first.tripped_at == NOW
    assert first.tripped_at is not None and first.tripped_at.tzinfo is UTC


def test_naive_trip_timestamp_is_rejected_without_mutating_switch() -> None:
    board = available_board()

    with pytest.raises(ValueError, match="timezone-aware"):
        board.trip(
            OptionalCapability.LLM_GENERATION,
            reason=KillSwitchReason.INCIDENT,
            tripped_at=datetime(2026, 10, 30, 16, 0),
        )

    assert (
        board.snapshot(OptionalCapability.LLM_GENERATION).state is CapabilityControlState.AVAILABLE
    )


def test_switchboard_rejects_duplicate_or_invalid_available_capabilities() -> None:
    with pytest.raises(ValueError, match="unique"):
        OptionalCapabilitySwitchboard(
            available=(OptionalCapability.OCR_PROCESSING, OptionalCapability.OCR_PROCESSING)
        )
    with pytest.raises(TypeError, match="OptionalCapability"):
        OptionalCapabilitySwitchboard(
            available=cast(tuple[OptionalCapability, ...], ("OCR_PROCESSING",))
        )


def test_resilience_foundation_has_no_reset_or_runtime_registration() -> None:
    board = available_board()
    application = create_app(Settings(_env_file=None))

    assert not hasattr(board, "reset")
    assert "resilience" not in application.state.module_registry.module_ids


@pytest.mark.asyncio
@pytest.mark.parametrize("capability", list(OptionalCapability))
async def test_every_optional_capability_is_disabled_by_default_without_calling_dependency(
    capability: OptionalCapability,
) -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        return "must-not-run"

    outcome = await OptionalDependencyExecutor(switchboard=OptionalCapabilitySwitchboard()).execute(
        capability, policy=FAST_POLICY, operation=operation
    )

    assert outcome == DependencyOutcome(
        capability=capability,
        state=DependencyOutcomeState.DEGRADED_DISABLED,
        attempts=0,
        failure_code=ResilienceFailureCode.SWITCH_DISABLED,
    )
    assert calls == 0


@pytest.mark.asyncio
async def test_available_synthetic_capability_succeeds_without_value_in_repr() -> None:
    marker = "synthetic-sensitive-provider-value"
    executor = OptionalDependencyExecutor(switchboard=available_board())

    outcome = await executor.execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=lambda: _return(marker),
    )

    assert outcome.state is DependencyOutcomeState.SUCCEEDED
    assert outcome.value == marker
    assert outcome.attempts == 1
    assert marker not in repr(outcome)


async def _return(value: str) -> str:
    return value


@pytest.mark.asyncio
async def test_trip_prevents_future_dependency_call() -> None:
    board = available_board()
    board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.MANUAL_SAFETY,
        tripped_at=NOW,
    )
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        return "not-called"

    outcome = await OptionalDependencyExecutor(switchboard=board).execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=operation,
    )

    assert outcome.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert calls == 0


@pytest.mark.asyncio
async def test_trip_during_in_flight_call_discards_late_result() -> None:
    board = available_board()
    started = asyncio.Event()
    release = asyncio.Event()

    async def operation() -> str:
        started.set()
        await release.wait()
        return "synthetic-late-result"

    task = asyncio.create_task(
        OptionalDependencyExecutor(switchboard=board).execute(
            OptionalCapability.LLM_GENERATION,
            policy=FAST_POLICY,
            operation=operation,
        )
    )
    await started.wait()
    board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.INCIDENT,
        tripped_at=NOW,
    )
    release.set()
    outcome = await task

    assert outcome.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert outcome.attempts == 1
    assert outcome.value is None
    assert "synthetic-late-result" not in repr(outcome)


@pytest.mark.asyncio
async def test_transient_idempotent_failure_retries_then_succeeds() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise DependencyFailure(DependencyFailureKind.UNAVAILABLE, retryable=True)
        return "synthetic-success"

    async def no_wait(_: float) -> None:
        return None

    outcome = await OptionalDependencyExecutor(
        switchboard=available_board(), sleeper=no_wait
    ).execute(
        OptionalCapability.LLM_GENERATION,
        policy=RetryPolicy(
            attempt_timeout_seconds=0.1,
            total_timeout_seconds=0.3,
            retry_budget=1,
            idempotent=True,
        ),
        operation=operation,
    )

    assert outcome.state is DependencyOutcomeState.SUCCEEDED
    assert outcome.attempts == 2
    assert attempts == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("kind", "retryable", "expected"),
    [
        (
            DependencyFailureKind.UNAVAILABLE,
            False,
            ResilienceFailureCode.DEPENDENCY_UNAVAILABLE,
        ),
        (
            DependencyFailureKind.RATE_LIMITED,
            False,
            ResilienceFailureCode.DEPENDENCY_RATE_LIMITED,
        ),
        (DependencyFailureKind.REJECTED, True, ResilienceFailureCode.DEPENDENCY_REJECTED),
        (
            DependencyFailureKind.INVALID_RESPONSE,
            True,
            ResilienceFailureCode.DEPENDENCY_INVALID_RESPONSE,
        ),
    ],
)
async def test_terminal_or_adapter_nonretryable_failures_are_not_retried(
    kind: DependencyFailureKind,
    retryable: bool,
    expected: ResilienceFailureCode,
) -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        raise DependencyFailure(kind, retryable=retryable)

    outcome = await OptionalDependencyExecutor(switchboard=available_board()).execute(
        OptionalCapability.LLM_GENERATION,
        policy=RetryPolicy(
            attempt_timeout_seconds=0.1,
            total_timeout_seconds=0.3,
            retry_budget=2,
            idempotent=True,
        ),
        operation=operation,
    )

    assert outcome.state is DependencyOutcomeState.DEGRADED_FAILURE
    assert outcome.failure_code is expected
    assert outcome.attempts == 1
    assert calls == 1


@pytest.mark.asyncio
async def test_timeout_is_bounded_and_cancels_dependency_operation() -> None:
    cancelled = asyncio.Event()

    async def operation() -> str:
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()
        return "unreachable"

    outcome = await OptionalDependencyExecutor(switchboard=available_board()).execute(
        OptionalCapability.LLM_GENERATION,
        policy=RetryPolicy(
            attempt_timeout_seconds=0.01,
            total_timeout_seconds=0.02,
            retry_budget=0,
            idempotent=False,
        ),
        operation=operation,
    )

    assert outcome.failure_code is ResilienceFailureCode.DEPENDENCY_TIMEOUT
    assert outcome.attempts == 1
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_total_deadline_bounds_retry_and_backoff_work() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(60)
        return "unreachable"

    loop = asyncio.get_running_loop()
    started = loop.time()
    outcome = await OptionalDependencyExecutor(switchboard=available_board()).execute(
        OptionalCapability.LLM_GENERATION,
        policy=RetryPolicy(
            attempt_timeout_seconds=0.02,
            total_timeout_seconds=0.03,
            retry_budget=3,
            idempotent=True,
        ),
        operation=operation,
    )
    elapsed = loop.time() - started

    assert outcome.failure_code is ResilienceFailureCode.DEPENDENCY_TIMEOUT
    assert outcome.attempts == 1
    assert calls == 1
    assert elapsed < 0.2


@pytest.mark.asyncio
async def test_unknown_exception_and_none_result_fail_closed_without_raw_detail() -> None:
    marker = "synthetic-sensitive-exception-detail"

    async def broken() -> str:
        raise RuntimeError(marker)

    executor = OptionalDependencyExecutor(switchboard=available_board())
    broken_outcome = await executor.execute(
        OptionalCapability.LLM_GENERATION, policy=FAST_POLICY, operation=broken
    )
    none_outcome = await executor.execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=cast(Callable[[], Awaitable[str]], lambda: _return_none()),
    )

    assert broken_outcome.failure_code is ResilienceFailureCode.DEPENDENCY_UNKNOWN
    assert marker not in repr(broken_outcome)
    assert none_outcome.failure_code is ResilienceFailureCode.DEPENDENCY_INVALID_RESPONSE


async def _return_none() -> None:
    return None


@pytest.mark.asyncio
async def test_retry_sleeper_failure_is_generic_and_stops_retry() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        raise DependencyFailure(DependencyFailureKind.UNAVAILABLE, retryable=True)

    async def broken_sleeper(_: float) -> None:
        raise RuntimeError("synthetic-sensitive-sleeper-detail")

    outcome = await OptionalDependencyExecutor(
        switchboard=available_board(), sleeper=broken_sleeper
    ).execute(
        OptionalCapability.LLM_GENERATION,
        policy=RetryPolicy(
            attempt_timeout_seconds=0.1,
            total_timeout_seconds=0.3,
            retry_budget=1,
            idempotent=True,
        ),
        operation=operation,
    )

    assert outcome.failure_code is ResilienceFailureCode.DEPENDENCY_UNKNOWN
    assert outcome.attempts == 1
    assert calls == 1
    assert "synthetic-sensitive-sleeper-detail" not in repr(outcome)


@pytest.mark.asyncio
async def test_cancellation_propagates_instead_of_becoming_degraded_success() -> None:
    async def cancelled() -> str:
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await OptionalDependencyExecutor(switchboard=available_board()).execute(
            OptionalCapability.LLM_GENERATION,
            policy=FAST_POLICY,
            operation=cancelled,
        )


@pytest.mark.asyncio
async def test_core_fallback_remains_caller_owned_and_usable_after_optional_failure() -> None:
    fallback_calls = 0

    async def unavailable() -> str:
        raise DependencyFailure(DependencyFailureKind.UNAVAILABLE, retryable=False)

    outcome = await OptionalDependencyExecutor(switchboard=available_board()).execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=unavailable,
    )
    if outcome.state is not DependencyOutcomeState.SUCCEEDED:
        fallback_calls += 1

    assert outcome.state is DependencyOutcomeState.DEGRADED_FAILURE
    assert fallback_calls == 1


class FailingObserver:
    def record_switch(self, snapshot: CapabilitySwitchSnapshot) -> None:
        raise RuntimeError("synthetic-sensitive-observer-detail")

    def record_outcome(self, outcome: DependencyOutcome[object]) -> None:
        raise RuntimeError("synthetic-sensitive-observer-detail")


@pytest.mark.asyncio
async def test_observer_failure_cannot_block_trip_or_relabel_dependency_result() -> None:
    observer = FailingObserver()
    board = available_board(observer=observer)
    snapshot = board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.INCIDENT,
        tripped_at=NOW,
    )
    outcome = await OptionalDependencyExecutor(switchboard=board, observer=observer).execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=lambda: _return("not-called"),
    )

    assert snapshot.state is CapabilityControlState.TRIPPED
    assert outcome.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert "synthetic-sensitive-observer-detail" not in repr((snapshot, outcome))


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
async def test_telemetry_uses_exact_bounded_attribute_allowlists() -> None:
    reader = InMemoryMetricReader()
    runtime = create_observability_runtime(ObservabilitySettings(), metric_reader=reader)
    telemetry = ResilienceTelemetry.from_meter(runtime.meter)
    board = available_board(observer=telemetry)
    executor = OptionalDependencyExecutor(switchboard=board, observer=telemetry)

    board.trip(
        OptionalCapability.LLM_GENERATION,
        reason=KillSwitchReason.INCIDENT,
        tripped_at=NOW,
    )
    outcome = await executor.execute(
        OptionalCapability.LLM_GENERATION,
        policy=FAST_POLICY,
        operation=lambda: _return("synthetic-sensitive-payload"),
    )

    switch_points = _metric_points(reader, KILL_SWITCH_TRIPS)
    outcome_points = _metric_points(reader, OPTIONAL_DEPENDENCY_OUTCOMES)
    assert outcome.state is DependencyOutcomeState.DEGRADED_DISABLED
    assert len(switch_points) == 1
    assert len(outcome_points) == 1
    assert set(switch_points[0].attributes) == {
        "capability",
        "switch.state",
        "switch.reason",
    }
    assert set(outcome_points[0].attributes) == {
        "capability",
        "outcome.state",
        "failure.code",
    }
    assert "synthetic-sensitive-payload" not in repr((switch_points, outcome_points))
