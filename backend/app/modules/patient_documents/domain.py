"""Immutable patient document metadata and content contracts."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.shared.storage import ObjectKey
from app.shared.types import OpaqueId


def _utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class PatientDocument:
    document_id: OpaqueId
    patient_id: OpaqueId
    display_name: str = field(repr=False)
    mime_type: str
    byte_size: int
    object_key: ObjectKey = field(repr=False)
    sha256_digest: str = field(repr=False)
    created_at: datetime
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        if (
            not self.display_name
            or self.display_name != self.display_name.strip()
            or len(self.display_name) > 255
        ):
            raise ValueError("display_name must be non-blank, trimmed, and bounded")
        if self.mime_type not in {"application/pdf", "image/jpeg", "image/png"}:
            raise ValueError("mime_type is unsupported")
        if self.byte_size <= 0:
            raise ValueError("byte_size must be positive")
        if len(self.sha256_digest) != 64 or any(
            character not in "0123456789abcdef" for character in self.sha256_digest
        ):
            raise ValueError("sha256_digest is invalid")
        created = _utc("created_at", self.created_at)
        deleted = None if self.deleted_at is None else _utc("deleted_at", self.deleted_at)
        if deleted is not None and deleted < created:
            raise ValueError("deleted_at must not precede created_at")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "deleted_at", deleted)


@dataclass(frozen=True, slots=True)
class DocumentContent:
    document: PatientDocument
    content: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.content, bytes):
            raise TypeError("content must be bytes")
        if len(self.content) != self.document.byte_size:
            raise ValueError("content size does not match metadata")
