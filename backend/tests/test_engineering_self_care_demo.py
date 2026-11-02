"""Regression coverage for the local/test-only P15 eligibility preview."""

from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.config.settings import Environment
from app.main import create_app
from app.modules.engineering_self_care_demo.api import EngineeringSelfCarePreviewView
from app.modules.engineering_self_care_demo.application import EngineeringSelfCareDemoService
from app.modules.self_care.eligibility import EligibilityContractCode, EligibilityContractError

PATH = "/api/v1/engineering-demo/self-care-preview"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_self_care_demo_wave6",)},
    )


def test_projection_composes_safety_first_and_unapproved_knowledge_contracts() -> None:
    result = EngineeringSelfCareDemoService(environment=Environment.TEST).project()

    assert result.knowledge_pack_state == "TEST_ONLY_UNAPPROVED"
    assert result.knowledge_item_review_state == "TEST_ONLY_UNAPPROVED"
    assert result.source_verification == "UNVERIFIED"
    assert result.candidate_outcome == "SYNTHETIC_ENGINEERING_CANDIDATE"
    assert result.candidate_count == 1
    assert result.blocked_outcome == "SYNTHETIC_BLOCKED"
    assert result.blocked_reason == "SYNTHETIC_SAFETY_BLOCK"
    assert result.blocked_candidate_count == 0
    assert result.safety_block_preserved is True
    assert result.clinical_eligibility_established is False
    assert result.guidance_text_available is False
    assert result.guidance_display_authorized is False
    assert result.rag_invoked is False
    assert result.patient_data_processed is False
    assert result.external_delivery is False


def test_service_fails_closed_when_directly_constructed_for_protected_environment() -> None:
    service = EngineeringSelfCareDemoService(environment=Environment.PRODUCTION)

    with pytest.raises(EligibilityContractError) as caught:
        service.project()

    assert caught.value.code is EligibilityContractCode.PROTECTED_ENVIRONMENT


def test_endpoint_is_default_off_and_never_registered_in_protected_environments() -> None:
    assert PATH not in create_app(Settings(_env_file=None)).openapi()["paths"]
    assert PATH in create_app(enabled_settings()).openapi()["paths"]
    assert PATH in create_app(enabled_settings(environment="test")).openapi()["paths"]
    for environment in ("staging", "pilot", "production"):
        assert PATH not in create_app(enabled_settings(environment=environment)).openapi()["paths"]


def test_endpoint_returns_minimized_no_store_preview() -> None:
    response = TestClient(create_app(enabled_settings())).get(PATH)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["guidance_text_available"] is False
    assert body["guidance_display_authorized"] is False
    assert {"patient_id", "session_id", "guidance_text", "remedy", "source_hash"}.isdisjoint(body)
    rendered = str(body).casefold()
    assert "http" not in rendered
    assert "@" not in rendered


def test_transport_rejects_forged_approval_or_effect() -> None:
    value = asdict(EngineeringSelfCareDemoService(environment=Environment.TEST).project())
    for mutation in (
        {"authority": "CLINICAL"},
        {"verification": "VERIFIED"},
        {"knowledge_pack_state": "APPROVED"},
        {"source_verification": "VERIFIED"},
        {"safety_block_preserved": False},
        {"clinical_eligibility_established": True},
        {"guidance_text_available": True},
        {"guidance_display_authorized": True},
        {"rag_invoked": True},
        {"patient_data_processed": True},
        {"external_delivery": True},
        {"unexpected_remedy": "private-canary"},
    ):
        with pytest.raises(ValidationError):
            EngineeringSelfCarePreviewView.model_validate({**value, **mutation})
