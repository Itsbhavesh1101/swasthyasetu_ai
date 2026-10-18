"""Request-correlation behavior tests."""

import re

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.middleware import REQUEST_ID_HEADER, RequestContextMiddleware
from app.config import ObservabilitySettings
from app.shared.observability import create_observability_runtime


async def test_valid_opaque_request_id_is_propagated(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={REQUEST_ID_HEADER: "client.request-123"})

    assert response.headers[REQUEST_ID_HEADER] == "client.request-123"


async def test_invalid_request_id_is_replaced(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={REQUEST_ID_HEADER: "invalid value"})

    assert re.fullmatch(r"req_[0-9a-f]{32}", response.headers[REQUEST_ID_HEADER])


async def test_missing_request_id_is_generated(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert re.fullmatch(r"req_[0-9a-f]{32}", response.headers[REQUEST_ID_HEADER])


async def test_unexpected_request_failure_is_sanitized_and_not_cacheable() -> None:
    application = FastAPI()
    application.add_middleware(
        RequestContextMiddleware,
        observability=create_observability_runtime(ObservabilitySettings()),
    )

    @application.get("/synthetic-failure")
    async def synthetic_failure() -> None:
        raise RuntimeError("sensitive synthetic detail")

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as test_client:
        response = await test_client.get("/synthetic-failure")
    assert response.status_code == 500
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["error"]["code"] == "PROCESSING_FAILED"
    assert "sensitive synthetic detail" not in response.text
