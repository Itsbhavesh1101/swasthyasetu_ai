"""Regression coverage for the local/test-only P11 engineering receipt."""

from dataclasses import asdict
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app
from app.modules.engineering_document_demo.api import EngineeringDocumentResultView
from app.modules.engineering_document_demo.application import EngineeringDocumentDemoService

NOW = datetime(2026, 11, 2, 12, tzinfo=UTC)
PATH = "/api/v1/engineering-demo/document-review"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_document_demo_wave2",)},
    )


def test_projection_composes_p11_contracts_without_content_or_authority() -> None:
    result = EngineeringDocumentDemoService().project(clock=NOW)

    assert result.status == "NEEDS_REVIEW"
    assert result.lifecycle == (
        "UPLOADED",
        "VALIDATING",
        "ACCEPTED",
        "QUEUED",
        "PROCESSING",
        "NEEDS_REVIEW",
    )
    assert result.processing_status == "SUCCEEDED"
    assert result.document_type == "LAB_REPORT"
    assert result.processor_disposition == "NOOP_ABSTAIN"
    assert result.candidate_disposition == "UNCONFIRMED"
    assert result.structural_match == "STRUCTURALLY_MATCHED_UNCONFIRMED"
    assert result.source_access == "NOT_VERIFIED"
    assert result.external_egress is False
    rendered = repr(result)
    assert "SYNTHETIC_DOCUMENT_TOKEN" not in rendered
    assert "00000000-0000" not in rendered


def test_demo_endpoint_is_default_off_and_protected_environment_off() -> None:
    assert PATH not in create_app(Settings(_env_file=None)).openapi()["paths"]
    assert PATH in create_app(enabled_settings()).openapi()["paths"]
    assert PATH in create_app(enabled_settings(environment="test")).openapi()["paths"]
    for environment in ("staging", "pilot", "production"):
        assert PATH not in create_app(enabled_settings(environment=environment)).openapi()["paths"]


def test_demo_endpoint_returns_minimized_no_store_receipt() -> None:
    response = TestClient(create_app(enabled_settings())).get(PATH)

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["classification"] == "ENGINEERING_ONLY"
    assert body["external_egress"] is False
    assert {
        "document_id",
        "request_id",
        "processing_attempt_id",
        "patient_id",
        "owner_scope",
        "source_ref",
    }.isdisjoint(body)
    rendered = str(body)
    assert "SYNTHETIC_DOCUMENT_TOKEN" not in rendered
    assert "filename" not in rendered.casefold()


def test_transport_rejects_forged_clinical_or_source_authority() -> None:
    value = asdict(EngineeringDocumentDemoService().project(clock=NOW))
    for mutation in (
        {"classification": "CLINICAL"},
        {"source_access": "VERIFIED"},
        {"candidate_disposition": "CONFIRMED"},
        {"external_egress": True},
        {"processor_disposition": "EXECUTED"},
        {"unexpected_patient_id": "private-canary"},
    ):
        with pytest.raises(ValidationError):
            EngineeringDocumentResultView.model_validate({**value, **mutation})
