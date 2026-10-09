"""Request-correlation behavior tests."""

import re

from httpx import AsyncClient

from app.api.middleware import REQUEST_ID_HEADER


async def test_valid_opaque_request_id_is_propagated(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={REQUEST_ID_HEADER: "client.request-123"})

    assert response.headers[REQUEST_ID_HEADER] == "client.request-123"


async def test_invalid_request_id_is_replaced(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={REQUEST_ID_HEADER: "invalid value"})

    assert re.fullmatch(r"req_[0-9a-f]{32}", response.headers[REQUEST_ID_HEADER])
