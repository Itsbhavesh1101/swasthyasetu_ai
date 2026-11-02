"""Regression coverage for the local/test-only P14 policy-mechanics preview."""

from dataclasses import asdict
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.config.settings import Environment
from app.main import create_app
from app.modules.engineering_mannsetu_demo.api import EngineeringMannSetuPreviewView
from app.modules.engineering_mannsetu_demo.application import EngineeringMannSetuDemoService
from app.modules.mental_health.policy import SyntheticPolicyCode, SyntheticPolicyError

NOW = datetime(2026, 11, 2, 18, tzinfo=UTC)
PATH = "/api/v1/engineering-demo/mannsetu-preview"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_mannsetu_demo_wave5",)},
    )


def test_projection_composes_p14_contracts_with_symbolic_override_only() -> None:
    result = EngineeringMannSetuDemoService(environment=Environment.TEST).project(clock=NOW)

    assert result.extraction_status == "SYNTHETIC_PARSED"
    assert result.extractor_signal == "SYN_MH_SIGNAL_ALPHA"
    assert result.backstop_outcome == "SYNTHETIC_MATCHED"
    assert result.backstop_signal == "SYN_MH_SIGNAL_DELTA"
    assert result.precedence == "SYNTHETIC_OVERRIDE"
    assert result.route == "SYNTHETIC_ROUTE_GAMMA"
    assert result.reason_code == "SYN_MH_POLICY_REASON_DELTA"
    assert result.verification == "UNVERIFIED"
    assert result.clinical_meaning_assigned is False
    assert result.mental_health_assessment_performed is False
    assert result.patient_data_processed is False
    assert result.resource_contacts_available is False
    assert result.referral_created is False
    assert result.external_delivery is False


def test_service_fails_closed_when_directly_constructed_for_protected_environment() -> None:
    service = EngineeringMannSetuDemoService(environment=Environment.PRODUCTION)

    with pytest.raises(SyntheticPolicyError) as caught:
        service.project(clock=NOW)

    assert caught.value.code is SyntheticPolicyCode.PROTECTED_ENVIRONMENT


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
    assert body["mental_health_assessment_performed"] is False
    assert body["resource_contacts_available"] is False
    assert {"patient_id", "session_id", "narrative", "contact", "policy_hash"}.isdisjoint(body)
    rendered = str(body).casefold()
    assert "http" not in rendered
    assert "@" not in rendered


def test_transport_rejects_forged_authority_or_effect() -> None:
    value = asdict(EngineeringMannSetuDemoService(environment=Environment.TEST).project(clock=NOW))
    for mutation in (
        {"authority": "CLINICAL"},
        {"verification": "VERIFIED"},
        {"clinical_meaning_assigned": True},
        {"mental_health_assessment_performed": True},
        {"patient_data_processed": True},
        {"resource_contacts_available": True},
        {"referral_created": True},
        {"external_delivery": True},
        {"route": "ROUTE_C"},
        {"unexpected_contact": "+00-0000000"},
    ):
        with pytest.raises(ValidationError):
            EngineeringMannSetuPreviewView.model_validate({**value, **mutation})
