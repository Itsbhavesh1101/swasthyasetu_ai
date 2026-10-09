"""Minimal project-level error types and public response models."""

from enum import StrEnum

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse


class ErrorCode(StrEnum):
    """Foundation error codes drawn from the canonical API contract."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class ErrorDetail(BaseModel):
    """Stable, privacy-safe public error detail."""

    code: ErrorCode
    message: str
    request_id: str
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Canonical project error envelope."""

    error: ErrorDetail


class ApplicationError(Exception):
    """Typed application error suitable for translation at the HTTP boundary."""

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        status_code: int,
        details: dict[str, str | int | float | bool | None] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def build_error_response(
    *,
    status_code: int,
    code: ErrorCode,
    message: str,
    request_id: str,
    details: dict[str, str | int | float | bool | None] | None = None,
) -> JSONResponse:
    """Serialize the canonical error envelope without internal exception details."""
    payload = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            request_id=request_id,
            details=details or {},
        )
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))
