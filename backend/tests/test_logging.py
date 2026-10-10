"""Privacy-safe structured logging tests."""

import json
import logging
from io import StringIO

from fastapi import APIRouter, Body
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.shared.observability.logging import JsonFormatter, request_id_context


def test_json_formatter_includes_correlation_without_unapproved_fields() -> None:
    token = request_id_context.set("req_test")
    try:
        record = logging.LogRecord(
            name="swasthyasetu.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=12,
            msg="HTTP request completed",
            args=(),
            exc_info=None,
        )
        record.method = "POST"
        record.route = "/api/v1/example"
        record.authorization = "Bearer secret-value"
        record.request_body = "sensitive-body"

        payload = json.loads(JsonFormatter().format(record))
    finally:
        request_id_context.reset(token)

    assert payload["request_id"] == "req_test"
    assert payload["method"] == "POST"
    assert payload["route"] == "/api/v1/example"
    assert "authorization" not in payload
    assert "request_body" not in payload
    assert "secret-value" not in json.dumps(payload)
    assert "sensitive-body" not in json.dumps(payload)


async def test_access_log_excludes_request_body_and_carries_request_id() -> None:
    router = APIRouter()

    @router.post("/logging-privacy")
    async def logging_privacy(value: str = Body(embed=True)) -> dict[str, bool]:
        return {"accepted": bool(value)}

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    logger = logging.getLogger("swasthyasetu")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    try:
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            response = await test_client.post(
                "/api/v1/logging-privacy",
                headers={"X-Request-ID": "privacy-test-request"},
                json={"value": "synthetic-sensitive-body"},
            )
    finally:
        logger.removeHandler(handler)

    output = stream.getvalue()
    assert response.status_code == 200
    assert "privacy-test-request" in output
    assert "synthetic-sensitive-body" not in output
