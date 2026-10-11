"""Real PostgreSQL and HTTP verification for P4-C consent."""

from __future__ import annotations

import asyncio
import os
from collections import Counter
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import DatabaseSettings, Settings
from app.events import EventEnvelope, OutboxEventRecord, OutboxRepository
from app.main import create_app
from app.modules.consent.application import ConsentService
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.consent.infrastructure import ConsentRecord as ConsentOrmRecord
from app.modules.consent.infrastructure import PostgresConsentRepository
from app.modules.consent.public import build_consent_registration
from app.modules.identity.domain import ActorType, RoleCode
from app.modules.identity.public import build_identity_registration
from app.modules.sessions.public import build_sessions_registration
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.persistence import DatabaseRuntime
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres

NOW = datetime(2026, 10, 11, 8, tzinfo=UTC)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    async with runtime.engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE consent_records, sessions, actor_roles, actors, "
                "outbox_events CASCADE"
            )
        )
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(
                text(
                    "TRUNCATE TABLE consent_records, sessions, actor_roles, actors, "
                    "outbox_events CASCADE"
                )
            )
        await runtime.dispose()


class MutableClock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value


class FailingOutbox(OutboxRepository):
    async def enqueue(
        self,
        session: AsyncSession,
        event: EventEnvelope,
        *,
        aggregate_type: str | None = None,
        aggregate_id: OpaqueId | None = None,
        available_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> OutboxEventRecord:
        await super().enqueue(
            session,
            event,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            available_at=available_at,
            created_at=created_at,
        )
        raise RuntimeError("synthetic outbox rollback")


def _service(
    runtime: DatabaseRuntime,
    *,
    clock: MutableClock | None = None,
    outbox: OutboxRepository | None = None,
) -> ConsentService:
    return ConsentService(
        database=runtime,
        repository=PostgresConsentRepository(),
        outbox=outbox or OutboxRepository(),
        clock=clock or MutableClock(NOW),
    )


async def _create_session(client: AsyncClient) -> tuple[str, str]:
    response = await client.post("/api/v1/sessions", json={"session_type": "PSEUDONYMOUS"})
    assert response.status_code == 201
    return response.json()["session_id"], response.json()["session_token"]


def _application(runtime: DatabaseRuntime, *, actor_context: ActorContext | None = None) -> FastAPI:
    settings = Settings(
        database=DatabaseSettings(
            enabled=True, url="postgresql+psycopg://unused:unused@localhost/unused"
        ),
        _env_file=None,
    )
    registrations = (
        build_identity_registration(database=runtime),
        build_sessions_registration(settings=settings.sessions, database=runtime),
        build_consent_registration(database=runtime),
    )
    application = create_app(settings, database=runtime, module_registrations=registrations)
    if actor_context is not None:

        @application.middleware("http")
        async def inject_trusted_actor(request, call_next):  # type: ignore[no-untyped-def]
            request.state.actor_context = actor_context
            return await call_next(request)

    return application


async def test_grant_check_revoke_jsonb_and_outbox_are_postgres_authoritative(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)
    subject_id = OpaqueId.new()

    general = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("document_upload", "clinical_intake")),
        notice_version=NoticeVersion("privacy-v1"),
    )
    second = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("clinical_intake",)),
        notice_version=NoticeVersion("privacy-v1"),
    )

    assert general.scope.values == ("clinical_intake", "document_upload")
    assert second.consent_id != general.consent_id
    assert await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        required_scope=ConsentScope(("clinical_intake",)),
    )
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.REFERRAL_SHARING,
        required_scope=ConsentScope(("clinical_intake",)),
    )
    referral = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.REFERRAL_SHARING,
        scope=ConsentScope(("referral_summary",)),
        notice_version=NoticeVersion("privacy-v1"),
    )
    assert await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.REFERRAL_SHARING,
        required_scope=ConsentScope(("referral_summary",)),
    )

    revoked = await service.revoke_consent(
        consent_id=referral.consent_id, reason=RevocationReason("user_requested")
    )
    assert revoked.status is ConsentStatus.REVOKED
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.REFERRAL_SHARING,
        required_scope=ConsentScope(("referral_summary",)),
    )

    async with database_runtime.session_factory() as session:
        persisted = await session.get(ConsentOrmRecord, general.consent_id.value)
        events = (
            (
                await session.execute(
                    select(OutboxEventRecord).order_by(
                        OutboxEventRecord.created_at, OutboxEventRecord.id
                    )
                )
            )
            .scalars()
            .all()
        )
    assert persisted is not None and persisted.scope == ["clinical_intake", "document_upload"]
    assert Counter(event.event_type for event in events) == {
        "ConsentGranted": 3,
        "ConsentRevoked": 1,
    }
    assert all(event.aggregate_type == "consent" for event in events)
    assert "metadata" not in repr([event.payload for event in events])


