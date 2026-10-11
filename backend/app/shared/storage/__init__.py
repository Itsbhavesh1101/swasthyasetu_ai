"""Provider-neutral object-storage contracts."""

from app.shared.storage.port import ObjectStoragePort
from app.shared.storage.types import (
    InvalidObjectKeyError,
    ObjectAlreadyExistsError,
    ObjectKey,
    ObjectMetadata,
    ObjectNotFoundError,
    ObjectStorageError,
)

__all__ = [
    "InvalidObjectKeyError",
    "ObjectAlreadyExistsError",
    "ObjectKey",
    "ObjectMetadata",
    "ObjectNotFoundError",
    "ObjectStorageError",
    "ObjectStoragePort",
]
