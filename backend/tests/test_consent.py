"""P4-C consent domain, event, module, and transport contract tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.security.bearer import parse_bearer
from app.config import Settings
from app.main import create_app
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.consent.events import consent_granted_event, consent_revoked_event
from app.modules.consent.public import (
    CONSENT_CHECK,
    CONSENT_GRANT,
    CONSENT_LIST,
    CONSENT_MANIFEST,
    CONSENT_READ,
    CONSENT_REVOKE,
)
from app.shared.errors import ErrorCode, SwasthyaSetuError
from app.shared.modules import ModuleId
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 11, 8, tzinfo=UTC)


def _record(**overrides: object) -> ConsentRecord:
    values: dict[str, object] = {
        "consent_id": OpaqueId.new(),
        "subject_type": ConsentSubjectType.SESSION,
        "subject_id": OpaqueId.new(),
        "actor_id": None,
        "purpose": ConsentPurpose.GENERAL_PRODUCT_USE,
        "scope": ConsentScope(("clinical_intake", "document_upload")),
        "notice_version": NoticeVersion("privacy-v1"),
        "status": ConsentStatus.GRANTED,
        "granted_at": NOW,
        "revoked_at": None,
        "revocation_reason": None,
        "expires_at": None,
        "metadata": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return ConsentRecord(**values)  # type: ignore[arg-type]


def test_canonical_consent_enums_are_exact_and_framework_independent() -> None:
    assert {value.value for value in ConsentPurpose} == {
        "GENERAL_PRODUCT_USE",
        "EXTERNAL_AI_PROCESSING",
        "REFERRAL_SHARING",
        "ABDM_EXCHANGE",
        "RESEARCH_USE",
        "CAREGIVER_ACCESS",
    }
    assert {value.value for value in ConsentStatus} == {
        "GRANTED",
        "REVOKED",
        "EXPIRED",
        "SUPERSEDED",
    }
    assert {value.value for value in ConsentSubjectType} == {"SESSION", "ACTOR", "PATIENT"}
    assert ConsentRecord.__module__ == "app.modules.consent.domain"


def test_scope_is_nonempty_unique_bounded_nonwildcard_and_deterministic() -> None:
    scope = ConsentScope(("document_upload", "clinical_intake"))

    assert scope.values == ("clinical_intake", "document_upload")
    assert scope.covers(ConsentScope(("clinical_intake",))) is True
    assert scope.covers(ConsentScope(("referral_summary",))) is False
    with pytest.raises(FrozenInstanceError):
        scope.values = ()  # type: ignore[misc]

    for invalid in (
        (),
        ("clinical_intake", "clinical_intake"),
        ("*",),
        ("referral_*",),
        ("Clinical_Intake",),
        (" leading",),
        ("a" * 65,),
        tuple(f"scope_{index}" for index in range(33)),
    ):
        with pytest.raises(ValueError):
            ConsentScope(invalid)


def test_notice_version_and_revocation_reason_are_bounded_machine_values() -> None:
    for value in ("privacy-v1", "privacy_v2", "notice.2026-10", "V1"):
        assert str(NoticeVersion(value)) == value
    assert str(RevocationReason("user_requested")) == "user_requested"

    for value in (
        "",
        "privacy v1",
        " privacy-v1",
        "privacy-v1 ",
        "privacy/v1",
        "privacy\nv1",
        "privacy\u00a0v1",
        "नोटिस-v1",
        "x" * 65,
    ):
        with pytest.raises(ValueError):
            NoticeVersion(value)
    for value in ("", "User requested", "user-requested", "x" * 65):
        with pytest.raises(ValueError):
            RevocationReason(value)


async def test_invalid_notice_version_returns_safe_validation_error() -> None:
    marker = "private notice value"
    application = create_app(Settings(_env_file=None))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/consents",
            json={
                "subject_type": "SESSION",
                "subject_id": str(OpaqueId.new()),
                "purpose": "GENERAL_PRODUCT_USE",
                "scope": ["clinical_intake"],
                "notice_version": marker,
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert marker not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_record_enforces_lifecycle_expiry_and_utc_invariants() -> None:
    granted = _record()
    assert granted.status is ConsentStatus.GRANTED
    with pytest.raises(FrozenInstanceError):
        granted.status = ConsentStatus.REVOKED  # type: ignore[misc]

    revoked = _record(
        status=ConsentStatus.REVOKED,
        revoked_at=NOW + timedelta(minutes=1),
        revocation_reason=RevocationReason("user_requested"),
        updated_at=NOW + timedelta(minutes=1),
    )
    assert revoked.revocation_reason == RevocationReason("user_requested")

    with pytest.raises(ValueError, match="GRANTED"):
        _record(revocation_reason=RevocationReason("user_requested"))
    with pytest.raises(ValueError, match="REVOKED"):
        _record(status=ConsentStatus.REVOKED)
    with pytest.raises(ValueError, match="expires_at"):
        _record(expires_at=NOW)
    with pytest.raises(ValueError, match="timezone-aware"):
        _record(granted_at=datetime(2026, 10, 11, 8))

    offset = timezone(timedelta(hours=5, minutes=30))
    normalized = _record(
        granted_at=datetime(2026, 10, 11, 13, 30, tzinfo=offset),
        created_at=datetime(2026, 10, 11, 13, 30, tzinfo=offset),
        updated_at=datetime(2026, 10, 11, 13, 30, tzinfo=offset),
    )
    assert normalized.granted_at == NOW
    assert normalized.granted_at.tzinfo is UTC


def test_consent_events_are_versioned_minimal_and_privacy_safe() -> None:
    actor_id = OpaqueId.new()
    record = _record(actor_id=actor_id)
    granted = consent_granted_event(record)
    revoked_record = _record(
        actor_id=actor_id,
        status=ConsentStatus.REVOKED,
        revoked_at=NOW + timedelta(minutes=1),
        revocation_reason=RevocationReason("user_requested"),
        updated_at=NOW + timedelta(minutes=1),
    )
    revoked = consent_revoked_event(revoked_record)

    assert str(granted.event_type) == "ConsentGranted"
    assert str(revoked.event_type) == "ConsentRevoked"
    assert granted.event_version == revoked.event_version == 1
    assert granted.actor_ref == revoked.actor_ref == str(actor_id)
    assert granted.to_dict()["payload"] == {
        "consent_id": str(record.consent_id),
        "subject_type": "SESSION",
        "subject_id": str(record.subject_id),
        "purpose": "GENERAL_PRODUCT_USE",
        "scope": ["clinical_intake", "document_upload"],
        "notice_version": "privacy-v1",
        "status": "GRANTED",
    }
    revoked_payload = revoked.to_dict()["payload"]
    assert isinstance(revoked_payload, dict)
    assert revoked_payload["revocation_reason"] == "user_requested"
    assert "metadata" not in repr(granted.to_dict()["payload"])


def test_consent_manifest_and_capabilities_are_explicit() -> None:
    assert CONSENT_MANIFEST.module_id == ModuleId("consent")
    assert CONSENT_MANIFEST.version == 1
    assert CONSENT_MANIFEST.api_prefixes == ("/consents",)
    assert CONSENT_MANIFEST.data_ownership == ("consent_records",)
    assert CONSENT_MANIFEST.events_published == ("ConsentGranted", "ConsentRevoked")
    assert {str(value) for value in CONSENT_MANIFEST.required_capabilities} == {"sessions.validate"}
    assert {
        str(key.identifier)
        for key in (CONSENT_GRANT, CONSENT_READ, CONSENT_LIST, CONSENT_REVOKE, CONSENT_CHECK)
    } == {
        "consent.grant",
        "consent.read",
        "consent.list",
        "consent.revoke",
        "consent.check",
    }


def test_default_application_registers_consent_and_exposes_no_public_check_route() -> None:
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
    for key in (CONSENT_GRANT, CONSENT_READ, CONSENT_LIST, CONSENT_REVOKE, CONSENT_CHECK):
        assert application.state.capability_registry.resolve(key) is not None
    paths = application.openapi()["paths"]
    assert "/api/v1/consents" in paths
    assert "/api/v1/consents/{consent_id}/revoke" in paths
    assert "/api/v1/consents/check" not in paths


@pytest.mark.parametrize(
    "value",
    [None, "", "Basic value", "Bearer", "Bearer ", "bearer value", "Bearer two parts"],
)
def test_shared_bearer_parser_rejects_malformed_values(value: str | None) -> None:
    with pytest.raises(SwasthyaSetuError) as error:
        parse_bearer(value)
    assert error.value.code is ErrorCode.AUTHENTICATION_REQUIRED


def test_shared_bearer_parser_returns_exact_token_without_echoing_it() -> None:
    marker = "synthetic-private-session-token"
    assert parse_bearer(f"Bearer {marker}") == marker


async def test_actor_subject_requires_trusted_context_and_database_availability() -> None:
    actor_id = OpaqueId.new()
    payload = {
        "subject_type": "ACTOR",
        "subject_id": str(actor_id),
        "purpose": "GENERAL_PRODUCT_USE",
        "scope": ["clinical_intake"],
        "notice_version": "privacy-v1",
    }
    anonymous = create_app(Settings(_env_file=None))
    anonymous_transport = ASGITransport(app=anonymous)
    async with AsyncClient(transport=anonymous_transport, base_url="http://test") as client:
        denied = await client.post("/api/v1/consents", json=payload)
    assert denied.status_code == 401
    assert denied.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert denied.headers["cache-control"] == "no-store"

    trusted = create_app(Settings(_env_file=None))

    @trusted.middleware("http")
    async def inject_actor(request, call_next):  # type: ignore[no-untyped-def]
        request.state.actor_context = ActorContext(actor_id=actor_id, is_authenticated=True)
        return await call_next(request)

    trusted_transport = ASGITransport(app=trusted)
    async with AsyncClient(transport=trusted_transport, base_url="http://test") as client:
        unavailable = await client.post("/api/v1/consents", json=payload)
    assert unavailable.status_code == 503
    assert unavailable.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert unavailable.headers["cache-control"] == "no-store"


def test_openapi_has_no_check_delete_update_or_client_owned_fields() -> None:
    schema = create_app(Settings(_env_file=None)).openapi()
    paths = schema["paths"]

    assert set(paths["/api/v1/consents"]) == {"get", "post"}
    assert set(paths["/api/v1/consents/{consent_id}/revoke"]) == {"post"}
    assert "/api/v1/consents/check" not in paths
    grant_schema = repr(schema["components"]["schemas"]["GrantConsentRequest"])
    for forbidden in (
        "actor_id",
        "status",
        "granted_at",
        "revoked_at",
        "expires_at",
        "metadata",
    ):
        assert forbidden not in grant_schema
