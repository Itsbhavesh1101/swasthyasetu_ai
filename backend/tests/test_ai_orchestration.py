"""P8-A orchestration, deadline, retry, and offline-provider tests."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.adapters.ai.disabled import DisabledLLMProvider
from app.adapters.ai.fake import DeterministicLLMFixture, DeterministicOfflineLLMProvider
from app.modules.ai_orchestration.application import AIOrchestrationService
from app.modules.ai_orchestration.contracts import (
    REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    FinishReason,
    ResultProvenance,
    SourceReference,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import (
    LLMFailureCategory,
    LLMProvider,
    OrchestrationOutcome,
    ProviderFailure,
    ProviderHealthStatus,
    ProviderSafetyClass,
)


class ControlledClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 1, 1, tzinfo=UTC)
        self.delays: list[float] = []

    def now(self) -> datetime:
        return self.current

    async def sleep(self, seconds: float) -> None:
        self.delays.append(seconds)
        self.current += timedelta(seconds=seconds)


def make_request(clock: ControlledClock, *, retry_budget: int = 0) -> StructuredLLMRequest:
    source = SourceReference("source_synthetic_0001", "1", "a" * 64)
    return StructuredLLMRequest(
        operation_id="synthetic.extract",
        language_code="en",
        request_id="req_synthetic_0001",
        request_contract_version=REQUEST_CONTRACT_VERSION,
        schema_id="synthetic_candidate",
        schema_version="1.0.0",
        prompt_id="synthetic_prompt",
        prompt_version="1.0.0",
        input={"message": "synthetic non-clinical fixture"},
        max_output_tokens=256,
        deadline_at=clock.current + timedelta(seconds=5),
        retry_budget=retry_budget,
        attempt=1,
        provider_policy_id="offline_only",
        provider_policy_version="1.0.0",
        provenance_context=(source,),
    )


def make_result(request: StructuredLLMRequest, *, attempt: int = 1) -> StructuredLLMResult:
    return StructuredLLMResult(
        result_contract_version=RESULT_CONTRACT_VERSION,
        request_id=request.request_id,
        operation_id=request.operation_id,
        request_contract_version=request.request_contract_version,
        schema_id=request.schema_id,
        schema_version=request.schema_version,
        prompt_id=request.prompt_id,
        prompt_version=request.prompt_version,
        provider_id="offline_fake",
        provider_model_id="fixture_model",
        provider_model_version="1.0.0",
        provider_request_id="provider_synthetic_0001",
        validated_payload={"candidate": "synthetic-only"},
        finish_reason=FinishReason.STOP,
        usage=None,
        latency_ms=1.0,
        attempt_count=attempt,
        provenance=ResultProvenance(
            schema_id=request.schema_id,
            schema_version=request.schema_version,
            prompt_id=request.prompt_id,
            prompt_version=request.prompt_version,
            provider_id="offline_fake",
            provider_model_id="fixture_model",
            provider_model_version="1.0.0",
            source_references=request.provenance_context,
        ),
    )


def service(
    provider: LLMProvider,
    clock: ControlledClock,
    *,
    sleeper: Callable[[float], Awaitable[None]] | None = None,
) -> AIOrchestrationService:
    return AIOrchestrationService(
        provider=provider,
        clock=clock.now,
        sleeper=sleeper or clock.sleep,
    )


async def test_disabled_provider_is_safe_default_and_fails_closed_without_retry() -> None:
    clock = ControlledClock()
    provider = DisabledLLMProvider()

    outcome = await service(provider, clock).generate_structured(
        make_request(clock, retry_budget=3)
    )

    assert outcome == OrchestrationOutcome.failure_outcome(
        category=LLMFailureCategory.PROVIDER_UNAVAILABLE,
        operation_id="synthetic.extract",
        request_id="req_synthetic_0001",
        attempt_count=1,
        retryable=False,
    )
    assert provider.safety_class is ProviderSafetyClass.SAFE_DEFAULT
    assert provider.health().status is ProviderHealthStatus.DISABLED
    assert clock.delays == []


async def test_offline_fake_is_deterministic_and_uses_no_hidden_variance() -> None:
    clock = ControlledClock()
    request = make_request(clock)
    fixture = DeterministicLLMFixture(request=request, outcomes=(make_result(request),))

    first = await service(DeterministicOfflineLLMProvider((fixture,)), clock).generate_structured(
        request
    )
    second = await service(DeterministicOfflineLLMProvider((fixture,)), clock).generate_structured(
        request
    )

    assert first == second == OrchestrationOutcome.success(make_result(request))
    assert isinstance(DeterministicOfflineLLMProvider((fixture,)), LLMProvider)


@pytest.mark.parametrize(
    "category",
    [
        LLMFailureCategory.TIMEOUT,
        LLMFailureCategory.RATE_LIMIT,
        LLMFailureCategory.PROVIDER_UNAVAILABLE,
    ],
)
async def test_only_retryable_transient_categories_retry_with_stable_context(
    category: LLMFailureCategory,
) -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=1)
    failure = ProviderFailure(
        category,
        retryable=True,
        retry_after_seconds=0.02 if category is LLMFailureCategory.RATE_LIMIT else None,
    )
    provider = DeterministicOfflineLLMProvider(
        (
            DeterministicLLMFixture(
                request=request,
                outcomes=(failure, make_result(request, attempt=2)),
            ),
        )
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome == OrchestrationOutcome.success(make_result(request, attempt=2))
    assert [seen.attempt for seen in provider.requests] == [1, 2]
    assert all(replace(seen, attempt=1) == request for seen in provider.requests)
    assert len(clock.delays) == 1


@pytest.mark.parametrize(
    "category",
    [
        LLMFailureCategory.AUTH_FAILURE,
        LLMFailureCategory.REFUSAL,
        LLMFailureCategory.SCHEMA_INVALID,
        LLMFailureCategory.CONTENT_POLICY_BLOCK,
        LLMFailureCategory.UNKNOWN,
    ],
)
async def test_non_retryable_categories_never_retry(category: LLMFailureCategory) -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=3)
    provider = DeterministicOfflineLLMProvider(
        (
            DeterministicLLMFixture(
                request=request,
                outcomes=(ProviderFailure(category), make_result(request, attempt=2)),
            ),
        )
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is category
    assert len(provider.requests) == 1
    assert clock.delays == []


@pytest.mark.parametrize("category", list(LLMFailureCategory))
async def test_every_provider_failure_is_normalized_to_the_closed_category(
    category: LLMFailureCategory,
) -> None:
    clock = ControlledClock()
    request = make_request(clock)
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(ProviderFailure(category),)),)
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.result is None
    assert outcome.failure is not None
    assert outcome.failure.category is category
    assert str(outcome.failure) == category.value


async def test_deadline_exhaustion_blocks_retry_and_returns_timeout() -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=1)
    request = replace(request, deadline_at=clock.current + timedelta(milliseconds=5))
    provider = DeterministicOfflineLLMProvider(
        (
            DeterministicLLMFixture(
                request=request,
                outcomes=(
                    ProviderFailure(
                        LLMFailureCategory.RATE_LIMIT,
                        retryable=True,
                        retry_after_seconds=0.02,
                    ),
                ),
            ),
        )
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.TIMEOUT
    assert len(provider.requests) == 1
    assert clock.delays == []


async def test_rate_limit_hint_above_engineering_cap_is_not_shortened_or_retried() -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=1)
    provider = DeterministicOfflineLLMProvider(
        (
            DeterministicLLMFixture(
                request=request,
                outcomes=(
                    ProviderFailure(
                        LLMFailureCategory.RATE_LIMIT,
                        retryable=True,
                        retry_after_seconds=10.0,
                    ),
                ),
            ),
        )
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.RATE_LIMIT
    assert len(provider.requests) == 1
    assert clock.delays == []


async def test_expired_deadline_never_calls_provider() -> None:
    clock = ControlledClock()
    request = replace(make_request(clock), deadline_at=clock.current - timedelta(milliseconds=1))
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(make_result(request),)),)
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.TIMEOUT
    assert provider.requests == ()


async def test_total_deadline_is_checked_after_provider_returns() -> None:
    clock = ControlledClock()
    request = make_request(clock)

    class LateProvider(DisabledLLMProvider):
        @property
        def provider_id(self) -> str:
            return "offline_fake"

        async def generate_structured(self, attempted: StructuredLLMRequest) -> StructuredLLMResult:
            clock.current += timedelta(seconds=6)
            return make_result(attempted)

    outcome = await service(LateProvider(), clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.TIMEOUT


async def test_provider_call_is_cancelled_when_runtime_deadline_expires() -> None:
    clock = ControlledClock()
    request = replace(make_request(clock), deadline_at=clock.current + timedelta(milliseconds=20))
    cancelled = asyncio.Event()

    class BlockingProvider(DisabledLLMProvider):
        async def generate_structured(self, attempted: StructuredLLMRequest) -> StructuredLLMResult:
            del attempted
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
            raise AssertionError("unreachable")

    outcome = await service(BlockingProvider(), clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.TIMEOUT
    assert cancelled.is_set()


async def test_retry_budget_exhaustion_stops_at_budget_plus_one_attempts() -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=1)
    transient = ProviderFailure(LLMFailureCategory.PROVIDER_UNAVAILABLE, retryable=True)
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(transient, transient)),)
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.PROVIDER_UNAVAILABLE
    assert outcome.failure.attempt_count == 2
    assert [seen.attempt for seen in provider.requests] == [1, 2]


async def test_result_version_or_correlation_mismatch_fails_without_retry() -> None:
    clock = ControlledClock()
    request = make_request(clock, retry_budget=2)
    mismatched = replace(make_result(request), schema_version="2.0.0")
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(mismatched,)),)
    )

    outcome = await service(provider, clock).generate_structured(request)

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.SCHEMA_INVALID
    assert len(provider.requests) == 1


async def test_unknown_provider_exception_is_isolated_without_sensitive_detail() -> None:
    marker = "synthetic-sensitive-provider-detail"
    clock = ControlledClock()

    class UnexpectedProvider(DisabledLLMProvider):
        async def generate_structured(self, request: StructuredLLMRequest) -> StructuredLLMResult:
            del request
            raise RuntimeError(marker)

    outcome = await service(UnexpectedProvider(), clock).generate_structured(make_request(clock))

    assert outcome.failure is not None
    assert outcome.failure.category is LLMFailureCategory.UNKNOWN
    assert marker not in repr(outcome)
    assert marker not in str(outcome.failure)


async def test_telemetry_failure_cannot_change_successful_outcome() -> None:
    clock = ControlledClock()
    request = make_request(clock)
    expected = make_result(request)
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(expected,)),)
    )

    class BrokenTelemetry:
        def record(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            raise RuntimeError("synthetic telemetry failure")

    orchestrator = AIOrchestrationService(
        provider=provider,
        clock=clock.now,
        sleeper=clock.sleep,
        telemetry=BrokenTelemetry(),
    )

    assert await orchestrator.generate_structured(request) == OrchestrationOutcome.success(expected)


async def test_cancellation_is_propagated_and_never_retried() -> None:
    clock = ControlledClock()

    class CancelledProvider(DisabledLLMProvider):
        async def generate_structured(self, request: StructuredLLMRequest) -> StructuredLLMResult:
            del request
            raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await service(CancelledProvider(), clock).generate_structured(
            make_request(clock, retry_budget=3)
        )

    assert clock.delays == []


def test_retryable_flag_is_rejected_for_permanent_failures() -> None:
    with pytest.raises(ValueError, match="cannot be retried"):
        ProviderFailure(LLMFailureCategory.AUTH_FAILURE, retryable=True)


@pytest.mark.parametrize("retry_after", [-1.0, float("inf"), float("nan")])
def test_invalid_retry_after_is_rejected(retry_after: float) -> None:
    with pytest.raises(ValueError, match="finite and non-negative"):
        ProviderFailure(
            LLMFailureCategory.RATE_LIMIT,
            retryable=True,
            retry_after_seconds=retry_after,
        )
