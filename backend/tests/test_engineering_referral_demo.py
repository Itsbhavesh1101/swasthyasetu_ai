"""Regression coverage for the local/test-only P13 discovery preview."""

from dataclasses import asdict
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app
from app.modules.engineering_referral_demo.api import EngineeringReferralDiscoveryView
from app.modules.engineering_referral_demo.application import EngineeringReferralDemoService

NOW = datetime(2026, 11, 2, 18, tzinfo=UTC)
PATH = "/api/v1/engineering-demo/referral-discovery"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_referral_demo_wave4",)},
    )


def test_projection_composes_p13_contracts_without_selection_or_external_effect() -> None:
    result = EngineeringReferralDemoService().project(clock=NOW)

    assert result.classification == "ENGINEERING_SYNTHETIC"
    assert result.authority == "ENGINEERING_ONLY"
    assert result.route_disposition == "SYMBOLIC_MATCH"
    assert result.route_reason == "EXACT_SYMBOLIC_MATCH"
    assert result.provider_verification == "UNVERIFIED"
    assert result.resource_verification == "UNVERIFIED"
    assert result.referral_state_model == "OFFERED"
    assert result.provider_selected is False
    assert result.referral_created is False
    assert result.sharing_consent == "NOT_REQUESTED"
    assert result.contacts_available is False
    assert result.external_delivery is False
    assert result.notification_delivery is False
    rendered = repr(result)
    assert "syn_provider_college_demo" not in rendered
    assert "syn_referral_college_demo" not in rendered
    assert "artifact_hash" not in rendered


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
    assert body["provider_selected"] is False
    assert body["referral_created"] is False
    assert {"provider_id", "resource_id", "referral_id", "source_id", "contact"}.isdisjoint(body)
    rendered = str(body).casefold()
    assert "http" not in rendered
    assert "@" not in rendered


def test_transport_rejects_forged_verification_selection_consent_and_delivery() -> None:
    value = asdict(EngineeringReferralDemoService().project(clock=NOW))
    for mutation in (
        {"authority": "PRODUCTION"},
        {"provider_verification": "VERIFIED"},
        {"source_verification": "VERIFIED"},
        {"provider_selected": True},
        {"referral_created": True},
        {"sharing_consent": "GRANTED"},
        {"external_delivery": True},
        {"notification_delivery": True},
        {"unexpected_contact": "+00-0000000"},
    ):
        with pytest.raises(ValidationError):
            EngineeringReferralDiscoveryView.model_validate({**value, **mutation})