async def test_grant_and_outbox_roll_back_together(database_runtime: DatabaseRuntime) -> None:
    service = _service(database_runtime, outbox=FailingOutbox())

    with pytest.raises(RuntimeError, match="synthetic outbox rollback"):
        await service.grant_consent(
            subject_type=ConsentSubjectType.SESSION,
            subject_id=OpaqueId.new(),
            actor_id=None,
            purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
            scope=ConsentScope(("clinical_intake",)),
            notice_version=NoticeVersion("privacy-v1"),
        )

    async with database_runtime.engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM consent_records")) == 0
        assert await connection.scalar(text("SELECT count(*) FROM outbox_events")) == 0


async def test_expiry_boundaries_and_repeat_revoke_fail_closed(
    database_runtime: DatabaseRuntime,
) -> None:
    clock = MutableClock(NOW)
    service = _service(database_runtime, clock=clock)
    subject_id = OpaqueId.new()
    expiring = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
        scope=ConsentScope(("external_processing",)),
        notice_version=NoticeVersion("privacy-v1"),
        expires_at=NOW + timedelta(minutes=1),
    )

    clock.value = NOW + timedelta(seconds=59)
    assert await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
        required_scope=ConsentScope(("external_processing",)),
    )
    clock.value = NOW + timedelta(minutes=1)
    assert not await service.has_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
        required_scope=ConsentScope(("external_processing",)),
    )
    with pytest.raises(SwasthyaSetuError) as expired:
        await service.revoke_consent(
            consent_id=expiring.consent_id, reason=RevocationReason("user_requested")
        )
    assert expired.value.code is ErrorCode.INVALID_STATE_TRANSITION

    active = await _service(database_runtime).grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=subject_id,
        actor_id=None,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("clinical_intake",)),
        notice_version=NoticeVersion("privacy-v1"),
    )
    await _service(database_runtime).revoke_consent(
        consent_id=active.consent_id, reason=RevocationReason("user_requested")
    )
    with pytest.raises(SwasthyaSetuError) as repeated:
        await _service(database_runtime).revoke_consent(
            consent_id=active.consent_id, reason=RevocationReason("user_requested")
        )
    assert repeated.value.code is ErrorCode.INVALID_STATE_TRANSITION


async def test_concurrent_revoke_has_one_success_and_one_conflict(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)
    granted = await service.grant_consent(
        subject_type=ConsentSubjectType.SESSION,
        subject_id=OpaqueId.new(),
        actor_id=None,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("clinical_intake",)),
        notice_version=NoticeVersion("privacy-v1"),
    )

    async def revoke() -> str:
        try:
            await service.revoke_consent(
                consent_id=granted.consent_id, reason=RevocationReason("user_requested")
            )
        except SwasthyaSetuError as error:
            return error.code.value
        return "SUCCESS"

    assert sorted(await asyncio.gather(revoke(), revoke())) == [
        "INVALID_STATE_TRANSITION",
        "SUCCESS",
    ]


