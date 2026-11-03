"""Stable composition exports for patient document storage."""

from fastapi import APIRouter

from app.adapters.storage import LocalFilesystemObjectStorage
from app.api.security.patient_authentication import PatientAuthenticator
from app.config import PatientDocumentSettings
from app.modules.patient_documents.application import PatientDocumentService
from app.modules.patient_documents.infrastructure import PostgresPatientDocumentRepository
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
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


PATIENT_DOCUMENTS_SERVICE = CapabilityKey[PatientDocumentService](
    CapabilityIdentifier("patient_documents.service")
)
PATIENT_DOCUMENTS_MANIFEST = ModuleManifest(
    module_id=ModuleId("patient_documents"),
    version=1,
    provided_capabilities=frozenset({PATIENT_DOCUMENTS_SERVICE.identifier}),
    api_prefixes=("/patients/{patient_id}/documents",),
    required_permissions=("patient:read:self", "patient:write:self"),
    configuration_keys=("patient_documents",),
    data_ownership=("patient_documents",),
)


def build_patient_documents_registration(
    *,
    service: PatientDocumentService,
    authenticator: PatientAuthenticator,
    max_bytes: int,
) -> ModuleRegistration[APIRouter]:
    from app.modules.patient_documents.api import build_patient_documents_router

    return ModuleRegistration(
        manifest=PATIENT_DOCUMENTS_MANIFEST,
        routers=(
            build_patient_documents_router(
                service=service,
                authenticator=authenticator,
                max_bytes=max_bytes,
            ),
        ),
        capability_bindings=(PATIENT_DOCUMENTS_SERVICE.bind(service),),
    )


__all__ = [
    "PATIENT_DOCUMENTS_MANIFEST",
    "PATIENT_DOCUMENTS_SERVICE",
    "PatientDocumentService",
    "build_patient_document_service",
    "build_patient_documents_registration",
]
