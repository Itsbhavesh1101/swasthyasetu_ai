"""Standard-library structured logging with request correlation context."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Final

from opentelemetry import trace

from app.config import LogLevel

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)

_EXTRA_FIELDS: Final = (
    "method",
    "route",
    "status_code",
    "duration_ms",
    "error_code",
    "module",
    "operation",
)


class JsonFormatter(logging.Formatter):
    """Format an allowlist of operational metadata as one JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str | int | float] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_context.get()
        if request_id is not None:
            payload["request_id"] = request_id
        current_span = trace.get_current_span()
        span_context = current_span.get_span_context()
        if current_span.is_recording() and span_context.is_valid:
            payload["trace_id"] = format(span_context.trace_id, "032x")
            payload["span_id"] = format(span_context.span_id, "016x")
        for field_name in _EXTRA_FIELDS:
            field_value = getattr(record, field_name, None)
            if isinstance(field_value, (str, int, float)):
                payload[field_name] = field_value
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def configure_logging(log_level: LogLevel) -> None:
    """Configure the project logger idempotently for an application instance."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("swasthyasetu")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(log_level.value)
    logger.propagate = False
