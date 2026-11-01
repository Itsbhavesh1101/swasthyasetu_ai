from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    SyntheticJourneyDefinition,
    SyntheticJourneyId,
    SyntheticJourneyObservation,
    SyntheticJourneyReadiness,
    SyntheticObservationState,
    evaluate_synthetic_journey_evidence,
)

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def definition() -> SyntheticJourneyDefinition:
    return SyntheticJourneyDefinition(
        journey_id=SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE,
        definition_version="engineering.v1",
        fixture_hash="a" * 64,
        oracle_hash="b" * 64,
        readiness=SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY,
        created_at=NOW,
    )


def observation(item: SyntheticJourneyDefinition) -> SyntheticJourneyObservation:
    return SyntheticJourneyObservation(
        observation_id="syn_journey_observation_alpha",
        journey_id=item.journey_id,
        definition_fingerprint=item.fingerprint,
        build_sha="c" * 40,
        config_hash="d" * 64,
        fixture_hash=item.fixture_hash,
        oracle_hash=item.oracle_hash,
        state=SyntheticObservationState.METADATA_RECORDED,
        captured_at=NOW + timedelta(minutes=1),
    )


def test_receipt_exposes_no_execution_approval_or_sensitive_content_surface() -> None:
    item = definition()
    result = evaluate_synthetic_journey_evidence(
        item,
        observation(item),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )

    for prohibited in (
        "approve",
        "execute",
        "export",
        "patient_id",
        "clinical_value",
        "persist",
        "promote",
        "publish",
        "release",
        "run",
        "search",
    ):
        assert not hasattr(result, prohibited)
        assert not hasattr(result.definition, prohibited)
        assert result.observation is not None
        assert not hasattr(result.observation, prohibited)


def test_validation_foundation_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "validation" not in module_ids
    assert "journey_evidence" not in module_ids
    assert all("validation" not in path and "journey-evidence" not in path for path in route_paths)


def test_evidence_labels_remain_explicitly_synthetic_and_unverified() -> None:
    item = definition()
    result = evaluate_synthetic_journey_evidence(
        item,
        observation(item),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.TEST,
    )

    assert result.authority.value == "ENGINEERING_ONLY"
    assert result.classification.value == "ENGINEERING_SYNTHETIC"
    assert result.verification.value == "UNVERIFIED"
    assert result.disposition.value != "PASS"