async def test_constraints_indexes_jsonb_and_actor_fk(database_runtime: DatabaseRuntime) -> None:
    async with database_runtime.engine.connect() as connection:
        constraints: set[str] = set(
            (
                await connection.execute(
                    text(
                        "SELECT conname FROM pg_constraint "
                        "WHERE conrelid = 'consent_records'::regclass"
                    )
                )
            ).scalars()
        )
        indexes: set[str] = set(
            (
                await connection.execute(
                    text(
                        "SELECT indexname FROM pg_indexes WHERE schemaname='public' "
                        "AND tablename='consent_records'"
                    )
                )
            ).scalars()
        )
        scope_type = await connection.scalar(
            text(
                "SELECT data_type FROM information_schema.columns WHERE table_schema='public' "
                "AND table_name='consent_records' AND column_name='scope'"
            )
        )
    assert {
        "ck_consent_records_subject_type_supported",
        "ck_consent_records_purpose_supported",
        "ck_consent_records_status_supported",
        "ck_consent_records_scope_json_array",
        "ck_consent_records_expiry_after_grant",
        "fk_consent_records_actor_id_actors",
    } <= constraints
    assert {
        "ix_consent_records_subject_type_subject_id_purpose_status",
        "ix_consent_records_actor_id",
    } <= indexes
    assert scope_type == "jsonb"

    base = {
        "id": uuid4(),
        "subject": uuid4(),
        "now": NOW,
    }
    statements = (
        "INSERT INTO consent_records (id,subject_type,subject_id,purpose,scope,notice_version,"
        "status,granted_at,created_at,updated_at) VALUES "
        "(:id,'INVALID',:subject,'GENERAL_PRODUCT_USE','[]'::jsonb,'v1','GRANTED',:now,:now,:now)",
        "INSERT INTO consent_records (id,subject_type,subject_id,purpose,scope,notice_version,"
        "status,granted_at,created_at,updated_at) VALUES "
        "(:id,'SESSION',:subject,'INVALID','[]'::jsonb,'v1','GRANTED',:now,:now,:now)",
        "INSERT INTO consent_records (id,subject_type,subject_id,purpose,scope,notice_version,"
        "status,granted_at,created_at,updated_at) VALUES "
        "(:id,'SESSION',:subject,'GENERAL_PRODUCT_USE','{}'::jsonb,'v1','GRANTED',:now,:now,:now)",
        "INSERT INTO consent_records (id,subject_type,subject_id,purpose,scope,notice_version,"
        "status,granted_at,created_at,updated_at) VALUES "
        "(:id,'SESSION',:subject,'GENERAL_PRODUCT_USE','[\"clinical_intake\"]'::jsonb,"
        "'v1','INVALID',:now,:now,:now)",
        "INSERT INTO consent_records (id,subject_type,subject_id,purpose,scope,notice_version,"
        "status,granted_at,expires_at,created_at,updated_at) VALUES "
        "(:id,'SESSION',:subject,'GENERAL_PRODUCT_USE','[\"clinical_intake\"]'::jsonb,"
        "'v1','GRANTED',:now,:now,:now,:now)",
        "INSERT INTO consent_records (id,subject_type,subject_id,actor_id,purpose,scope,"
        "notice_version,status,granted_at,created_at,updated_at) VALUES "
        "(:id,'SESSION',:subject,:actor,'GENERAL_PRODUCT_USE',"
        "'[\"clinical_intake\"]'::jsonb,'v1','GRANTED',:now,:now,:now)",
    )
    for statement in statements:
        values = {**base, "id": uuid4(), "actor": uuid4()}
        with pytest.raises(IntegrityError, match="constraint|violates"):
            async with database_runtime.transaction() as session:
                await session.execute(text(statement), values)


