"""FastAPI exception-handler registration."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.api.errors.models import build_error_response
from app.shared.errors import ErrorCode, SwasthyaSetuError

HTTP_STATUS_BY_ERROR_CODE = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.AUTHENTICATION_REQUIRED: 401,
    ErrorCode.AUTHORIZATION_DENIED: 403,
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.RESOURCE_CONFLICT: 409,
    ErrorCode.INVALID_STATE_TRANSITION: 409,
    ErrorCode.FEATURE_DISABLED: 404,
    ErrorCode.CONSENT_REQUIRED: 403,
    ErrorCode.SESSION_EXPIRED: 401,
    ErrorCode.RATE_LIMITED: 429,
    # The canonical API does not freeze 504; dependency timeouts conservatively use 503.
    ErrorCode.DEPENDENCY_TIMEOUT: 503,
    ErrorCode.DEPENDENCY_UNAVAILABLE: 503,
    ErrorCode.PROCESSING_FAILED: 500,
    ErrorCode.POLICY_UNAVAILABLE: 503,
    ErrorCode.INSUFFICIENT_INFORMATION: 400,
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: 415,
    ErrorCode.PAYLOAD_TOO_LARGE: 413,
}


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unavailable"))


def _protect_sensitive_response(request: Request, response: JSONResponse) -> JSONResponse:
    """Prevent storage of sensitive API errors without inspecting request secrets."""
    route = str(getattr(request.scope.get("route"), "path", ""))
    if any(
        f"/{segment}" in route
        for segment in ("sessions", "consents", "patients", "encounters", "intakes")
    ):
        response.headers["Cache-Control"] = "no-store"
    return response


async def application_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate a typed application error into the canonical envelope."""
    if not isinstance(exc, SwasthyaSetuError):
        raise TypeError("application_error_handler received an unexpected exception")
    return _protect_sensitive_response(
        request,
        build_error_response(
            status_code=HTTP_STATUS_BY_ERROR_CODE[exc.code],
            code=exc.code,
            message=exc.message,
            request_id=_request_id(request),
            details=exc.details,
        ),
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a stable validation response without echoing submitted values."""
    if not isinstance(exc, RequestValidationError):
        raise TypeError("validation_error_handler received an unexpected exception")
    return _protect_sensitive_response(
        request,
        build_error_response(
            status_code=422,
            code=ErrorCode.VALIDATION_ERROR,
            message="The request did not pass validation.",
            request_id=_request_id(request),
        ),
    )


async def http_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Normalize framework HTTP errors into the project envelope."""
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError("http_error_handler received an unexpected exception")
    code_by_status = {
        400: ErrorCode.INSUFFICIENT_INFORMATION,
        401: ErrorCode.AUTHENTICATION_REQUIRED,
        403: ErrorCode.AUTHORIZATION_DENIED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        409: ErrorCode.RESOURCE_CONFLICT,
        413: ErrorCode.PAYLOAD_TOO_LARGE,
        415: ErrorCode.UNSUPPORTED_MEDIA_TYPE,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMITED,
        503: ErrorCode.DEPENDENCY_UNAVAILABLE,
    }
    message_by_status = {
        400: "The request could not be understood.",
        401: "Authentication is required.",
        403: "This action is not permitted.",
        404: "The requested resource was not found.",
        409: "The request conflicts with current resource state.",
        413: "The request payload is too large.",
        415: "The request media type is not supported.",
        422: "The request did not pass validation.",
        429: "Too many requests.",
        503: "This service is temporarily unavailable.",
    }
    return _protect_sensitive_response(
        request,
        build_error_response(
            status_code=exc.status_code,
            code=code_by_status.get(exc.status_code, ErrorCode.PROCESSING_FAILED),
            message=message_by_status.get(exc.status_code, "The request could not be completed."),
            request_id=_request_id(request),
        ),
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fail closed with a stable envelope; exception details stay server-side."""
    return _protect_sensitive_response(
        request,
        build_error_response(
            status_code=500,
            code=ErrorCode.PROCESSING_FAILED,
            message="The request could not be completed.",
            request_id=_request_id(request),
        ),
    )


def register_error_handlers(application: FastAPI) -> None:
    """Register project-owned exception translation with FastAPI."""
    application.add_exception_handler(SwasthyaSetuError, application_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_error_handler)
    application.add_exception_handler(Exception, unexpected_error_handler)
