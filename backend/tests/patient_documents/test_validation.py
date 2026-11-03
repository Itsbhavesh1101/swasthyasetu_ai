"""Adversarial patient-document validation tests."""

import hashlib
import unicodedata
from datetime import UTC, datetime

import pytest

from app.modules.patient_documents.domain import PatientDocument
from app.modules.patient_documents.validation import document_object_key, validate_document
from app.shared.types import OpaqueId

PDF = b"%PDF-1.7\nsynthetic document"
JPEG = b"\xff\xd8\xff\xe0synthetic image\xff\xd9"
PNG = b"\x89PNG\r\n\x1a\nsynthetic image"


@pytest.mark.parametrize(
    ("filename", "mime_type", "content", "extension"),
    [
        ("report.pdf", "application/pdf", PDF, ".pdf"),
        ("photo.jpg", "image/jpeg", JPEG, ".jpg"),
        ("photo.jpeg", "image/jpeg", JPEG, ".jpeg"),
        ("scan.png", "image/png", PNG, ".png"),
    ],
)
def test_valid_documents_are_detected_and_digested(
    filename: str, mime_type: str, content: bytes, extension: str
) -> None:
    result = validate_document(
        filename=filename, claimed_mime_type=mime_type, content=content, max_bytes=1024
    )
    assert result.extension == extension
    assert result.sha256_digest == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize(
    ("filename", "mime_type", "content", "maximum"),
    [
        ("empty.pdf", "application/pdf", b"", 1024),
        ("large.pdf", "application/pdf", PDF, 2),
        ("wrong.png", "image/png", PDF, 1024),
        ("wrong.pdf", "application/pdf", PNG, 1024),
        ("short.pdf", "application/pdf", b"%PD", 1024),
        ("program.pdf", "application/pdf", b"MZ executable", 1024),
        ("program.png", "image/png", b"\x7fELF executable", 1024),
        ("report.exe", "application/pdf", PDF, 1024),
        ("report.pdf", "application/octet-stream", PDF, 1024),
    ],
)
def test_rejects_empty_oversized_mismatched_truncated_and_executable_content(
    filename: str, mime_type: str, content: bytes, maximum: int
) -> None:
    with pytest.raises(ValueError):
        validate_document(
            filename=filename,
            claimed_mime_type=mime_type,
            content=content,
            max_bytes=maximum,
        )


@pytest.mark.parametrize(
    "filename",
    [
        "../report.pdf",
        "folder/report.pdf",
        "folder\\report.pdf",
        "C:report.pdf",
        " report.pdf",
        "report.pdf ",
        "report\x00.pdf",
        "report\n.pdf",
        "report\u202eexe.pdf",
        "report\u200b.pdf",
    ],
)
def test_rejects_unsafe_display_names(filename: str) -> None:
    with pytest.raises(ValueError):
        validate_document(
            filename=filename,
            claimed_mime_type="application/pdf",
            content=PDF,
            max_bytes=1024,
        )


def test_normalizes_safe_unicode_but_never_places_name_in_object_key() -> None:
    decomposed = unicodedata.normalize("NFD", "रिपोर्ट-é.pdf")
    result = validate_document(
        filename=decomposed,
        claimed_mime_type="application/pdf",
        content=PDF,
        max_bytes=1024,
    )
    patient_id = OpaqueId.new()
    document_id = OpaqueId.new()
    first = document_object_key(patient_id, document_id, result.extension)
    second = document_object_key(patient_id, document_id, result.extension)
    assert result.display_name == unicodedata.normalize("NFC", decomposed)
    assert first == second
    assert str(patient_id) in first and str(document_id) in first
    assert "रिपोर्ट" not in first and "é" not in first


def test_document_repr_does_not_expose_filename_or_storage_key() -> None:
    patient_id = OpaqueId.new()
    document_id = OpaqueId.new()
    key = document_object_key(patient_id, document_id, ".pdf")
    document = PatientDocument(
        document_id=document_id,
        patient_id=patient_id,
        display_name="private-report.pdf",
        mime_type="application/pdf",
        byte_size=len(PDF),
        object_key=key,
        sha256_digest=hashlib.sha256(PDF).hexdigest(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
    )
    rendered = repr(document)
    assert "private-report.pdf" not in rendered
    assert str(key) not in rendered