async def test_session_http_grant_list_revoke_cross_subject_and_privacy(
    database_runtime: DatabaseRuntime,
) -> None:
    application = _application(database_runtime)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        session_a, token_a = await _create_session(client)
        session_b, token_b = await _create_session(client)
        async with database_runtime.session_factory() as database_session:
            assert await database_session.scalar(text("SELECT count(*) FROM consent_records")) == 0
        payload = {
            "subject_type": "SESSION",
            "subject_id": session_a,
            "purpose": "GENERAL_PRODUCT_USE",
            "scope": ["clinical_intake"],
            "notice_version": "privacy-v1",
        }
        granted = await client.post(
            "/api/v1/consents",
            json=payload,
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert granted.status_code == 201
        assert granted.headers["cache-control"] == "no-store"
        assert granted.json()["status"] == "GRANTED"
        consent_id = granted.json()["consent_id"]

        listed = await client.get(
            "/api/v1/consents",
            params={"subject_type": "SESSION", "subject_id": session_a},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert listed.status_code == 200
        assert [item["consent_id"] for item in listed.json()] == [consent_id]
        assert listed.headers["cache-control"] == "no-store"

        cross = await client.post(
            "/api/v1/consents",
            json={**payload, "subject_id": session_b},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert cross.status_code == 401
        assert cross.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
        assert cross.headers["cache-control"] == "no-store"

        granted_b = await client.post(
            "/api/v1/consents",
            json={**payload, "subject_id": session_b},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert granted_b.status_code == 201
        cross_list = await client.get(
            "/api/v1/consents",
            params={"subject_type": "SESSION", "subject_id": session_b},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        cross_revoke = await client.post(
            f"/api/v1/consents/{granted_b.json()['consent_id']}/revoke",
            json={"reason": "user_requested"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert cross_list.status_code == cross_revoke.status_code == 401
        assert cross_list.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
        assert cross_revoke.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        unscoped = await client.get("/api/v1/consents")
        assert unscoped.status_code == 422
        assert unscoped.headers["cache-control"] == "no-store"
        patient = await client.post(
            "/api/v1/consents",
            json={**payload, "subject_type": "PATIENT"},
        )
        assert patient.status_code == 422
        assert patient.json()["error"]["code"] == "VALIDATION_ERROR"
        forbidden = await client.post(
            "/api/v1/consents",
            json={**payload, "actor_id": str(uuid4()), "metadata": {"secret": "marker"}},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert forbidden.status_code == 422
        assert "marker" not in forbidden.text

        revoked = await client.post(
            f"/api/v1/consents/{consent_id}/revoke",
            json={"reason": "user_requested"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert revoked.status_code == 200
        assert revoked.json()["status"] == "REVOKED"
        repeated = await client.post(
            f"/api/v1/consents/{consent_id}/revoke",
            json={"reason": "user_requested"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert repeated.status_code == 409
        assert repeated.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


async def test_actor_http_self_authorization_and_cross_actor_denial(
    database_runtime: DatabaseRuntime,
) -> None:
    from app.modules.identity.application import IdentityService

    identity = IdentityService(database=database_runtime, authentication_provider=None)
    actor_a = await identity.create_actor(
        actor_type=ActorType.PATIENT,
        roles=frozenset({RoleCode.PATIENT}),
        subject_id=None,
    )
    actor_b = await identity.create_actor(
        actor_type=ActorType.PATIENT,
        roles=frozenset({RoleCode.PATIENT}),
        subject_id=None,
    )
    async with database_runtime.session_factory() as database_session:
        assert await database_session.scalar(text("SELECT count(*) FROM consent_records")) == 0
    context = ActorContext(actor_id=actor_a.actor_id, is_authenticated=True)
    actor_b_consent = await _service(database_runtime).grant_consent(
        subject_type=ConsentSubjectType.ACTOR,
        subject_id=actor_b.actor_id,
        actor_id=actor_b.actor_id,
        purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
        scope=ConsentScope(("clinical_intake",)),
        notice_version=NoticeVersion("privacy-v1"),
    )
    application = _application(database_runtime, actor_context=context)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        base = {
            "subject_type": "ACTOR",
            "purpose": "GENERAL_PRODUCT_USE",
            "scope": ["clinical_intake"],
            "notice_version": "privacy-v1",
        }
        own = await client.post(
            "/api/v1/consents", json={**base, "subject_id": str(actor_a.actor_id)}
        )
        assert own.status_code == 201
        async with database_runtime.session_factory() as session:
            persisted = await session.get(ConsentOrmRecord, own.json()["consent_id"])
        assert persisted is not None and persisted.actor_id == actor_a.actor_id.value

        listed = await client.get(
            "/api/v1/consents",
            params={"subject_type": "ACTOR", "subject_id": str(actor_a.actor_id)},
        )
        assert listed.status_code == 200
        cross = await client.post(
            "/api/v1/consents", json={**base, "subject_id": str(actor_b.actor_id)}
        )
        assert cross.status_code == 403
        assert cross.json()["error"]["code"] == "AUTHORIZATION_DENIED"

        cross_list = await client.get(
            "/api/v1/consents",
            params={"subject_type": "ACTOR", "subject_id": str(actor_b.actor_id)},
        )
        cross_revoke = await client.post(
            f"/api/v1/consents/{actor_b_consent.consent_id}/revoke",
            json={"reason": "user_requested"},
        )
        assert cross_list.status_code == cross_revoke.status_code == 403
        assert cross_list.json()["error"]["code"] == "AUTHORIZATION_DENIED"
        assert cross_revoke.json()["error"]["code"] == "AUTHORIZATION_DENIED"

        revoked = await client.post(
            f"/api/v1/consents/{own.json()['consent_id']}/revoke",
            json={"reason": "user_requested"},
        )
        assert revoked.status_code == 200
