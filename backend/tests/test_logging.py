"""Privacy-safe structured logging tests."""

import json
import logging

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
