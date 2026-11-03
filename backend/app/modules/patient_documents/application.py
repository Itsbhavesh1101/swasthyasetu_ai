"""Patient-owned document metadata and storage orchestration."""

import hashlib
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime

from app.modules.patient_documents.contracts import PatientDocumentRepository
from app.modules.patient_documents.domain import DocumentContent, PatientDocument
from app.modules.patient_documents.validation import document_object_key, validate_document
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.storage import ObjectNotFoundError, ObjectStorageError, ObjectStoragePort
from app.shared.types import OpaqueId, utc_now


class PatientDocumentService:
    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        repository: PatientDocumentRepository,
        storage: ObjectStoragePort | None,
        max_bytes: int,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._database = database
        self._repository = repository
        self._storage = storage
        self._max_bytes = max_bytes
        self._clock = clock

    async def upload(
        self, *, patient_id: OpaqueId, filename: str, mime_type: str, content: bytes
    ) -> PatientDocument:
        database, storage = self._dependencies()
        validated = validate_document(
            filename=filename,
            claimed_mime_type=mime_type,
            content=content,
            max_bytes=self._max_bytes,
        )
        document_id = OpaqueId.new()
        document = PatientDocument(
            document_id=document_id,
            patient_id=patient_id,
            display_name=validated.display_name,
            mime_type=validated.mime_type,
            byte_size=len(validated.content),
            object_key=document_object_key(patient_id, document_id, validated.extension),
            sha256_digest=validated.sha256_digest,
            created_at=self._now(),
        )
        metadata = await storage.put_bytes(document.object_key, validated.content)
        if (
            metadata.key != document.object_key
            or metadata.size_bytes != document.byte_size
            or metadata.sha256 != document.sha256_digest
        ):
            with suppress(ObjectStorageError):
                await storage.delete(document.object_key)
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Document storage verification failed.",
            )
        try:
            async with database.transaction() as transaction:
                await self._repository.add(transaction, document)
        except Exception:
            with suppress(ObjectStorageError):
                await storage.delete(document.object_key)
            raise
        return document

    async def list_documents(self, *, patient_id: OpaqueId) -> tuple[PatientDocument, ...]:
        database, _ = self._dependencies()
        async with database.transaction() as transaction:
            return await self._repository.list_active(transaction, patient_id=patient_id)

    async def read(self, *, patient_id: OpaqueId, document_id: OpaqueId) -> DocumentContent:
        database, storage = self._dependencies()
        async with database.transaction() as transaction:
            document = await self._repository.get_owned(
                transaction, patient_id=patient_id, document_id=document_id
            )
        if document is None or document.deleted_at is not None:
            raise self._not_found()
        try:
            content = await storage.get_bytes(document.object_key)
        except ObjectNotFoundError as exc:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Document content is temporarily unavailable.",
                cause=exc,
            ) from exc
        if (
            len(content) != document.byte_size
            or len(content) > self._max_bytes
            or hashlib.sha256(content).hexdigest() != document.sha256_digest
        ):
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Document content verification failed.",
            )
        return DocumentContent(document=document, content=content)

    async def delete(self, *, patient_id: OpaqueId, document_id: OpaqueId) -> None:
        database, storage = self._dependencies()
        async with database.transaction() as transaction:
            document = await self._repository.mark_deleted(
                transaction,
                patient_id=patient_id,
                document_id=document_id,
                deleted_at=self._now(),
            )
        if document is None:
            raise self._not_found()
        if document.deleted_at is not None:
            try:
                await storage.delete(document.object_key)
            except ObjectNotFoundError:
                return
            except ObjectStorageError as exc:
                raise DependencyError(
                    code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                    message="Document cleanup is temporarily unavailable.",
                    cause=exc,
                ) from exc

    def _dependencies(self) -> tuple[DatabaseRuntime, ObjectStoragePort]:
        if self._database is None or self._storage is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Patient document storage is unavailable.",
            )
        return self._database, self._storage

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("patient document clock must be timezone-aware")
        return value.astimezone(UTC)

    @staticmethod
    def _not_found() -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message="The requested document was not found.",
        )
