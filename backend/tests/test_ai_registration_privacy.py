"""P8-A explicit composition, production guard, health, and privacy tests."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.adapters.ai.fake import DeterministicLLMFixture, DeterministicOfflineLLMProvider
from app.config import Environment, LlmSettings, ObservabilitySettings, Settings
from app.main import create_app
from app.modules.ai_orchestration.contracts import (
    REQUEST_CONTRACT_VERSION,
    RESULT_CONTRACT_VERSION,
    FinishReason,
    ResultProvenance,
    SourceReference,
    StructuredLLMRequest,
    StructuredLLMResult,
)
from app.modules.ai_orchestration.providers import ProviderHealthStatus
from app.modules.ai_orchestration.public import (
    AI_GENERATE_STRUCTURED,
    AI_HEALTH,
    AI_ORCHESTRATION_MANIFEST,
    UnsafeProviderCompositionError,
    build_ai_orchestration_registration,
)
from app.modules.ai_orchestration.telemetry import (
    AI_ATTEMPT_COUNT,
    AI_OPERATION_COUNT,
    AI_OPERATION_DURATION,
)
from app.shared.modules import ModuleId, ModuleRegistry
from app.shared.observability import create_observability_runtime


def request_and_result(
    marker: str = "synthetic-sensitive-canary",
) -> tuple[StructuredLLMRequest, StructuredLLMResult]:
    source = SourceReference("source_synthetic_0001", "1", "a" * 64)
    request = StructuredLLMRequest(
        operation_id="synthetic.extract",
        language_code="en",
        request_id="req_synthetic_0001",
        request_contract_version=REQUEST_CONTRACT_VERSION,
        schema_id="synthetic_candidate",
        schema_version="1.0.0",
        prompt_id="synthetic_prompt",
        prompt_version="1.0.0",
        input={"message": marker, "nested": {"value": marker}},
        max_output_tokens=128,
        deadline_at=datetime.now(UTC) + timedelta(seconds=5),
        retry_budget=0,
        attempt=1,
        provider_policy_id="offline_only",
        provider_policy_version="1.0.0",
        provenance_context=(source,),
    )
    result = StructuredLLMResult(
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
        validated_payload={"candidate": marker},
        finish_reason=FinishReason.STOP,
        usage=None,
        latency_ms=1.5,
        attempt_count=1,
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
    return request, result


def metric_points(data: Any) -> dict[str, list[Any]]:
    return {
        metric.name: list(metric.data.data_points)
        for resource_metrics in data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
    }


def test_manifest_has_explicit_router_free_capabilities_and_no_data_ownership() -> None:
    assert AI_ORCHESTRATION_MANIFEST.module_id == ModuleId("ai_orchestration")
    assert AI_ORCHESTRATION_MANIFEST.version == 1
    assert AI_ORCHESTRATION_MANIFEST.api_prefixes == ()
    assert AI_ORCHESTRATION_MANIFEST.data_ownership == ()
    assert AI_ORCHESTRATION_MANIFEST.required_capabilities == frozenset()
    assert AI_ORCHESTRATION_MANIFEST.configuration_keys == ("llm.enabled",)

    registration = build_ai_orchestration_registration(
        environment=Environment.TEST,
        enabled=False,
        observability=create_observability_runtime(ObservabilitySettings()),
    )
    registry = ModuleRegistry[object]()
    registry.register(registration)
    registry.finalize()

    assert registration.routers == ()
    assert registry.capability_registry.resolve(AI_GENERATE_STRUCTURED) is not None
    assert registry.capability_registry.resolve(AI_HEALTH).health().status is (
        ProviderHealthStatus.DISABLED
    )


def test_default_application_registers_disabled_ai_without_endpoint_or_readiness_dependency() -> (
    None
):
    application = create_app(Settings(_env_file=None))

    assert "ai_orchestration" in application.state.module_registry.module_ids
    assert application.state.capability_registry.resolve(AI_HEALTH).health().status is (
        ProviderHealthStatus.DISABLED
    )
    assert not any("/ai" in path or "/llm" in path for path in application.openapi()["paths"])


def test_enabled_without_an_approved_provider_is_honestly_unconfigured() -> None:
    application = create_app(Settings(llm=LlmSettings(enabled=True), _env_file=None))

    health = application.state.capability_registry.resolve(AI_HEALTH).health()
    assert health.status is ProviderHealthStatus.UNCONFIGURED
    assert health.clinically_approved is False


def test_provider_health_can_report_degraded_without_a_live_probe() -> None:
    provider = DeterministicOfflineLLMProvider((), degraded=True)
    registration = build_ai_orchestration_registration(
        environment=Environment.TEST,
        enabled=True,
        observability=create_observability_runtime(ObservabilitySettings()),
        provider=provider,
    )
    registry = ModuleRegistry[object]()
    registry.register(registration)
    registry.finalize()

    health = registry.capability_registry.resolve(AI_HEALTH).health()
    assert health.status is ProviderHealthStatus.DEGRADED
    assert provider.requests == ()


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_engineering_fake_is_rejected_outside_local_and_test(
    environment: Environment,
) -> None:
    provider = DeterministicOfflineLLMProvider(())

    with pytest.raises(UnsafeProviderCompositionError, match="engineering-only"):
        build_ai_orchestration_registration(
            environment=environment,
            enabled=True,
            observability=create_observability_runtime(ObservabilitySettings()),
            provider=provider,
        )


async def test_fake_is_explicitly_injectable_in_test_and_telemetry_excludes_content() -> None:
    marker = "synthetic-sensitive-canary"
    request, result = request_and_result(marker)
    provider = DeterministicOfflineLLMProvider(
        (DeterministicLLMFixture(request=request, outcomes=(result,)),)
    )
    exporter = InMemorySpanExporter()
    reader = InMemoryMetricReader()
    runtime = create_observability_runtime(
        ObservabilitySettings(), span_exporter=exporter, metric_reader=reader
    )
    registration = build_ai_orchestration_registration(
        environment=Environment.TEST,
        enabled=True,
        observability=runtime,
        provider=provider,
    )
    registry = ModuleRegistry[object]()
    registry.register(registration)
    registry.finalize()

    outcome = await registry.capability_registry.resolve(
        AI_GENERATE_STRUCTURED
    ).generate_structured(request)

    assert outcome.result == result
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "AI structured generation"
    points = metric_points(reader.get_metrics_data())
    assert set(points) == {AI_OPERATION_COUNT, AI_ATTEMPT_COUNT, AI_OPERATION_DURATION}
    serialized = repr((spans, points))
    assert marker not in serialized
    assert "provider_synthetic_0001" not in serialized
    assert "source_synthetic_0001" not in serialized
    metric_attributes = [point.attributes for values in points.values() for point in values]
    assert all("swasthyasetu.ai.request_id" not in value for value in metric_attributes)


def test_contract_repr_excludes_structured_input_and_candidate_payload() -> None:
    marker = "synthetic-sensitive-canary"
    request, result = request_and_result(marker)

    assert marker not in repr(request)
    assert marker not in repr(result)
    assert "source_synthetic_0001" not in repr(request)
    assert "source_synthetic_0001" not in repr(result)
