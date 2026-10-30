"""Bounded optional dependency execution with honest degraded outcomes."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import TypeVar, cast

from app.resilience.contracts import (
    CapabilityControlState,
    DependencyFailure,
    DependencyFailureKind,
    DependencyOutcome,
    DependencyOutcomeState,
    OptionalCapability,
    ResilienceFailureCode,
    ResilienceObserver,
    RetryPolicy,
)
from app.resilience.switchboard import OptionalCapabilitySwitchboard

T = TypeVar("T")
BASE_RETRY_DELAY_SECONDS = 0.01
MAX_RETRY_DELAY_SECONDS = 0.05

_FAILURE_CODES = {
    DependencyFailureKind.TIMEOUT: ResilienceFailureCode.DEPENDENCY_TIMEOUT,
    DependencyFailureKind.UNAVAILABLE: ResilienceFailureCode.DEPENDENCY_UNAVAILABLE,
    DependencyFailureKind.RATE_LIMITED: ResilienceFailureCode.DEPENDENCY_RATE_LIMITED,
    DependencyFailureKind.REJECTED: ResilienceFailureCode.DEPENDENCY_REJECTED,
    DependencyFailureKind.INVALID_RESPONSE: ResilienceFailureCode.DEPENDENCY_INVALID_RESPONSE,
    DependencyFailureKind.UNKNOWN: ResilienceFailureCode.DEPENDENCY_UNKNOWN,
}
_TRANSIENT_FAILURES = frozenset(
    {
        DependencyFailureKind.TIMEOUT,
        DependencyFailureKind.UNAVAILABLE,
        DependencyFailureKind.RATE_LIMITED,
    }
)


class OptionalDependencyExecutor:
    """Execute optional work without owning policy, authorization, or fallback content."""

    def __init__(
        self,
        *,
        switchboard: OptionalCapabilitySwitchboard,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
        observer: ResilienceObserver | None = None,
    ) -> None:
        if not isinstance(switchboard, OptionalCapabilitySwitchboard):
            raise TypeError("switchboard must be an OptionalCapabilitySwitchboard")
        self._switchboard = switchboard
        self._sleeper = sleeper
        self._observer = observer

    async def execute(
        self,
        capability: OptionalCapability,
        *,
        policy: RetryPolicy,
        operation: Callable[[], Awaitable[T]],
    ) -> DependencyOutcome[T]:
        """Return success or a closed degraded result within the total deadline."""
        if not isinstance(capability, OptionalCapability):
            raise TypeError("capability must be an OptionalCapability")
        if not isinstance(policy, RetryPolicy):
            raise TypeError("policy must be a RetryPolicy")
        if not callable(operation):
            raise TypeError("operation must be callable")
        if self._switchboard.snapshot(capability).state is not CapabilityControlState.AVAILABLE:
            return self._record(self._disabled(capability, attempts=0))

        loop = asyncio.get_running_loop()
        deadline = loop.time() + policy.total_timeout_seconds
        attempts = 0
        while attempts <= policy.retry_budget:
            if self._switchboard.snapshot(capability).state is not CapabilityControlState.AVAILABLE:
                return self._record(self._disabled(capability, attempts=attempts))
            remaining = deadline - loop.time()
            if remaining <= 0:
                return self._record(
                    self._failure(capability, attempts, DependencyFailureKind.TIMEOUT)
                )
            attempts += 1
            try:
                value = await asyncio.wait_for(
                    operation(), timeout=min(policy.attempt_timeout_seconds, remaining)
                )
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                failure = DependencyFailure(DependencyFailureKind.TIMEOUT, retryable=True)
            except DependencyFailure as error:
                failure = error
            except Exception:
                failure = DependencyFailure(DependencyFailureKind.UNKNOWN, retryable=False)
            else:
                if (
                    self._switchboard.snapshot(capability).state
                    is not CapabilityControlState.AVAILABLE
                ):
                    return self._record(self._disabled(capability, attempts=attempts))
                if value is None:
                    return self._record(
                        self._failure(capability, attempts, DependencyFailureKind.INVALID_RESPONSE)
                    )
                return self._record(
                    DependencyOutcome(
                        capability=capability,
                        state=DependencyOutcomeState.SUCCEEDED,
                        attempts=attempts,
                        value=value,
                    )
                )

            can_retry = (
                failure.retryable
                and failure.kind in _TRANSIENT_FAILURES
                and attempts <= policy.retry_budget
            )
            if not can_retry:
                return self._record(self._failure(capability, attempts, failure.kind))
            remaining = deadline - loop.time()
            delay = min(BASE_RETRY_DELAY_SECONDS * (2 ** (attempts - 1)), MAX_RETRY_DELAY_SECONDS)
            if delay >= remaining:
                return self._record(
                    self._failure(capability, attempts, DependencyFailureKind.TIMEOUT)
                )
            try:
                await asyncio.wait_for(self._sleeper(delay), timeout=remaining)
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                return self._record(
                    self._failure(capability, attempts, DependencyFailureKind.TIMEOUT)
                )
            except Exception:
                return self._record(
                    self._failure(capability, attempts, DependencyFailureKind.UNKNOWN)
                )

        raise AssertionError("bounded optional dependency loop must return")

    @staticmethod
    def _disabled(capability: OptionalCapability, attempts: int) -> DependencyOutcome[T]:
        return DependencyOutcome(
            capability=capability,
            state=DependencyOutcomeState.DEGRADED_DISABLED,
            attempts=attempts,
            failure_code=ResilienceFailureCode.SWITCH_DISABLED,
        )

    @staticmethod
    def _failure(
        capability: OptionalCapability,
        attempts: int,
        kind: DependencyFailureKind,
    ) -> DependencyOutcome[T]:
        return DependencyOutcome(
            capability=capability,
            state=DependencyOutcomeState.DEGRADED_FAILURE,
            attempts=attempts,
            failure_code=_FAILURE_CODES[kind],
        )

    def _record(self, outcome: DependencyOutcome[T]) -> DependencyOutcome[T]:
        if self._observer is not None:
            with suppress(Exception):
                self._observer.record_outcome(cast(DependencyOutcome[object], outcome))
        return outcome
