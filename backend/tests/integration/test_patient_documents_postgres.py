"""Real PostgreSQL and controlled-filesystem patient document proofs."""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage import LocalFilesystemObjectStorage
from app.config import DatabaseSettings, PatientAccountSettings, PatientDocumentSettings, Settings
from app.main import create_app
from app.modules.identity.infrastructure import PostgresActorRepository
from app.modules.patient_accounts.application import PatientAccountService
from app.modules.patient_accounts.contracts import RegisterPatient
from app.modules.patient_accounts.domain import DisplayName, EmailAddress, RawPassword
from app.modules.patient_accounts.infrastructure import PostgresPatientAccountRepository
from app.modules.patient_accounts.passwords import Argon2PasswordHasher
from app.modules.patient_documents.application import PatientDocumentService
from app.modules.patient_documents.domain import PatientDocument
from app.modules.patient_documents.infrastructure import (
    PatientDocumentRecord,
    PostgresPatientDocumentRepository,
)
from app.modules.patients.infrastructure import PostgresPatientRepository
from app.modules.sessions.infrastructure import PostgresSessionRepository
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 11, 3, 14, tzinfo=UTC)
PDF = b"%PDF-1.7\nsynthetic integration document"
TRUNCATE = text(
    "TRUNCATE TABLE patient_documents, patient_accounts, intake_answers, "
    "questionnaire_instances, clinical_intakes, observations, allergies, medications, "
    "clinical_fact_provenance, clinical_facts, encounters, patient_identifiers, "
    "patient_demographics, patients, consent_records, sessions, actor_roles, actors, "
    "outbox_events CASCADE"
)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=url))
    async with runtime.engine.begin() as connection:
        await connection.execute(TRUNCATE)
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(TRUNCATE)
        await runtime.dispose()


async def patient_account(runtime: DatabaseRuntime) -> tuple[OpaqueId, OpaqueId]:
    accounts = PatientAccountService(
        database=runtime,
        settings=PatientAccountSettings(),
        accounts=PostgresPatientAccountRepository(),
        actors=PostgresActorRepository(),
        patients=PostgresPatientRepository(),
        sessions=PostgresSessionRepository(),
        passwords=Argon2PasswordHasher(),
        clock=lambda: NOW,
        token_factory=lambda: "synthetic-document-session-token",
    )
    registered = await accounts.register(
        RegisterPatient(
            email=EmailAddress("documents@example.com"),
            display_name=DisplayName("Document Patient"),
            password=RawPassword("correct horse battery staple"),
            preferred_language="en",
        )
    )
    return registered.account.patient_id, registered.account.actor_id


async def test_document_metadata_and_content_round_trip_then_soft_delete(
    database_runtime: DatabaseRuntime, tmp_path: Path
) -> None:
    patient_id, _ = await patient_account(database_runtime)
    storage = LocalFilesystemObjectStorage(tmp_path / "vault")
    service = PatientDocumentService(
        database=database_runtime,
        repository=PostgresPatientDocumentRepository(),
        storage=storage,
        max_bytes=1024,
        clock=lambda: NOW,
    )

    document = await service.upload(
        patient_id=patient_id,
        filename="synthetic-report.pdf",
        mime_type="application/pdf",
        content=PDF,
    )
    assert await service.list_documents(patient_id=patient_id) == (document,)
    assert (
        await service.read(patient_id=patient_id, document_id=document.document_id)
    ).content == PDF
    assert "synthetic-report" not in str(document.object_key)

    await service.delete(patient_id=patient_id, document_id=document.document_id)
    await service.delete(patient_id=patient_id, document_id=document.document_id)
    assert await service.list_documents(patient_id=patient_id) == ()
    assert await storage.exists(document.object_key) is False
    async with database_runtime.transaction() as transaction:
        persisted = await transaction.get(PatientDocumentRecord, document.document_id.value)
    assert persisted is not None and persisted.deleted_at == NOW


class FailingRepository(PostgresPatientDocumentRepository):
    async def add(self, session: AsyncSession, document: PatientDocument) -> PatientDocumentRecord:
        await super().add(session, document)
        raise RuntimeError("injected metadata failure")


async def test_metadata_failure_rolls_back_row_and_compensates_object(
    database_runtime: DatabaseRuntime, tmp_path: Path
) -> None:
    patient_id, _ = await patient_account(database_runtime)
    root = tmp_path / "vault"
    service = PatientDocumentService(
        database=database_runtime,
        repository=FailingRepository(),
        storage=LocalFilesystemObjectStorage(root),
        max_bytes=1024,
        clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="injected metadata failure"):
        await service.upload(
            patient_id=patient_id,
            filename="synthetic-report.pdf",
            mime_type="application/pdf",
            content=PDF,
        )

    async with database_runtime.transaction() as transaction:
        count = await transaction.scalar(select(func.count()).select_from(PatientDocumentRecord))
    assert count == 0
    assert list(root.rglob("*.pdf")) == []


async def test_document_http_authentication_upload_download_idor_and_delete(
    database_runtime: DatabaseRuntime, tmp_path: Path
) -> None:
    settings = Settings(
        patient_documents=PatientDocumentSettings(
            enabled=True,
            root=tmp_path / "http-vault",
            max_bytes=1024,
        ),
        _env_file=None,
    )
    application = create_app(settings, database=database_runtime)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        unauthenticated = await client.post(
            f"/api/v1/patients/{OpaqueId.new()}/documents",
            content=b"not even multipart",
            headers={"Content-Type": "multipart/form-data; boundary=broken"},
        )
        assert unauthenticated.status_code == 401

        account = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "http-documents@example.com",
                "display_name": "HTTP Document Patient",
                "password": "correct horse battery staple",
            },
        )
        bearer = {"Authorization": f"Bearer {account.json()['session_token']}"}
        current = await client.get("/api/v1/accounts/me", headers=bearer)
        patient_id = current.json()["patient_id"]
        path = f"/api/v1/patients/{patient_id}/documents"

        uploaded = await client.post(
            path,
            headers=bearer,
            files={"file": ("synthetic report.pdf", PDF, "application/pdf")},
        )
        assert uploaded.status_code == 201
        payload = uploaded.json()
        assert set(payload) == {
            "document_id",
            "display_name",
            "mime_type",
            "byte_size",
            "created_at",
        }
        assert uploaded.headers["cache-control"] == "no-store"
        document_id = payload["document_id"]

        listed = await client.get(path, headers=bearer)
        downloaded = await client.get(f"{path}/{document_id}/content", headers=bearer)
        cross = await client.get(
            f"/api/v1/patients/{OpaqueId.new()}/documents/{document_id}/content",
            headers=bearer,
        )
        assert listed.status_code == 200 and len(listed.json()["items"]) == 1
        assert downloaded.status_code == 200 and downloaded.content == PDF
        assert downloaded.headers["content-type"].startswith("application/pdf")
        assert (
            "filename*=UTF-8''synthetic%20report.pdf" in downloaded.headers["content-disposition"]
        )
        assert downloaded.headers["x-content-type-options"] == "nosniff"
        assert cross.status_code == 403

        oversized = await client.post(
            path,
            headers=bearer,
            files={
                "file": (
                    "large.pdf",
                    b"%PDF-" + b"x" * 1024,
                    "application/pdf",
                )
            },
        )
        assert oversized.status_code == 413

        deleted = await client.delete(f"{path}/{document_id}", headers=bearer)
        unavailable = await client.get(f"{path}/{document_id}/content", headers=bearer)
        assert deleted.status_code == 204
        assert unavailable.status_code == 404
