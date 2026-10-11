"""Provider-neutral object-storage value types and errors."""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_OBJECT_KEY_LENGTH = 1024
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


class ObjectStorageError(Exception):
    """Base error that does not expose provider or filesystem details."""


class InvalidObjectKeyError(ObjectStorageError, ValueError):
    """Raised when a technical object key is unsafe or malformed."""


class ObjectNotFoundError(ObjectStorageError):
    """Raised when the requested object does not exist."""


class ObjectAlreadyExistsError(ObjectStorageError):
    """Raised when a non-overwriting write targets an existing object."""


class ObjectKey(str):
    """Immutable, bounded, root-relative POSIX technical object key."""

    def __new__(cls, value: str) -> ObjectKey:
        if not isinstance(value, str):
            raise TypeError("object key must be a string")
        segments = value.split("/")
        if (
            not value
            or len(value) > MAX_OBJECT_KEY_LENGTH
            or value.startswith("/")
            or _WINDOWS_DRIVE.match(value) is not None
            or "\\" in value
            or "\x00" in value
            or any(segment in {"", ".", ".."} for segment in segments)
        ):
            raise InvalidObjectKeyError("object key is invalid")
        return super().__new__(cls, value)


@dataclass(frozen=True, slots=True)
class ObjectMetadata:
    """Provider-neutral result of storing one object."""

    key: ObjectKey
    size_bytes: int
    sha256: str
