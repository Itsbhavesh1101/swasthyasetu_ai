"""Authenticated patient document-vault HTTP boundary."""

from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response, status
from pydantic import BaseModel, ConfigDict
from starlette.datastructures import UploadFile

from app.api.security.authorization import require_self_subject
from app.api.security.patient_authentication import PatientAuthenticator, authenticate_patient
from app.modules.identity.authorization import PATIENT_READ_SELF, PATIENT_WRITE_SELF
from app.modules.patient_documents.application import PatientDocumentService
from app.modules.patient_documents.domain import PatientDocument
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId


class DocumentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: UUID
    display_name: str
    mime_type: str
    byte_size: int
    created_at: str


class DocumentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: tuple[DocumentResponse, ...]


def document_view(value: PatientDocument) -> DocumentResponse:
    return DocumentResponse(
        document_id=value.document_id.value,
        display_name=value.display_name,
        mime_type=value.mime_type,
        byte_size=value.byte_size,
        created_at=value.created_at.isoformat(),
    )


def build_patient_documents_router(
    *,
    service: PatientDocumentService,
    authenticator: PatientAuthenticator,
    max_bytes: int,
) -> APIRouter:
    async def require_patient(
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> None:
        await authenticate_patient(request, authorization, authenticator=authenticator)

    router = APIRouter(
        prefix="/patients/{patient_id}/documents",
        tags=["patient-documents"],
        dependencies=[Depends(require_patient)],
    )

    @router.get(
        "",
        response_model=DocumentListResponse,
        dependencies=[Depends(require_self_subject(PATIENT_READ_SELF, "patient_id"))],
    )
    async def list_documents(patient_id: UUID, response: Response) -> DocumentListResponse:
        response.headers["Cache-Control"] = "no-store"
        items = await service.list_documents(patient_id=OpaqueId(patient_id))
        return DocumentListResponse(items=tuple(document_view(item) for item in items))

    @router.post(
        "",
        response_model=DocumentResponse,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_self_subject(PATIENT_WRITE_SELF, "patient_id"))],
    )
    async def upload_document(
        patient_id: UUID, request: Request, response: Response
    ) -> DocumentResponse:
        response.headers["Cache-Control"] = "no-store"
        try:
            async with request.form(
                max_files=1,
                max_fields=0,
                max_part_size=max_bytes + 1,
            ) as form:
                if set(form) != {"file"} or not isinstance(form["file"], UploadFile):
                    raise ValueError("exactly one file part is required")
                upload = form["file"]
                content = await upload.read(max_bytes + 1)
                if await upload.read(1) or len(content) > max_bytes:
                    raise ApplicationError(
                        code=ErrorCode.PAYLOAD_TOO_LARGE,
                        message="The document exceeds the upload limit.",
                    )
                filename = upload.filename or ""
                mime_type = upload.content_type or ""
        except ApplicationError:
            raise
        except Exception as exc:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The document upload is invalid.",
                cause=exc,
            ) from exc
        try:
            document = await service.upload(
                patient_id=OpaqueId(patient_id),
                filename=filename,
                mime_type=mime_type,
                content=content,
            )
        except ValueError as exc:
            raise ApplicationError(
                code=ErrorCode.UNSUPPORTED_MEDIA_TYPE,
                message="The document type or filename is not supported.",
                cause=exc,
            ) from exc
        return document_view(document)

    @router.get(
        "/{document_id}/content",
        dependencies=[Depends(require_self_subject(PATIENT_READ_SELF, "patient_id"))],
    )
    async def download_document(patient_id: UUID, document_id: UUID) -> Response:
        content = await service.read(
            patient_id=OpaqueId(patient_id), document_id=OpaqueId(document_id)
        )
        encoded = quote(content.document.display_name, safe="")
        response = Response(content=content.content, media_type=content.document.mime_type)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Disposition"] = (
            f"attachment; filename=\"document\"; filename*=UTF-8''{encoded}"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @router.delete(
        "/{document_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_self_subject(PATIENT_WRITE_SELF, "patient_id"))],
    )
    async def delete_document(patient_id: UUID, document_id: UUID, response: Response) -> None:
        response.headers["Cache-Control"] = "no-store"
        await service.delete(patient_id=OpaqueId(patient_id), document_id=OpaqueId(document_id))

    return router
