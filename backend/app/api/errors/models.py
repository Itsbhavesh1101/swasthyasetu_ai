"""Transport-owned models for the canonical public error envelope."""

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from app.shared.errors import ErrorCode, ErrorDetails


class ErrorDetail(BaseModel):
    """Stable, privacy-safe public error detail."""

    code: ErrorCode
    message: str
    request_id: str
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Canonical project error envelope."""

    error: ErrorDetail


def build_error_response(
    *,
    status_code: int,
    code: ErrorCode,
    message: str,
    request_id: str,
    details: ErrorDetails | None = None,
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
