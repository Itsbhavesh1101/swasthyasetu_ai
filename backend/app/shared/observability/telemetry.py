"""Project-owned, in-process OpenTelemetry runtime."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Final

from opentelemetry import metrics, trace
from opentelemetry.metrics import Meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter
from opentelemetry.trace import Span, Status, StatusCode, Tracer

from app.config import ObservabilitySettings

INSTRUMENTATION_SCOPE: Final = "app.shared.observability"
HTTP_REQUEST_COUNT: Final = "swasthyasetu.http.server.requests"
HTTP_REQUEST_DURATION: Final = "swasthyasetu.http.server.duration"
HTTP_DURATION_UNIT: Final = "ms"
UNMATCHED_ROUTE: Final = "unmatched"
_logger = logging.getLogger("swasthyasetu.observability")


@dataclass(frozen=True, slots=True)
class ObservabilityRuntime:
    """Per-application tracing and metrics providers without default export."""

    resource: Resource
    tracer_provider: TracerProvider
    meter_provider: MeterProvider
    tracer: Tracer
    meter: Meter
    tracing_enabled: bool
    metrics_enabled: bool
    span_exporter_configured: bool
    metric_reader_configured: bool
    request_counter: metrics.Counter
    request_duration: metrics.Histogram

    @contextmanager
    def start_http_span(self, method: str, request_id: str) -> Iterator[Span]:
        """Start a content-free server span, or a no-op span when tracing is disabled."""
        if not self.tracing_enabled:
            yield trace.INVALID_SPAN
            return

        try:
            span_manager = self.tracer.start_as_current_span(
                f"HTTP {method}",
                kind=trace.SpanKind.SERVER,
                attributes={
                    "http.request.method": method,
                    "swasthyasetu.request_id": request_id,
                },
                record_exception=False,
                set_status_on_exception=False,
            )
            span = span_manager.__enter__()
        except Exception:
            _logger.warning("HTTP trace start failed", extra={"operation": "http.trace.start"})
            yield trace.INVALID_SPAN
            return

        try:
            yield span
        finally:
            try:
                span_manager.__exit__(None, None, None)
            except Exception:
                _logger.warning(
                    "HTTP trace finish failed", extra={"operation": "http.trace.finish"}
                )

    def complete_http_request(
        self,
        span: Span,
        *,
        method: str,
        route: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Record allowlisted response metadata with bounded cardinality."""
        try:
            attributes: dict[str, str | int] = {
                "http.request.method": method,
                "http.route": route,
                "http.response.status_code": status_code,
            }
            if span.is_recording():
                span.update_name(
                    f"HTTP {method} {route}" if route != UNMATCHED_ROUTE else f"HTTP {method}"
                )
                span.set_attributes(attributes)
                if status_code >= 500:
                    span.set_attribute("error.code", "PROCESSING_FAILED")
                    span.set_status(Status(StatusCode.ERROR))

            if self.metrics_enabled:
                self.request_counter.add(1, attributes)
                self.request_duration.record(duration_ms, attributes)
        except Exception:
            _logger.warning("HTTP telemetry recording failed", extra={"operation": "http.observe"})


def create_observability_runtime(
    settings: ObservabilitySettings,
    *,
    span_exporter: SpanExporter | None = None,
    metric_reader: MetricReader | None = None,
) -> ObservabilityRuntime:
    """Create isolated providers; exporters/readers are injectable only for deterministic tests."""
    resource = Resource.create({SERVICE_NAME: settings.service_name})
    tracer_provider = TracerProvider(resource=resource)
    if span_exporter is not None:
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))

    metric_readers = () if metric_reader is None else (metric_reader,)
    meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    tracer = tracer_provider.get_tracer(INSTRUMENTATION_SCOPE)
    meter = meter_provider.get_meter(INSTRUMENTATION_SCOPE)

    return ObservabilityRuntime(
        resource=resource,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        tracer=tracer,
        meter=meter,
        tracing_enabled=settings.tracing_enabled,
        metrics_enabled=settings.metrics_enabled,
        span_exporter_configured=span_exporter is not None,
        metric_reader_configured=metric_reader is not None,
        request_counter=meter.create_counter(
            HTTP_REQUEST_COUNT,
            unit="{request}",
            description="Completed inbound HTTP requests",
        ),
        request_duration=meter.create_histogram(
            HTTP_REQUEST_DURATION,
            unit=HTTP_DURATION_UNIT,
            description="Inbound HTTP request duration",
        ),
    )
