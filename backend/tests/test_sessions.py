"""P4-A session domain, token, module, and HTTP boundary tests."""

import base64
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import SessionsSettings, Settings
from app.main import create_app
from app.modules.sessions.application import (
    SessionCreationResult,
    generate_session_token,
    hash_session_token,
    normalize_utc,
)
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.modules.sessions.public import (
    SESSIONS_CLOSE,
    SESSIONS_CREATE,
    SESSIONS_MANIFEST,
    SESSIONS_READ,
    SESSIONS_VALIDATE,
)
from app.shared.modules import ModuleId
from app.shared.types import OpaqueId


def test_session_domain_is_framework_independent_and_secret_free() -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    session = Session(
        session_id=OpaqueId.new(),
        session_type=SessionType.PSEUDONYMOUS,
        language_preference="en",
        status=SessionStatus.ACTIVE,
        created_at=now,
        expires_at=now + timedelta(hours=1),
        closed_at=None,
        updated_at=now,
    )

    assert {value.value for value in SessionType} == {
        "PSEUDONYMOUS",
        "AUTHENTICATED",
        "KIOSK",
        "CLINICIAN",
        "ADMIN",
        "RESEARCH",
    }
    assert {value.value for value in SessionStatus} == {
        "ACTIVE",
        "EXPIRED",
        "CLOSED",
        "REVOKED",
    }
    assert "token" not in repr(session).lower()
    assert session.__class__.__module__ == "app.modules.sessions.domain"
    with pytest.raises(FrozenInstanceError):
        session.status = SessionStatus.CLOSED  # type: ignore[misc]


def test_token_uses_urlsafe_32_byte_input_and_hashes_to_sha256_hex() -> None:
    tokens = {generate_session_token() for _ in range(32)}

    assert len(tokens) == 32
    assert all(
        token
        and set(token) <= set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        for token in tokens
    )
    assert all(len(hash_session_token(token)) == 64 for token in tokens)
    assert all(set(hash_session_token(token)) <= set("0123456789abcdef") for token in tokens)
    assert all(
        len(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))) == 32 for token in tokens
    )


def test_creation_result_repr_excludes_raw_token() -> None:
    marker = "synthetic-session-token-marker"
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    session = Session(
        session_id=OpaqueId.new(),
        session_type=SessionType.KIOSK,
        language_preference=None,
        status=SessionStatus.ACTIVE,
        created_at=now,
        expires_at=now + timedelta(minutes=30),
        closed_at=None,
        updated_at=now,
    )

    result = SessionCreationResult(session=session, session_token=marker)

    assert marker not in repr(result)


def test_clock_normalization_rejects_naive_and_converts_offsets() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        normalize_utc("clock", datetime(2026, 10, 11, 8))

    value = datetime(2026, 10, 11, 13, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    assert normalize_utc("clock", value) == datetime(2026, 10, 11, 8, tzinfo=UTC)


def test_sessions_manifest_and_capabilities_are_explicit() -> None:
    assert SESSIONS_MANIFEST.module_id == ModuleId("sessions")
    assert SESSIONS_MANIFEST.api_prefixes == ("/sessions",)
    assert SESSIONS_MANIFEST.configuration_keys == ("sessions",)
    assert SESSIONS_MANIFEST.data_ownership == ("sessions",)
    assert SESSIONS_MANIFEST.feature_flags == ()
    assert {
        str(key.identifier)
        for key in (SESSIONS_CREATE, SESSIONS_READ, SESSIONS_CLOSE, SESSIONS_VALIDATE)
    } == {
        "sessions.create",
        "sessions.read",
        "sessions.close",
        "sessions.validate",
    }


def test_default_application_registers_sessions_and_seals_capabilities() -> None:
    application = create_app(Settings(_env_file=None))

    assert application.state.module_registry.module_ids == (
        "ai_orchestration",
        "clinical_intake",
        "consent",
        "encounters",
        "identity",
        "patients",
        "provenance",
        "sessions",
    )
    assert application.state.module_registry.is_sealed is True
    assert application.state.capability_registry.is_sealed is True
    for key in (SESSIONS_CREATE, SESSIONS_READ, SESSIONS_CLOSE, SESSIONS_VALIDATE):
        assert application.state.capability_registry.resolve(key) is not None


async def test_database_disabled_application_exposes_create_as_safe_503() -> None:
    application = create_app(Settings(_env_file=None))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sessions",
            json={"session_type": "PSEUDONYMOUS", "language_preference": "en"},
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("session_type", ["AUTHENTICATED", "CLINICIAN", "ADMIN", "RESEARCH"])
async def test_identity_bound_create_types_are_rejected(session_type: str) -> None:
    application = create_app(Settings(_env_file=None))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/sessions", json={"session_type": session_type})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_identity_fields_are_forbidden_in_create_body() -> None:
    marker = "synthetic-private-name"
    application = create_app(Settings(_env_file=None))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sessions",
            json={"session_type": "PSEUDONYMOUS", "name": marker},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert marker not in response.text
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "authorization",
    [None, "Basic value", "Bearer", "Bearer ", "bearer value", "Bearer two parts"],
)
async def test_missing_or_malformed_bearer_is_rejected_without_database(
    authorization: str | None,
) -> None:
    application = create_app(Settings(_env_file=None))
    transport = ASGITransport(app=application)
    headers = {} if authorization is None else {"Authorization": authorization}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/sessions/00000000-0000-4000-8000-000000000001",
            headers=headers,
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert response.headers["cache-control"] == "no-store"


def test_sessions_settings_defaults_and_bounds() -> None:
    settings = SessionsSettings()

    assert settings.pseudonymous_ttl_minutes == 60
    assert settings.kiosk_ttl_minutes == 30
    for value in (0, -1, 10081):
        with pytest.raises(ValueError):
            SessionsSettings(pseudonymous_ttl_minutes=value)


def test_openapi_exposes_only_versioned_safe_session_contracts() -> None:
    application = create_app(Settings(_env_file=None))
    schema = application.openapi()
    rendered = repr(schema)

    assert "/api/v1/sessions" in schema["paths"]
    assert "/api/v1/sessions/{session_id}" in schema["paths"]
    assert "/api/v1/sessions/{session_id}/close" in schema["paths"]
    assert "/sessions" not in schema["paths"]
    assert "token_hash" not in rendered
    assert "recovery_token_hash" not in rendered
