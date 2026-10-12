"""Privacy-safe parsing for exact HTTP Bearer credentials."""

from app.shared.errors import ApplicationError, ErrorCode


def parse_bearer(value: str | None) -> str:
    """Return the exact bearer token or fail without echoing credential material."""
    if value is None:
        raise _authentication_required()
    scheme, separator, token = value.partition(" ")
    if (
        separator != " "
        or scheme != "Bearer"
        or not token
        or token != token.strip()
        or " " in token
    ):
        raise _authentication_required()
    return token


def _authentication_required() -> ApplicationError:
    return ApplicationError(
        code=ErrorCode.AUTHENTICATION_REQUIRED,
        message="A valid bearer token is required.",
    )


__all__ = ["parse_bearer"]
