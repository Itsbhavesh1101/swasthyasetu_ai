"""FastAPI exception-handler registration."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.api.errors.models import ApplicationError, ErrorCode, build_error_response


def _request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unavailable"))


async def application_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate a typed application error into the canonical envelope."""
    if not isinstance(exc, ApplicationError):
        raise TypeError("application_error_handler received an unexpected exception")
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        request_id=_request_id(request),
        details=exc.details,
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a stable validation response without echoing submitted values."""
    if not isinstance(exc, RequestValidationError):
        raise TypeError("validation_error_handler received an unexpected exception")
    return build_error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR,
        message="The request did not pass validation.",
        request_id=_request_id(request),
    )


async def http_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Normalize framework HTTP errors into the project envelope."""
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError("http_error_handler received an unexpected exception")
    code_by_status = {
        401: ErrorCode.AUTHENTICATION_REQUIRED,
        403: ErrorCode.AUTHORIZATION_DENIED,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        409: ErrorCode.RESOURCE_CONFLICT,
        429: ErrorCode.RATE_LIMITED,
        503: ErrorCode.DEPENDENCY_UNAVAILABLE,
    }
    message_by_status = {
        401: "Authentication is required.",
        403: "This action is not permitted.",
        404: "The requested resource was not found.",
        409: "The request conflicts with current resource state.",
        429: "Too many requests.",
        503: "This service is temporarily unavailable.",
    }
    return build_error_response(
        status_code=exc.status_code,
        code=code_by_status.get(exc.status_code, ErrorCode.PROCESSING_FAILED),
        message=message_by_status.get(exc.status_code, "The request could not be completed."),
        request_id=_request_id(request),
    )


def register_error_handlers(application: FastAPI) -> None:
    """Register project-owned exception translation with FastAPI."""
    application.add_exception_handler(ApplicationError, application_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_error_handler)
