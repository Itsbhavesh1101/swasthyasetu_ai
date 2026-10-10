"""OpenTelemetry HTTP instrumentation and privacy tests."""

import logging
from io import StringIO
from typing import Any

import pytest
from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode
from pydantic import ValidationError

from app.config import ObservabilitySettings, Settings
from app.main import create_app
from app.shared.observability import (
    HTTP_DURATION_UNIT,
    HTTP_REQUEST_COUNT,
    HTTP_REQUEST_DURATION,
    UNMATCHED_ROUTE,
    create_observability_runtime,
)
from app.shared.observability.logging import JsonFormatter


def _metric_points(metrics_data: Any, name: str) -> list[Any]:
    return [
        point
        for resource_metrics in metrics_data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
        if metric.name == name
        for point in metric.data.data_points
    ]


def test_runtime_is_per_application_and_has_no_default_export_pipeline() -> None:
    settings = ObservabilitySettings()

    first = create_observability_runtime(settings)
    second = create_observability_runtime(settings)

    assert first.tracer_provider is not second.tracer_provider
    assert first.meter_provider is not second.meter_provider
    assert first.span_exporter_configured is False
    assert first.metric_reader_configured is False
    assert first.tracer_provider.resource.attributes[SERVICE_NAME] == "swasthyasetu-backend"
    assert first.resource.attributes[SERVICE_NAME] == "swasthyasetu-backend"


def test_external_export_configuration_is_rejected() -> None:
    with pytest.raises(ValidationError, match="not supported in P2-C"):
        ObservabilitySettings(external_export_enabled=True)


async def test_request_trace_uses_route_template_and_excludes_sensitive_content() -> None:
    marker = "synthetic-sensitive-value"
    router = APIRouter()

    @router.get("/synthetic/{item_id}")
    async def synthetic(item_id: str) -> dict[str, bool]:
        return {"accepted": bool(item_id)}

    exporter = InMemorySpanExporter()
    runtime = create_observability_runtime(ObservabilitySettings(), span_exporter=exporter)
    application = create_app(
        Settings(_env_file=None), api_v1_routers=(router,), observability=runtime
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/synthetic/{marker}?secret={marker}",
            headers={"Authorization": f"Bearer {marker}", "Cookie": f"session={marker}"},
        )

    span = exporter.get_finished_spans()[0]
    serialized = repr((span.name, span.attributes, span.events))
    attributes = span.attributes
    assert response.status_code == 200
    assert span.name == "HTTP GET /synthetic/{item_id}"
    assert attributes is not None
    assert attributes["http.request.method"] == "GET"
    assert attributes["http.route"] == "/synthetic/{item_id}"
    assert attributes["http.response.status_code"] == 200
    assert "swasthyasetu.request_id" in attributes
    assert marker not in serialized
    assert "Authorization" not in serialized
    assert "Cookie" not in serialized
    assert "secret=" not in serialized


async def test_exception_response_logs_and_trace_exclude_internal_detail() -> None:
    marker = "synthetic-sensitive-internal-detail"
    router = APIRouter()

    @router.get("/synthetic-failure")
    async def synthetic_failure() -> None:
        raise RuntimeError(marker)

    exporter = InMemorySpanExporter()
    runtime = create_observability_runtime(ObservabilitySettings(), span_exporter=exporter)
    application = create_app(
        Settings(_env_file=None), api_v1_routers=(router,), observability=runtime
    )
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("swasthyasetu")
    logger.addHandler(handler)
    try:
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/synthetic-failure")
    finally:
        logger.removeHandler(handler)

    span = exporter.get_finished_spans()[0]
    telemetry = repr((span.attributes, span.events))
    attributes = span.attributes
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "PROCESSING_FAILED"
    assert span.status.status_code is StatusCode.ERROR
    assert attributes is not None
    assert attributes["error.code"] == "PROCESSING_FAILED"
    assert marker not in response.text
    assert marker not in stream.getvalue()
    assert marker not in telemetry
    assert not span.events


async def test_metrics_are_bounded_and_exclude_request_identifiers_and_raw_paths() -> None:
    marker = "patient-like-id-12345"
    router = APIRouter()

    @router.get("/synthetic/{item_id}")
    async def synthetic(item_id: str) -> dict[str, bool]:
        return {"accepted": bool(item_id)}

    reader = InMemoryMetricReader()
    runtime = create_observability_runtime(ObservabilitySettings(), metric_reader=reader)
    application = create_app(
        Settings(_env_file=None), api_v1_routers=(router,), observability=runtime
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        matched = await client.get(
            f"/api/v1/synthetic/{marker}?secret=value",
            headers={"X-Request-ID": "metric-request-id"},
        )
        unmatched = await client.get(f"/not-found/{marker}?secret=value")

    metrics_data = reader.get_metrics_data()
    count_points = _metric_points(metrics_data, HTTP_REQUEST_COUNT)
    duration_points = _metric_points(metrics_data, HTTP_REQUEST_DURATION)
    all_attributes = [point.attributes for point in (*count_points, *duration_points)]
    serialized = repr(all_attributes)

    assert matched.status_code == 200
    assert unmatched.status_code == 404
    assert sum(point.value for point in count_points) == 2
    assert all(point.count >= 1 for point in duration_points)
    assert {attributes["http.route"] for attributes in all_attributes} == {
        "/synthetic/{item_id}",
        UNMATCHED_ROUTE,
    }
    assert all(
        set(attributes)
        == {
            "http.request.method",
            "http.route",
            "http.response.status_code",
        }
        for attributes in all_attributes
    )
    assert marker not in serialized
    assert "metric-request-id" not in serialized
    assert "secret=value" not in serialized
    assert HTTP_DURATION_UNIT == "ms"


async def test_disabled_instrumentation_does_not_change_health_contract() -> None:
    settings = Settings(
        observability=ObservabilitySettings(tracing_enabled=False, metrics_enabled=False),
        _env_file=None,
    )
    application = create_app(settings)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")

    assert live.json() == {"status": "ok"}
    assert ready.json() == {"status": "ready", "required": {}, "optional": {}}
