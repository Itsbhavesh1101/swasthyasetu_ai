"""Authenticated consent and guidance HTTP contract."""

from datetime import UTC, datetime

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.errors import register_error_handlers
from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentRecord,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.self_care.guidance_api import build_guidance_router
from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    SourceAnnotation,
)
from app.modules.self_care.guidance_policy import GuidancePolicy
from app.modules.self_care.guidance_service import GuidanceService
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


class Authenticator:
    def __init__(self, actor_id: OpaqueId) -> None:
        self.actor_id = actor_id

    async def authenticate(self, token: str) -> ActorContext:
        assert token == "patient-token"
        return ActorContext(
            actor_id=self.actor_id,
            actor_type="PATIENT",
            subject_id=OpaqueId.new(),
            is_authenticated=True,
        )


class Consent:
    def __init__(self, actor_id: OpaqueId) -> None:
        self.actor_id = actor_id
        self.record: ConsentRecord | None = None

    async def has_active_consent(self, **_: object) -> bool:
        return self.record is not None and self.record.status is ConsentStatus.GRANTED

    async def grant_consent(self, **values: object) -> ConsentRecord:
        self.record = ConsentRecord(
            consent_id=OpaqueId.new(),
            subject_type=ConsentSubjectType.ACTOR,
            subject_id=self.actor_id,
            actor_id=self.actor_id,
            purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
            scope=ConsentScope(("ayurvedic_guidance",)),
            notice_version=NoticeVersion("external-ai-v1"),
            status=ConsentStatus.GRANTED,
            granted_at=NOW,
            revoked_at=None,
            revocation_reason=None,
            expires_at=None,
            metadata=None,
            created_at=NOW,
            updated_at=NOW,
        )
        return self.record

    async def list_consents(self, **_: object) -> tuple[ConsentRecord, ...]:
        return () if self.record is None else (self.record,)

    async def revoke_consent(self, **_: object) -> ConsentRecord:
        assert self.record is not None
        self.record = ConsentRecord(
            consent_id=self.record.consent_id,
            subject_type=self.record.subject_type,
            subject_id=self.record.subject_id,
            actor_id=self.record.actor_id,
            purpose=self.record.purpose,
            scope=self.record.scope,
            notice_version=self.record.notice_version,
            status=ConsentStatus.REVOKED,
            granted_at=self.record.granted_at,
            revoked_at=NOW,
            revocation_reason=RevocationReason("user_requested"),
            expires_at=None,
            metadata=None,
            created_at=self.record.created_at,
            updated_at=NOW,
        )
        return self.record


class Provider:
    def __init__(self) -> None:
        self.requests: list[GuidanceProviderRequest] = []

    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        self.requests.append(request)
        return GuidanceProviderResult(
            answer="Gentle hydration habits may support general wellbeing.",
            citations=(GuidanceCitation(title="WHO", url="https://who.int/advice"),),
            annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
            retrieved_at=NOW,
        )


async def test_consent_lifecycle_gates_exactly_one_provider_request() -> None:
    actor_id = OpaqueId.new()
    consent = Consent(actor_id)
    provider = Provider()
    service = GuidanceService(
        consent=consent,
        provider_factory=lambda: provider,
        policy=GuidancePolicy(("who.int",)),
    )
    application = FastAPI()
    register_error_handlers(application)
    application.include_router(
        build_guidance_router(
            service=service,
            consent=consent,  # type: ignore[arg-type]
            authenticator=Authenticator(actor_id),
        ),
        prefix="/api/v1",
    )
    headers = {"Authorization": "Bearer patient-token"}
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        blocked = await client.post(
            "/api/v1/guidance/ayurveda",
            headers=headers,
            json={"question": "How can I support hydration?"},
        )
        assert blocked.json() == {
            "outcome": "CONSENT_REQUIRED",
            "answer": None,
            "citations": [],
            "retrieved_at": None,
        }
        assert provider.requests == []

        granted = await client.post("/api/v1/guidance/consent", headers=headers)
        assert granted.status_code == 201
        assert granted.json()["active"] is True
        answered = await client.post(
            "/api/v1/guidance/ayurveda",
            headers=headers,
            json={"question": "How can I support hydration?"},
        )
        assert answered.json()["outcome"] == "ANSWERED"
        assert answered.json()["citations"] == [{"title": "WHO", "url": "https://who.int/advice"}]
        assert len(provider.requests) == 1

        revoked = await client.delete("/api/v1/guidance/consent", headers=headers)
        assert revoked.json()["active"] is False
        blocked_again = await client.post(
            "/api/v1/guidance/ayurveda",
            headers=headers,
            json={"question": "How can I support hydration?"},
        )
        assert blocked_again.json()["outcome"] == "CONSENT_REQUIRED"
        assert len(provider.requests) == 1


async def test_authentication_runs_before_malformed_guidance_body() -> None:
    actor_id = OpaqueId.new()
    consent = Consent(actor_id)
    application = FastAPI()
    register_error_handlers(application)
    application.include_router(
        build_guidance_router(
            service=GuidanceService(
                consent=consent,
                provider_factory=Provider,
                policy=GuidancePolicy(("who.int",)),
            ),
            consent=consent,  # type: ignore[arg-type]
            authenticator=Authenticator(actor_id),
        ),
        prefix="/api/v1",
    )
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/guidance/ayurveda",
            content=b"not-json",
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 401
