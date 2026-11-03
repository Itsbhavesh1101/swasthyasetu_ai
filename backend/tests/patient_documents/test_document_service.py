"""Document service ownership, compensation, and deletion semantics."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import UTC, datetime
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patient_documents.application import PatientDocumentService
from app.modules.patient_documents.domain import PatientDocument
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.storage import ObjectKey, ObjectMetadata, ObjectNotFoundError, ObjectStorageError
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 14, tzinfo=UTC)
PDF = b"%PDF-1.7\nsynthetic document"


class FakeDatabase:
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        yield cast(AsyncSession, object())


class FakeRepository:
    def __init__(self, *, fail_add: bool = False) -> None:
        self.values: dict[OpaqueId, PatientDocument] = {}
        self.fail_add = fail_add

    async def add(self, session: AsyncSession, document: PatientDocument) -> object:
        if self.fail_add:
            raise RuntimeError("injected metadata failure")
        self.values[document.document_id] = document
        return document

    async def get_owned(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        for_update: bool = False,
    ) -> PatientDocument | None:
        value = self.values.get(document_id)
        return value if value is not None and value.patient_id == patient_id else None

    async def list_active(
        self, session: AsyncSession, *, patient_id: OpaqueId
    ) -> tuple[PatientDocument, ...]:
        return tuple(
            value
            for value in self.values.values()
            if value.patient_id == patient_id and value.deleted_at is None
        )

    async def mark_deleted(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        deleted_at: datetime,
    ) -> PatientDocument | None:
        value = await self.get_owned(session, patient_id=patient_id, document_id=document_id)
        if value is None:
            return None
        if value.deleted_at is None:
            value = replace(value, deleted_at=deleted_at)
            self.values[document_id] = value
        return value


class FakeStorage:
    def __init__(self) -> None:
        self.values: dict[ObjectKey, bytes] = {}
        self.fail_delete = False

    async def put_bytes(
        self, key: ObjectKey, data: bytes | bytearray | memoryview, *, overwrite: bool = False
    ) -> ObjectMetadata:
        content = bytes(data)
        import hashlib

        self.values[key] = content
        return ObjectMetadata(key, len(content), hashlib.sha256(content).hexdigest())

    async def get_bytes(self, key: ObjectKey) -> bytes:
        if key not in self.values:
            raise ObjectNotFoundError
        return self.values[key]

    async def exists(self, key: ObjectKey) -> bool:
        return key in self.values

    async def delete(self, key: ObjectKey) -> None:
        if self.fail_delete:
            raise ObjectStorageError("injected delete failure")
        if key not in self.values:
            raise ObjectNotFoundError
        del self.values[key]


def service(repository: FakeRepository, storage: FakeStorage) -> PatientDocumentService:
    return PatientDocumentService(
        database=cast(DatabaseRuntime, FakeDatabase()),
        repository=repository,
        storage=storage,
        max_bytes=1024,
        clock=lambda: NOW,
    )


async def test_upload_read_list_and_cross_patient_denial() -> None:
    repository = FakeRepository()
    storage = FakeStorage()
    patient_id = OpaqueId.new()
    document = await service(repository, storage).upload(
        patient_id=patient_id,
        filename="report.pdf",
        mime_type="application/pdf",
        content=PDF,
    )
    assert await service(repository, storage).list_documents(patient_id=patient_id) == (document,)
    assert (
        await service(repository, storage).read(
            patient_id=patient_id, document_id=document.document_id
        )
    ).content == PDF
    with pytest.raises(ApplicationError) as cross:
        await service(repository, storage).read(
            patient_id=OpaqueId.new(), document_id=document.document_id
        )
    assert cross.value.code is ErrorCode.RESOURCE_NOT_FOUND


async def test_metadata_failure_compensates_stored_object() -> None:
    repository = FakeRepository(fail_add=True)
    storage = FakeStorage()
    with pytest.raises(RuntimeError, match="injected metadata failure"):
        await service(repository, storage).upload(
            patient_id=OpaqueId.new(),
            filename="report.pdf",
            mime_type="application/pdf",
            content=PDF,
        )
    assert storage.values == {}


async def test_delete_is_idempotent_and_storage_failure_stays_non_observable() -> None:
    repository = FakeRepository()
    storage = FakeStorage()
    patient_id = OpaqueId.new()
    documents = service(repository, storage)
    document = await documents.upload(
        patient_id=patient_id,
        filename="report.pdf",
        mime_type="application/pdf",
        content=PDF,
    )
    storage.fail_delete = True
    with pytest.raises(DependencyError) as failed_delete:
        await documents.delete(patient_id=patient_id, document_id=document.document_id)
    assert failed_delete.value.code is ErrorCode.DEPENDENCY_UNAVAILABLE
    assert await documents.list_documents(patient_id=patient_id) == ()
    with pytest.raises(ApplicationError):
        await documents.read(patient_id=patient_id, document_id=document.document_id)
    storage.fail_delete = False
    await documents.delete(patient_id=patient_id, document_id=document.document_id)
    await documents.delete(patient_id=patient_id, document_id=document.document_id)
    assert storage.values == {}
