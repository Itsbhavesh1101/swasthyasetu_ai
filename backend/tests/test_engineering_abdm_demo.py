"""Regression coverage for the local/test-only P17 boundary preview."""

from dataclasses import asdict
from importlib import import_module
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.config.settings import Environment
from app.main import create_app
from app.modules.interoperability.abdm.contracts import ABDMBoundaryCode, ABDMBoundaryError

PATH = "/api/v1/engineering-demo/abdm-preview"


def subjects() -> tuple[type[Any], type[Any]]:
    try:
        api = import_module("app.modules.engineering_abdm_demo.api")
        application = import_module("app.modules.engineering_abdm_demo.application")
    except ModuleNotFoundError:
        pytest.fail("engineering ABDM demo module is not implemented")
    return api.EngineeringABDMPreviewView, application.EngineeringABDMDemoService


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_abdm_demo_wave8",)},
    )


def test_projection_composes_rejected_and_unavailable_zero_egress_results() -> None:
    _, service_type = subjects()

    result = service_type(environment=Environment.TEST).project()

    assert result.mode == "SYNTHETIC_OFFLINE_MOCK"
    assert result.operation == "SYNTHETIC_OPERATION_ALPHA"
    assert result.scripted_state == "SYNTHETIC_REJECTED"
    assert result.scripted_issue == "SYNTHETIC_REJECTED"
    assert result.unknown_state == "SYNTHETIC_UNAVAILABLE"
    assert result.unknown_issue == "SYNTHETIC_UNAVAILABLE"
    assert result.zero_egress is True
    assert result.official_protocol_adopted is False
    assert result.abha_identity_processed is False
    assert result.consent_evaluated is False
    assert result.fhir_payload_present is False
    assert result.sandbox_connected is False
    assert result.patient_data_processed is False
    assert result.local_intake_accessed is False
    assert result.local_intake_mutated is False
    assert result.external_transport is False
    assert result.persistence_written is False


def test_service_fails_closed_before_request_construction_in_protected_environment() -> None:
    _, service_type = subjects()
    service = service_type(environment=Environment.PRODUCTION)

    with pytest.raises(ABDMBoundaryError) as caught:
        service.project()

    assert caught.value.code is ABDMBoundaryCode.PROTECTED_ENVIRONMENT


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
    assert body["zero_egress"] is True
    assert body["local_intake_mutated"] is False
    assert {
        "patient_id",
        "session_id",
        "abha_id",
        "artifact_id",
        "endpoint",
        "credential",
        "payload",
        "request_fingerprint",
        "completed_at",
    }.isdisjoint(body)
    rendered = str(body).casefold()
    assert "http" not in rendered
    assert "@" not in rendered


def test_transport_rejects_forged_success_identity_exchange_or_payload() -> None:
    view_type, service_type = subjects()
    value = asdict(service_type(environment=Environment.TEST).project())
    for mutation in (
        {"authority": "OFFICIAL"},
        {"verification": "VERIFIED"},
        {"scripted_state": "SYNTHETIC_ACCEPTED"},
        {"unknown_state": "SYNTHETIC_ACCEPTED"},
        {"zero_egress": False},
        {"official_protocol_adopted": True},
        {"abha_identity_processed": True},
        {"consent_evaluated": True},
        {"fhir_payload_present": True},
        {"sandbox_connected": True},
        {"patient_data_processed": True},
        {"local_intake_accessed": True},
        {"local_intake_mutated": True},
        {"external_transport": True},
        {"persistence_written": True},
        {"unexpected_payload": {"identifier": "private-canary"}},
    ):
        with pytest.raises(ValidationError):
            view_type.model_validate({**value, **mutation})
