"""Transaction-scoped patient document persistence contracts."""

from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patient_documents.domain import PatientDocument
from app.shared.types import OpaqueId


class PatientDocumentRepository(Protocol):
    async def add(self, session: AsyncSession, document: PatientDocument) -> object: ...
    async def get_owned(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        for_update: bool = False,
    ) -> PatientDocument | None: ...
    async def list_active(
        self, session: AsyncSession, *, patient_id: OpaqueId
    ) -> tuple[PatientDocument, ...]: ...
    async def mark_deleted(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        deleted_at: datetime,
    ) -> PatientDocument | None: ...
