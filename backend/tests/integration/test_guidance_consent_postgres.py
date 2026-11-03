"""Real PostgreSQL proof for account-bound external-AI consent and guidance."""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.adapters.ai.fake_guidance import FakeGuidanceProvider
from app.config import DatabaseSettings, Settings
from app.main import create_app
from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderResult,
    SourceAnnotation,
)
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)
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


async def test_exact_actor_consent_gates_grounded_guidance_and_revocation(
    database_runtime: DatabaseRuntime,
) -> None:
    result = GuidanceProviderResult(
        answer="Gentle hydration habits may support general wellbeing.",
        citations=(GuidanceCitation(title="WHO", url="https://who.int/advice"),),
        annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
        retrieved_at=NOW,
    )
    provider = FakeGuidanceProvider((result,))
    application = create_app(
        Settings(
            database=DatabaseSettings(
                enabled=True,
                url=str(database_runtime.engine.url),
            ),
            _env_file=None,
        ),
        database=database_runtime,
        guidance_provider_factory=lambda: provider,
    )
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        registered = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "guidance@example.com",
                "display_name": "Guidance Patient",
                "password": "correct horse battery staple",
            },
        )
        headers = {"Authorization": f"Bearer {registered.json()['session_token']}"}
        blocked = await client.post(
            "/api/v1/guidance/ayurveda",
            headers=headers,
            json={"question": "How can I support hydration?"},
        )
        assert blocked.json()["outcome"] == "CONSENT_REQUIRED"
        assert provider.requests == ()

        granted = await client.post("/api/v1/guidance/consent", headers=headers)
        assert granted.status_code == 201
        answered = await client.post(
            "/api/v1/guidance/ayurveda",
            headers=headers,
            json={"question": "How can I support hydration?"},
        )
        assert answered.json()["outcome"] == "ANSWERED"
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

    async with database_runtime.transaction() as transaction:
        rows = (
            (
                await transaction.execute(
                    text(
                        "SELECT purpose, scope, notice_version, status "
                        "FROM consent_records ORDER BY created_at"
                    )
                )
            )
            .mappings()
            .all()
        )
    assert rows == [
        {
            "purpose": "EXTERNAL_AI_PROCESSING",
            "scope": ["ayurvedic_guidance"],
            "notice_version": "external-ai-v1",
            "status": "REVOKED",
        }
    ]
