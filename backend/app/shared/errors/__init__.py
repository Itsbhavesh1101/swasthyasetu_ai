"""Stable shared error contracts."""

from app.shared.errors.base import (
    ApplicationError,
    DependencyError,
    DomainError,
    ErrorDetails,
    ErrorValue,
    SwasthyaSetuError,
)
from app.shared.errors.codes import ErrorCode

__all__ = [
    "ApplicationError",
    "DependencyError",
    "DomainError",
    "ErrorCode",
    "ErrorDetails",
    "ErrorValue",
    "SwasthyaSetuError",
]
