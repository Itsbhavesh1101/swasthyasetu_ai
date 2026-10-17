"""P4-B identity, authentication, authorization, and transport tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest
from fastapi import APIRouter, Depends, FastAPI, Request
from httpx import ASGITransport, AsyncClient

from app.api.security.authorization import require_permission, require_self_subject
from app.main import create_app
from app.modules.identity.application import IdentityService, normalize_utc
from app.modules.identity.authorization import (
    AUDIT_READ,
    PATIENT_READ_SELF,
    PROVIDER_MANAGE,
    RESEARCH_RUN,
    AuthorizationService,
)
from app.modules.identity.contracts import AuthenticationCredential
from app.modules.identity.domain import Actor, ActorStatus, ActorType, PermissionCode, RoleCode
from app.modules.identity.public import (
    IDENTITY_AUTHENTICATE,
    IDENTITY_AUTHORIZE,
    IDENTITY_CURRENT_ACTOR,
    IDENTITY_MANIFEST,
    build_identity_registration,
)
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.modules import ModuleId
from app.shared.security import ActorContext
from app.shared.types import OpaqueId


def _context(
    *roles: RoleCode,
    actor_type: ActorType = ActorType.PATIENT,
    subject_id: OpaqueId | None = None,
    authenticated: bool = True,
    mfa_verified: bool = False,
) -> ActorContext:
    return ActorContext(
        actor_id=OpaqueId.new() if authenticated else None,
        actor_type=actor_type.value if authenticated else None,
        roles=frozenset(role.value for role in roles),
        subject_id=subject_id,
        is_authenticated=authenticated,
        mfa_verified=mfa_verified,
    )


def test_actor_domain_is_explicit_immutable_and_privacy_safe() -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    actor = Actor(
        actor_id=OpaqueId.new(),
        actor_type=ActorType.CLINICIAN,
        roles=frozenset({RoleCode.CLINICIAN}),
        subject_id=None,
        institution_id=OpaqueId.new(),
        status=ActorStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )

    assert {value.value for value in ActorType} == {
        "PATIENT",
        "PSEUDONYMOUS_USER",
        "CAREGIVER",
        "CLINICIAN",
        "COUNSELLOR",
        "TRIAGE_STAFF",
        "RESOURCE_ADMIN",
        "CLINICAL_REVIEWER",
        "SYSTEM_ADMIN",
        "RESEARCHER",
        "SERVICE_ACCOUNT",
    }
    assert {value.value for value in ActorStatus} == {"ACTIVE", "DISABLED"}
    assert {value.value for value in RoleCode} == {
        "patient",
        "pseudonymous_user",
        "clinician",
        "resource_admin",
        "clinical_reviewer",
        "system_admin",
        "researcher",
    }
    assert not any(field in repr(actor).lower() for field in ("email", "phone", "password"))
    with pytest.raises(FrozenInstanceError):
        actor.status = ActorStatus.DISABLED  # type: ignore[misc]


@pytest.mark.parametrize(
    "value",
    ["patient:read:self", "encounter:read:assigned", "provider:manage", "audit:read"],
)
def test_permission_code_accepts_exact_canonical_grammar(value: str) -> None:
    assert str(PermissionCode(value)) == value


@pytest.mark.parametrize("value", ["*", "admin:*", "*:read", "Admin:read", " patient:read"])
def test_permission_code_rejects_wildcards_and_noncanonical_values(value: str) -> None:
    with pytest.raises(ValueError):
        PermissionCode(value)


def test_actor_context_defaults_to_anonymous_and_has_immutable_safe_fields() -> None:
    context = ActorContext()

    assert context.actor_id is None
    assert context.actor_type is None
    assert context.subject_id is None
    assert context.institution_id is None
    assert context.session_id is None
    assert context.request_id is None
    assert context.roles == frozenset()
    assert context.is_authenticated is context.mfa_verified is False
    assert "credential" not in repr(context).lower()
    with pytest.raises(AttributeError):
        context.roles.add("system_admin")  # type: ignore[attr-defined]


def test_authentication_credential_is_bounded_immutable_and_redacted() -> None:
    marker = "synthetic-private-auth-credential"
    credential = AuthenticationCredential(marker)

    assert credential.value == marker
    assert marker not in repr(credential)
    with pytest.raises(FrozenInstanceError):
        credential.value = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError):
        AuthenticationCredential("")
    with pytest.raises(ValueError):
        AuthenticationCredential("x" * 8193)


def test_actor_type_never_implies_role_or_permission() -> None:
    service = AuthorizationService()

    assert not service.has_permission(_context(actor_type=ActorType.SYSTEM_ADMIN), PROVIDER_MANAGE)
    assert not service.has_permission(_context(actor_type=ActorType.PATIENT), PATIENT_READ_SELF)
    assert not service.has_permission(_context(actor_type=ActorType.CAREGIVER), PATIENT_READ_SELF)


def test_role_permission_policy_is_explicit_and_has_no_wildcard_superuser() -> None:
    service = AuthorizationService()
    admin = _context(RoleCode.SYSTEM_ADMIN, actor_type=ActorType.SYSTEM_ADMIN, mfa_verified=True)

    assert service.has_permission(admin, AUDIT_READ)
    assert service.has_permission(admin, PROVIDER_MANAGE)
    assert not service.has_permission(admin, RESEARCH_RUN)
    assert service.policy_version == "p5c-v1"
    with pytest.raises(TypeError):
        service.role_permissions[RoleCode.SYSTEM_ADMIN] = frozenset()  # type: ignore[index]


@pytest.mark.parametrize(
    "role", [RoleCode.RESOURCE_ADMIN, RoleCode.CLINICAL_REVIEWER, RoleCode.SYSTEM_ADMIN]
)
def test_administrative_roles_require_trusted_mfa(role: RoleCode) -> None:
    service = AuthorizationService()
    permission = next(iter(service.role_permissions[role]))

    with pytest.raises(SwasthyaSetuError) as denied:
        service.require_permission(_context(role, mfa_verified=False), permission)
    assert denied.value.code is ErrorCode.AUTHORIZATION_DENIED
    service.require_permission(_context(role, mfa_verified=True), permission)


def test_authorization_distinguishes_unauthenticated_and_forbidden() -> None:
    service = AuthorizationService()

    with pytest.raises(SwasthyaSetuError) as anonymous:
        service.require_permission(ActorContext(), PROVIDER_MANAGE)
    with pytest.raises(SwasthyaSetuError) as forbidden:
        service.require_permission(_context(RoleCode.PATIENT), PROVIDER_MANAGE)
    assert anonymous.value.code is ErrorCode.AUTHENTICATION_REQUIRED
    assert forbidden.value.code is ErrorCode.AUTHORIZATION_DENIED


def test_self_subject_authorization_denies_cross_subject_access() -> None:
    service = AuthorizationService()
    subject_a, subject_b = OpaqueId.new(), OpaqueId.new()
    actor = _context(RoleCode.PATIENT, subject_id=subject_a)

    service.require_self_subject(actor, PATIENT_READ_SELF, subject_a)
    with pytest.raises(SwasthyaSetuError) as denied:
        service.require_self_subject(actor, PATIENT_READ_SELF, subject_b)
    assert denied.value.code is ErrorCode.AUTHORIZATION_DENIED


def test_identity_manifest_and_default_composition_are_explicit_and_router_free() -> None:
    registration = build_identity_registration(database=None)
    app = create_app()

    assert IDENTITY_MANIFEST.module_id == ModuleId("identity")
    assert IDENTITY_MANIFEST.version == 1
    assert IDENTITY_MANIFEST.api_prefixes == ()
    assert IDENTITY_MANIFEST.data_ownership == ("actors", "actor_roles")
    assert registration.routers == ()
    assert app.state.module_registry.module_ids == (
        "clinical_intake",
        "consent",
        "encounters",
        "identity",
        "patients",
        "provenance",
        "sessions",
    )
    assert app.state.module_registry.is_sealed
    for key in (IDENTITY_AUTHENTICATE, IDENTITY_CURRENT_ACTOR, IDENTITY_AUTHORIZE):
        assert app.state.capability_registry.resolve(key) is not None
    assert not any(path.startswith("/api/v1/identity") for path in app.openapi()["paths"])


async def test_unconfigured_authentication_provider_fails_honestly() -> None:
    service = IdentityService(database=None, authentication_provider=None)

    with pytest.raises(SwasthyaSetuError) as error:
        await service.authenticate(AuthenticationCredential("synthetic-private-auth-credential"))
    assert error.value.code is ErrorCode.DEPENDENCY_UNAVAILABLE


async def test_provider_rejection_and_exception_are_safe(caplog: pytest.LogCaptureFixture) -> None:
    class RejectingProvider:
        async def authenticate(self, credential: AuthenticationCredential) -> None:
            return None

    class FailingProvider:
        async def authenticate(self, credential: AuthenticationCredential) -> None:
            raise RuntimeError("synthetic-provider-secret-detail")

    for provider, expected in (
        (RejectingProvider(), ErrorCode.AUTHENTICATION_REQUIRED),
        (FailingProvider(), ErrorCode.DEPENDENCY_UNAVAILABLE),
    ):
        service = IdentityService(database=None, authentication_provider=provider)
        with pytest.raises(SwasthyaSetuError) as error:
            await service.authenticate(
                AuthenticationCredential("synthetic-private-auth-credential")
            )
        assert error.value.code is expected
        assert "synthetic" not in error.value.message
    assert "synthetic-private-auth-credential" not in caplog.text
    assert "synthetic-provider-secret-detail" not in caplog.text


def test_identity_clock_rejects_naive_and_normalizes_offsets() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        normalize_utc("identity clock", datetime(2026, 10, 11, 8))
    offset = datetime(2026, 10, 11, 13, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    assert normalize_utc("identity clock", offset) == datetime(2026, 10, 11, 8, tzinfo=UTC)


def _synthetic_guard_app(context: ActorContext | None) -> FastAPI:
    app = create_app(module_registrations=(build_identity_registration(database=None),))
    router = APIRouter()

    @router.get("/privileged", dependencies=[Depends(require_permission(PROVIDER_MANAGE))])
    async def privileged() -> dict[str, bool]:
        return {"allowed": True}

    @router.get("/subjects/{subject_id}")
    async def subject(
        subject_id: str,
        _: None = Depends(require_self_subject(PATIENT_READ_SELF, "subject_id")),
    ) -> dict[str, str]:
        return {"subject_id": subject_id}

    if context is not None:

        @app.middleware("http")
        async def inject_test_context(request: Request, call_next):  # type: ignore[no-untyped-def]
            request.state.actor_context = context
            return await call_next(request)

    app.include_router(router)
    return app


@pytest.mark.parametrize(
    ("context", "expected"),
    [
        (None, 401),
        (_context(RoleCode.PATIENT), 403),
        (_context(RoleCode.RESOURCE_ADMIN, mfa_verified=False), 403),
        (_context(RoleCode.RESOURCE_ADMIN, mfa_verified=True), 200),
    ],
)
async def test_real_permission_guard_enforces_auth_permission_and_mfa(
    context: ActorContext | None, expected: int
) -> None:
    app = _synthetic_guard_app(context)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/privileged",
            headers={"X-Actor-ID": str(OpaqueId.new()), "X-Role": "system_admin", "X-MFA": "true"},
        )

    assert response.status_code == expected
    if expected != 200:
        assert response.json()["error"]["code"] in {
            "AUTHENTICATION_REQUIRED",
            "AUTHORIZATION_DENIED",
        }


async def test_real_self_subject_guard_prevents_basic_idor() -> None:
    subject_a, subject_b = OpaqueId.new(), OpaqueId.new()
    app = _synthetic_guard_app(_context(RoleCode.PATIENT, subject_id=subject_a))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        own = await client.get(f"/subjects/{subject_a}")
        cross = await client.get(f"/subjects/{subject_b}")

    assert own.status_code == 200
    assert cross.status_code == 403
    assert cross.json()["error"]["code"] == "AUTHORIZATION_DENIED"
