"""Regression coverage for the local/test-only P16 FHIR boundary preview."""

from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.config.settings import Environment
from app.main import create_app
from app.modules.engineering_fhir_demo.api import EngineeringFHIRPreviewView
from app.modules.engineering_fhir_demo.application import EngineeringFHIRDemoService
from app.modules.interoperability.fhir.contracts import FHIRMappingCode, FHIRMappingError

PATH = "/api/v1/engineering-demo/fhir-preview"


def enabled_settings(*, environment: str = "local") -> Settings:
    return Settings(
        _env_file=None,
        environment=environment,
        features={"enabled": ("engineering_fhir_demo_wave7",)},
    )


def test_projection_composes_mapping_and_fail_closed_validation_contracts() -> None:
    result = EngineeringFHIRDemoService(environment=Environment.TEST).project()

    assert result.fhir_version == "4.0.1"
    assert result.mapping_direction == "EXPORT"
    assert result.mapping_state == "SYNTHETIC_EXPORT_PROJECTION"
    assert result.resource_type == "Observation"
    assert result.structural_validation == "SYNTHETIC_STRUCTURAL_PASS"
    assert result.profile_validation == "SYNTHETIC_UNAVAILABLE"
    assert result.profile_issue == "PROFILE_PACKAGE_UNAVAILABLE"
    assert result.fhir_payload_present is False
    assert result.patient_data_processed is False
    assert result.profile_conformance_claimed is False
    assert result.exchange_authorized is False
    assert result.external_transport is False
    assert result.abdm_invoked is False
    assert result.persistence_written is False


def test_service_fails_closed_before_mapping_in_protected_environment() -> None:
    service = EngineeringFHIRDemoService(environment=Environment.PRODUCTION)

    with pytest.raises(FHIRMappingError) as caught:
        service.project()

    assert caught.value.code is FHIRMappingCode.PROTECTED_ENVIRONMENT


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
    assert body["fhir_payload_present"] is False
    assert body["profile_conformance_claimed"] is False
    assert {
        "patient_id",
        "session_id",
        "resource",
        "payload",
        "source_hash",
        "transformed_at",
    }.isdisjoint(body)
    rendered = str(body).casefold()
    assert "http" not in rendered
    assert "@" not in rendered


def test_transport_rejects_forged_conformance_exchange_or_payload() -> None:
    value = asdict(EngineeringFHIRDemoService(environment=Environment.TEST).project())
    for mutation in (
        {"authority": "CLINICAL"},
        {"verification": "VERIFIED"},
        {"fhir_version": "5.0.0"},
        {"resource_type": "Condition"},
        {"profile_validation": "SYNTHETIC_STRUCTURAL_PASS"},
        {"profile_conformance_claimed": True},
        {"fhir_payload_present": True},
        {"patient_data_processed": True},
        {"exchange_authorized": True},
        {"external_transport": True},
        {"abdm_invoked": True},
        {"persistence_written": True},
        {"unexpected_payload": {"resourceType": "Observation"}},
    ):
        with pytest.raises(ValidationError):
            EngineeringFHIRPreviewView.model_validate({**value, **mutation})
