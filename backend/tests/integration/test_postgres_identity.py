"""Real PostgreSQL verification for P4-B identity and authorization."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.config import DatabaseSettings
from app.modules.identity.application import IdentityService
from app.modules.identity.authorization import PROVIDER_MANAGE, AuthorizationService
from app.modules.identity.contracts import AuthenticatedPrincipal, AuthenticationCredential
from app.modules.identity.domain import ActorStatus, ActorType, RoleCode
from app.modules.identity.infrastructure import PostgresActorRepository
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    async with runtime.engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE sessions, actor_roles, actors CASCADE"))
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE sessions, actor_roles, actors CASCADE"))
        await runtime.dispose()


class FixedProvider:
    def __init__(self, actor_id: OpaqueId, *, mfa_verified: bool) -> None:
        self.actor_id = actor_id
        self.mfa_verified = mfa_verified

    async def authenticate(self, credential: AuthenticationCredential) -> AuthenticatedPrincipal:
        return AuthenticatedPrincipal(
            actor_id=self.actor_id,
            provider="synthetic-test-only",
            mfa_verified=self.mfa_verified,
        )


async def test_actor_roles_round_trip_authenticate_mfa_and_disable(
    database_runtime: DatabaseRuntime,
) -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    creator = IdentityService(
        database=database_runtime,
        authentication_provider=None,
        repository=PostgresActorRepository(),
        clock=lambda: now,
    )
    actor = await creator.create_actor(
        actor_type=ActorType.RESOURCE_ADMIN,
        roles=frozenset({RoleCode.RESOURCE_ADMIN}),
        subject_id=OpaqueId.new(),
        institution_id=OpaqueId.new(),
    )
    loaded = await creator.get_actor(actor.actor_id)

    assert loaded == actor
    assert actor.created_at == actor.updated_at == now
    assert actor.roles == frozenset({RoleCode.RESOURCE_ADMIN})

    without_mfa = IdentityService(
        database=database_runtime,
        authentication_provider=FixedProvider(actor.actor_id, mfa_verified=False),
    )
    context = await without_mfa.authenticate(
        AuthenticationCredential("synthetic-private-auth-credential")
    )
    assert context.is_authenticated
    assert context.roles == frozenset({"resource_admin"})
    with pytest.raises(SwasthyaSetuError) as denied:
        AuthorizationService().require_permission(context, PROVIDER_MANAGE)
    assert denied.value.code is ErrorCode.AUTHORIZATION_DENIED

    with_mfa = IdentityService(
        database=database_runtime,
        authentication_provider=FixedProvider(actor.actor_id, mfa_verified=True),
    )
    trusted = await with_mfa.authenticate(
        AuthenticationCredential("synthetic-private-auth-credential")
    )
    AuthorizationService().require_permission(trusted, PROVIDER_MANAGE)

    disabled = await creator.disable_actor(actor.actor_id)
    assert disabled.status is ActorStatus.DISABLED
    with pytest.raises(SwasthyaSetuError) as rejected:
        await with_mfa.authenticate(AuthenticationCredential("synthetic-private-auth-credential"))
    assert rejected.value.code is ErrorCode.AUTHENTICATION_REQUIRED


async def test_unknown_provider_actor_fails_as_authentication_required(
    database_runtime: DatabaseRuntime,
) -> None:
    service = IdentityService(
        database=database_runtime,
        authentication_provider=FixedProvider(OpaqueId.new(), mfa_verified=True),
    )
    with pytest.raises(SwasthyaSetuError) as error:
        await service.authenticate(AuthenticationCredential("synthetic-private-auth-credential"))
    assert error.value.code is ErrorCode.AUTHENTICATION_REQUIRED


async def test_identity_constraints_and_foreign_keys_are_enforced(
    database_runtime: DatabaseRuntime,
) -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    actor_id = uuid4()
    async with database_runtime.transaction() as session:
        await session.execute(
            text(
                "INSERT INTO actors "
                "(id, actor_type, subject_ref, institution_id, status, created_at, updated_at) "
                "VALUES (:id, 'PATIENT', NULL, NULL, 'ACTIVE', :now, :now)"
            ),
            {"id": actor_id, "now": now},
        )
        await session.execute(
            text(
                "INSERT INTO actor_roles (actor_id, role_code, created_at) "
                "VALUES (:id, 'patient', :now)"
            ),
            {"id": actor_id, "now": now},
        )

    async with database_runtime.engine.connect() as connection:
        constraints: set[str] = set(
            (
                await connection.execute(
                    text(
                        "SELECT conname FROM pg_constraint WHERE conrelid IN "
                        "('actors'::regclass, 'actor_roles'::regclass, 'sessions'::regclass)"
                    )
                )
            ).scalars()
        )
    assert {
        "ck_actors_actor_type_supported",
        "ck_actors_status_supported",
        "ck_actor_roles_role_code_supported",
        "fk_actor_roles_actor_id_actors",
        "fk_sessions_actor_id_actors",
    } <= constraints

    for statement, values in (
        (
            "INSERT INTO actors (id, actor_type, status, created_at, updated_at) "
            "VALUES (:id, 'INVALID', 'ACTIVE', :now, :now)",
            {"id": uuid4(), "now": now},
        ),
        (
            "INSERT INTO actor_roles (actor_id, role_code, created_at) "
            "VALUES (:id, 'invalid', :now)",
            {"id": actor_id, "now": now},
        ),
        (
            "UPDATE sessions SET actor_id = :actor WHERE id = (SELECT id FROM sessions LIMIT 1)",
            {"actor": uuid4()},
        ),
    ):
        if statement.startswith("UPDATE"):
            async with database_runtime.transaction() as session:
                await session.execute(
                    text(
                        "INSERT INTO sessions "
                        "(id, session_type, actor_id, patient_id, status, token_hash, "
                        "created_at, expires_at, updated_at) VALUES "
                        "(:id, 'PSEUDONYMOUS', NULL, NULL, 'ACTIVE', :hash, :now, :expires, :now)"
                    ),
                    {
                        "id": uuid4(),
                        "hash": uuid4().hex * 2,
                        "now": now,
                        "expires": datetime(2026, 10, 11, 9, tzinfo=UTC),
                    },
                )
        with pytest.raises(IntegrityError):
            async with database_runtime.transaction() as session:
                await session.execute(text(statement), values)


async def test_sessions_allow_null_actor_but_reject_unknown_actor(
    database_runtime: DatabaseRuntime,
) -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    base = {
        "id": uuid4(),
        "hash": uuid4().hex * 2,
        "now": now,
        "expires": datetime(2026, 10, 11, 9, tzinfo=UTC),
    }
    insert = text(
        "INSERT INTO sessions (id, session_type, actor_id, patient_id, status, token_hash, "
        "created_at, expires_at, updated_at) VALUES "
        "(:id, 'PSEUDONYMOUS', :actor_id, NULL, 'ACTIVE', :hash, :now, :expires, :now)"
    )
    async with database_runtime.transaction() as session:
        await session.execute(insert, {**base, "actor_id": None})
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            await session.execute(
                insert,
                {**base, "id": uuid4(), "hash": uuid4().hex * 2, "actor_id": uuid4()},
            )

    async with database_runtime.engine.connect() as connection:
        patient_fk_count = await connection.scalar(
            text(
                "SELECT count(*) FROM pg_constraint c JOIN pg_attribute a ON a.attrelid=c.conrelid "
                "AND a.attnum=ANY(c.conkey) WHERE c.conrelid='sessions'::regclass "
                "AND c.contype='f' AND a.attname='patient_id'"
            )
        )
    assert patient_fk_count == 0
