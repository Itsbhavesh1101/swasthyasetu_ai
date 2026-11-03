"""Stable composition exports for patient document storage."""

from app.adapters.storage import LocalFilesystemObjectStorage
from app.config import PatientDocumentSettings
from app.modules.patient_documents.application import PatientDocumentService
from app.modules.patient_documents.infrastructure import PostgresPatientDocumentRepository
from app.shared.persistence import DatabaseRuntime


def build_patient_document_service(
    *, database: DatabaseRuntime | None, settings: PatientDocumentSettings
) -> PatientDocumentService:
    storage = (
        LocalFilesystemObjectStorage(settings.root)
        if settings.enabled and settings.root is not None
        else None
    )
    return PatientDocumentService(
        database=database,
        repository=PostgresPatientDocumentRepository(),
        storage=storage,
        max_bytes=settings.max_bytes,
    )


__all__ = ["PatientDocumentService", "build_patient_document_service"]
