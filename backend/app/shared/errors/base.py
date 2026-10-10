"""Framework-independent project error hierarchy."""

from collections.abc import Mapping

from app.shared.errors.codes import ErrorCode

type ErrorValue = str | int | float | bool | None
type ErrorDetails = Mapping[str, ErrorValue]


class SwasthyaSetuError(Exception):
    """Base error carrying only safe public fields at transport boundaries."""

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        details: ErrorDetails | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details or {})
        if cause is not None:
            self.__cause__ = cause


class DomainError(SwasthyaSetuError):
    """Base for domain-rule failures defined by later bounded contexts."""


class ApplicationError(SwasthyaSetuError):
    """Base for application/use-case failures."""


class DependencyError(SwasthyaSetuError):
    """Provider-neutral external dependency failure."""

    _ALLOWED_CODES = {ErrorCode.DEPENDENCY_TIMEOUT, ErrorCode.DEPENDENCY_UNAVAILABLE}

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        details: ErrorDetails | None = None,
        cause: Exception | None = None,
    ) -> None:
        if code not in self._ALLOWED_CODES:
            raise ValueError("DependencyError requires a dependency error code")
        super().__init__(code=code, message=message, details=details, cause=cause)
