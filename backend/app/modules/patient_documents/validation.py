"""Strict, text-blind validation for the private patient document vault."""

import hashlib
import unicodedata
from dataclasses import dataclass
from pathlib import PurePath

from app.shared.storage import ObjectKey
from app.shared.types import OpaqueId

SUPPORTED_TYPES = {
    "application/pdf": (".pdf", b"%PDF-"),
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
}


@dataclass(frozen=True, slots=True)
class ValidatedDocument:
    display_name: str
    mime_type: str
    content: bytes
    sha256_digest: str
    extension: str


def validate_document(
    *, filename: str, claimed_mime_type: str, content: bytes, max_bytes: int
) -> ValidatedDocument:
    if not isinstance(content, bytes):
        raise TypeError("document content must be bytes")
    if not content or len(content) > max_bytes:
        raise ValueError("document size is invalid")
    normalized = unicodedata.normalize("NFC", filename)
    if (
        not normalized
        or normalized != normalized.strip()
        or len(normalized) > 255
        or PurePath(normalized).name != normalized
        or "/" in normalized
        or "\\" in normalized
        or ":" in normalized
        or any(unicodedata.category(character).startswith("C") for character in normalized)
    ):
        raise ValueError("document filename is invalid")
    supported = SUPPORTED_TYPES.get(claimed_mime_type.lower())
    if supported is None:
        raise ValueError("document type is unsupported")
    canonical_extension, signature = supported
    suffix = PurePath(normalized).suffix.lower()
    if claimed_mime_type.lower() == "image/jpeg" and suffix == ".jpeg":
        canonical_extension = ".jpeg"
    if (
        suffix != canonical_extension
        or len(content) < len(signature)
        or not content.startswith(signature)
    ):
        raise ValueError("document type does not match content")
    return ValidatedDocument(
        display_name=normalized,
        mime_type=claimed_mime_type.lower(),
        content=content,
        sha256_digest=hashlib.sha256(content).hexdigest(),
        extension=canonical_extension,
    )


def document_object_key(patient_id: OpaqueId, document_id: OpaqueId, extension: str) -> ObjectKey:
    if extension not in {".pdf", ".jpg", ".jpeg", ".png"}:
        raise ValueError("document extension is unsupported")
    return ObjectKey(f"patient-documents/{patient_id}/{document_id}{extension}")
