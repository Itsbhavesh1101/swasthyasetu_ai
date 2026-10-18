"""Privacy-safe OpenTelemetry instrumentation for P8-A orchestration."""

from typing import Final

from opentelemetry.trace import Status, StatusCode

from app.modules.ai_orchestration.application import OrchestrationTelemetry
from app.modules.ai_orchestration.contracts import StructuredLLMRequest, StructuredLLMResult
from app.modules.ai_orchestration.providers import LLMFailureCategory
from app.shared.observability import ObservabilityRuntime

AI_OPERATION_COUNT: Final = "swasthyasetu.ai.operations"
AI_ATTEMPT_COUNT: Final = "swasthyasetu.ai.attempts"
AI_OPERATION_DURATION: Final = "swasthyasetu.ai.duration"


class OpenTelemetryAIOrchestration(OrchestrationTelemetry):
    """Record allowlisted operational metadata and never request/result content."""

    def __init__(self, runtime: ObservabilityRuntime) -> None:
        self._runtime = runtime
        self._operation_count = runtime.meter.create_counter(
            AI_OPERATION_COUNT,
            unit="{operation}",
            description="Completed structured AI orchestration operations",
        )
        self._attempt_count = runtime.meter.create_histogram(
            AI_ATTEMPT_COUNT,
            unit="{attempt}",
            description="Attempts per structured AI orchestration operation",
        )
        self._duration = runtime.meter.create_histogram(
            AI_OPERATION_DURATION,
            unit="ms",
            description="Provider-reported structured AI operation latency",
        )

    def record(
        self,
        request: StructuredLLMRequest,
        *,
        provider_id: str,
        attempt_count: int,
        result: StructuredLLMResult | None,
        failure: LLMFailureCategory | None,
    ) -> None:
        outcome = "success" if failure is None else failure.value
        model_id = "none" if result is None else result.provider_model_id
        model_version = "none" if result is None else result.provider_model_version
        attributes: dict[str, str | int] = {
            "swasthyasetu.ai.operation_id": request.operation_id,
            "swasthyasetu.ai.prompt_id": request.prompt_id,
            "swasthyasetu.ai.prompt_version": request.prompt_version,
            "swasthyasetu.ai.schema_id": request.schema_id,
            "swasthyasetu.ai.schema_version": request.schema_version,
            "swasthyasetu.ai.provider_id": provider_id,
            "swasthyasetu.ai.model_id": model_id,
            "swasthyasetu.ai.model_version": model_version,
            "swasthyasetu.ai.outcome": outcome,
        }
        try:
            if self._runtime.tracing_enabled:
                with self._runtime.tracer.start_as_current_span(
                    "AI structured generation",
                    attributes={
                        **attributes,
                        "swasthyasetu.ai.request_id": request.request_id,
                        "swasthyasetu.ai.attempt_count": attempt_count,
                    },
                    record_exception=False,
                    set_status_on_exception=False,
                ) as span:
                    if failure is not None:
                        span.set_status(Status(StatusCode.ERROR))
            if self._runtime.metrics_enabled:
                self._operation_count.add(1, attributes)
                self._attempt_count.record(attempt_count, attributes)
                duration_ms = 0.0 if result is None else result.latency_ms
                self._duration.record(duration_ms, attributes)
        except Exception:
            # Observability is optional and must never change application behavior.
            return
