"""Bounded in-process orchestration over the provider-neutral LLM port."""

import asyncio
import math
from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import UTC, datetime
from typing import Final, Protocol

from app.modules.ai_orchestration.contracts import (
    ContractValidationError,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import (
    LLMFailureCategory,
    LLMProvider,
    OrchestrationOutcome,
    ProviderFailure,
    ProviderHealth,
)

MAX_TOTAL_DEADLINE_SECONDS: Final = 30.0
BASE_RETRY_DELAY_SECONDS: Final = 0.05
MAX_RETRY_DELAY_SECONDS: Final = 0.25


class _RetrySleeperError(Exception):
    """Content-free marker for an unexpected injected sleeper failure."""


class OrchestrationTelemetry(Protocol):
    """Content-free telemetry hook implemented with the shared OTel runtime."""

    def record(
        self,
        request: StructuredLLMRequest,
        *,
        provider_id: str,
        attempt_count: int,
        result: StructuredLLMResult | None,
        failure: LLMFailureCategory | None,
    ) -> None: ...


class NoOpOrchestrationTelemetry:
    """Explicit no-op used when telemetry is not supplied to a unit composition."""

    def record(
        self,
        request: StructuredLLMRequest,
        *,
        provider_id: str,
        attempt_count: int,
        result: StructuredLLMResult | None,
        failure: LLMFailureCategory | None,
    ) -> None:
        del request, provider_id, attempt_count, result, failure


class AIOrchestrationService:
    """Apply total-deadline and retry policy without task or clinical authority."""

    def __init__(
        self,
        *,
        provider: LLMProvider,
        clock: Callable[[], datetime] | None = None,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
        telemetry: OrchestrationTelemetry | None = None,
    ) -> None:
        self._provider = provider
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sleeper = sleeper
        self._telemetry = telemetry or NoOpOrchestrationTelemetry()

    def health(self) -> ProviderHealth:
        """Return adapter state without making a model/network request."""
        return self._provider.health()

    async def generate_structured(self, request: StructuredLLMRequest) -> OrchestrationOutcome:
        """Generate a candidate or a closed, normalized failure."""
        now = self._utc_now()
        initial_remaining = (request.deadline_at - now).total_seconds()
        if request.attempt != 1 or initial_remaining > MAX_TOTAL_DEADLINE_SECONDS:
            return self._failure(
                request,
                LLMFailureCategory.SCHEMA_INVALID,
                attempt_count=0,
                retryable=False,
            )
        if initial_remaining <= 0:
            return self._failure(
                request,
                LLMFailureCategory.TIMEOUT,
                attempt_count=0,
                retryable=False,
            )

        for attempt in range(1, request.retry_budget + 2):
            remaining = (request.deadline_at - self._utc_now()).total_seconds()
            if remaining <= 0:
                return self._failure(
                    request,
                    LLMFailureCategory.TIMEOUT,
                    attempt_count=max(0, attempt - 1),
                    retryable=False,
                )
            attempted_request = replace(request, attempt=attempt)
            try:
                result = await asyncio.wait_for(
                    self._provider.generate_structured(attempted_request), timeout=remaining
                )
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                provider_failure = ProviderFailure(LLMFailureCategory.TIMEOUT, retryable=True)
            except ProviderFailure as error:
                provider_failure = error
            except ContractValidationError:
                return self._failure(
                    request,
                    LLMFailureCategory.SCHEMA_INVALID,
                    attempt_count=attempt,
                    retryable=False,
                )
            except Exception:
                return self._failure(
                    request,
                    LLMFailureCategory.UNKNOWN,
                    attempt_count=attempt,
                    retryable=False,
                )
            else:
                if (request.deadline_at - self._utc_now()).total_seconds() <= 0:
                    return self._failure(
                        request,
                        LLMFailureCategory.TIMEOUT,
                        attempt_count=attempt,
                        retryable=False,
                    )
                if not self._result_matches(attempted_request, result):
                    return self._failure(
                        request,
                        LLMFailureCategory.SCHEMA_INVALID,
                        attempt_count=attempt,
                        retryable=False,
                    )
                self._record_telemetry(
                    request,
                    provider_id=self._provider.provider_id,
                    attempt_count=attempt,
                    result=result,
                    failure=None,
                )
                return OrchestrationOutcome.success(result)

            can_retry = provider_failure.retryable and attempt <= request.retry_budget
            if not can_retry:
                return self._failure(
                    request,
                    provider_failure.category,
                    attempt_count=attempt,
                    retryable=False,
                    diagnostic_code=provider_failure.diagnostic_code,
                )
            if (
                provider_failure.retry_after_seconds is not None
                and provider_failure.retry_after_seconds > MAX_RETRY_DELAY_SECONDS
            ):
                return self._failure(
                    request,
                    provider_failure.category,
                    attempt_count=attempt,
                    retryable=False,
                    diagnostic_code=provider_failure.diagnostic_code,
                )
            delay = self._retry_delay(attempt, provider_failure)
            remaining = (request.deadline_at - self._utc_now()).total_seconds()
            if delay >= remaining:
                return self._failure(
                    request,
                    LLMFailureCategory.TIMEOUT,
                    attempt_count=attempt,
                    retryable=False,
                )
            try:
                await asyncio.wait_for(self._sleep_for_retry(delay), timeout=remaining)
            except asyncio.CancelledError:
                raise
            except TimeoutError:
                return self._failure(
                    request,
                    LLMFailureCategory.TIMEOUT,
                    attempt_count=attempt,
                    retryable=False,
                )
            except _RetrySleeperError:
                return self._failure(
                    request,
                    LLMFailureCategory.UNKNOWN,
                    attempt_count=attempt,
                    retryable=False,
                )
            if (request.deadline_at - self._utc_now()).total_seconds() <= 0:
                return self._failure(
                    request,
                    LLMFailureCategory.TIMEOUT,
                    attempt_count=attempt,
                    retryable=False,
                )

        raise AssertionError("bounded attempt loop must return")

    def _utc_now(self) -> datetime:
        current = self._clock()
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("orchestration clock must return an aware datetime")
        return current.astimezone(UTC)

    async def _sleep_for_retry(self, delay: float) -> None:
        try:
            await self._sleeper(delay)
        except asyncio.CancelledError:
            raise
        except Exception:
            raise _RetrySleeperError from None

    @staticmethod
    def _retry_delay(attempt: int, failure: ProviderFailure) -> float:
        if failure.retry_after_seconds is not None:
            return failure.retry_after_seconds
        exponential_delay = BASE_RETRY_DELAY_SECONDS * float(2 ** (attempt - 1))
        return min(exponential_delay, MAX_RETRY_DELAY_SECONDS)

    def _failure(
        self,
        request: StructuredLLMRequest,
        category: LLMFailureCategory,
        *,
        attempt_count: int,
        retryable: bool,
        diagnostic_code: str | None = None,
    ) -> OrchestrationOutcome:
        self._record_telemetry(
            request,
            provider_id=self._provider.provider_id,
            attempt_count=attempt_count,
            result=None,
            failure=category,
        )
        return OrchestrationOutcome.failure_outcome(
            category=category,
            operation_id=request.operation_id,
            request_id=request.request_id,
            attempt_count=attempt_count,
            retryable=retryable,
            diagnostic_code=diagnostic_code,
        )

    def _record_telemetry(
        self,
        request: StructuredLLMRequest,
        *,
        provider_id: str,
        attempt_count: int,
        result: StructuredLLMResult | None,
        failure: LLMFailureCategory | None,
    ) -> None:
        try:
            self._telemetry.record(
                request,
                provider_id=provider_id,
                attempt_count=attempt_count,
                result=result,
                failure=failure,
            )
        except Exception:
            # Instrumentation is optional and cannot alter generation behavior.
            return

    def _result_matches(self, request: StructuredLLMRequest, result: object) -> bool:
        if not isinstance(result, StructuredLLMResult):
            return False
        try:
            validated_result = StructuredLLMResult.from_dict(result.to_dict())
            return (
                validated_result == result
                and result.request_id == request.request_id
                and result.operation_id == request.operation_id
                and result.request_contract_version == request.request_contract_version
                and result.schema_id == request.schema_id
                and result.schema_version == request.schema_version
                and result.prompt_id == request.prompt_id
                and result.prompt_version == request.prompt_version
                and result.provider_id == self._provider.provider_id
                and result.attempt_count == request.attempt
                and result.provenance.schema_id == request.schema_id
                and result.provenance.schema_version == request.schema_version
                and result.provenance.prompt_id == request.prompt_id
                and result.provenance.prompt_version == request.prompt_version
                and result.provenance.provider_id == result.provider_id
                and result.provenance.provider_model_id == result.provider_model_id
                and result.provenance.provider_model_version == result.provider_model_version
                and result.provenance.source_references == request.provenance_context
                and result.raw_retained is False
                and math.isfinite(result.latency_ms)
            )
        except Exception:
            # Provider-returned objects and their diagnostics must never cross this boundary.
            return False
