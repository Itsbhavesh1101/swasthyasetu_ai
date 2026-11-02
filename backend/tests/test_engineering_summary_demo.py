"""Regression coverage for the local/test-only P10 engineering draft."""

from dataclasses import asdict
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app
from app.modules.engineering_summary_demo.api import EngineeringSummaryResultView
from app.modules.engineering_summary_demo.application import EngineeringSummaryDemoService
from app.modules.summaries.domain import CANONICAL_SECTION_ORDER

NOW = datetime(2026, 11, 2, 12, tzinfo=UTC)
PATH = "/api/v1/engineering-demo/summary-review"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_summary_demo_wave3",)},
    )


def test_projection_composes_p10_contracts_without_identity_or_clinical_authority() -> None:
    result = EngineeringSummaryDemoService().project(clock=NOW)

    assert result.status == "DRAFT"
    assert result.classification == "ENGINEERING_ONLY"
    assert result.review_state == "REVIEW_REQUIRED"
    assert result.freshness == "STALE"
    assert result.affected_sections == ("HPI",)
    assert result.drift_reasons == ("NEW_SOURCE",)
    assert tuple(section.section for section in result.sections) == tuple(
        section.value for section in CANONICAL_SECTION_ORDER
    )
    assert result.sections[0].assertions == ("SYNTHETIC_REPORTED_COMPLAINT",)
    assert result.sections[0].readiness == "UNVERIFIED"
    assert all(section.readiness == "UNKNOWN" for section in result.sections[1:])
    assert not result.can_edit and not result.can_confirm and not result.can_reject
    rendered = repr(result)
    assert "00000000-0000" not in rendered
    assert "patient_id" not in rendered


def test_demo_endpoint_is_default_off_and_protected_environment_off() -> None:
    assert PATH not in create_app(Settings(_env_file=None)).openapi()["paths"]
    assert PATH in create_app(enabled_settings()).openapi()["paths"]
    assert PATH in create_app(enabled_settings(environment="test")).openapi()["paths"]
    for environment in ("staging", "pilot", "production"):
        assert PATH not in create_app(enabled_settings(environment=environment)).openapi()["paths"]


def test_demo_endpoint_returns_minimized_no_store_draft() -> None:
    response = TestClient(create_app(enabled_settings())).get(PATH)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["status"] == "DRAFT"
    assert body["source_access"] == "NOT_AUTHORIZED"
    assert body["external_egress"] is False
    assert {"summary_id", "encounter_id", "patient_id", "actor_id", "created_at"}.isdisjoint(body)
    assert "diagnosis" not in str(body).casefold()


def test_transport_rejects_forged_authority_and_malformed_projection() -> None:
    value = asdict(EngineeringSummaryDemoService().project(clock=NOW))
    for mutation in (
        {"classification": "CLINICAL"},
        {"source_access": "AUTHORIZED"},
        {"status": "CONFIRMED"},
        {"can_confirm": True},
        {"can_edit": True},
        {"external_egress": True},
        {"affected_sections": ("ALLERGIES",)},
        {"unexpected_actor_id": "private-canary"},
    ):
        with pytest.raises(ValidationError):
            EngineeringSummaryResultView.model_validate({**value, **mutation})

    reversed_sections = tuple(reversed(value["sections"]))
    with pytest.raises(ValidationError):
        EngineeringSummaryResultView.model_validate({**value, "sections": reversed_sections})
