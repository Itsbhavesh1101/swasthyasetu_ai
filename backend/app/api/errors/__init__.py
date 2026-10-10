"""HTTP error contracts and exception translation."""

from app.api.errors.handlers import register_error_handlers
from app.api.errors.models import ErrorResponse
from app.shared.errors import (
    ApplicationError,
    DependencyError,
    DomainError,
    ErrorCode,
    SwasthyaSetuError,
)

__all__ = [
    "ApplicationError",
    "DependencyError",
    "DomainError",
    "ErrorCode",
    "ErrorResponse",
    "SwasthyaSetuError",
    "register_error_handlers",
]
