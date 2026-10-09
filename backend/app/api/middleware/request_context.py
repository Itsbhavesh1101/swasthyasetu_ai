"""Privacy-safe request correlation and access logging middleware."""

import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.api.errors.models import ErrorCode, build_error_response
from app.shared.observability import request_id_context

REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_logger = logging.getLogger("swasthyasetu.http")


def _new_request_id() -> str:
    return f"req_{uuid4().hex}"


def _resolve_request_id(inbound_request_id: str | None) -> str:
    if inbound_request_id and _REQUEST_ID_PATTERN.fullmatch(inbound_request_id):
        return inbound_request_id
    return _new_request_id()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach an opaque request ID and log content-free request metadata."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id
        context_token = request_id_context.set(request_id)
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            _logger.error(
                "Unhandled request failure",
                extra={"error_code": ErrorCode.PROCESSING_FAILED.value},
            )
            response = build_error_response(
                status_code=500,
                code=ErrorCode.PROCESSING_FAILED,
                message="The request could not be completed.",
                request_id=request_id,
            )

        response.headers[REQUEST_ID_HEADER] = request_id
        duration_ms = round((perf_counter() - started_at) * 1000, 3)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        _logger.info(
            "HTTP request completed",
            extra={
                "method": request.method,
                "route": route_path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        request_id_context.reset(context_token)
        return response
