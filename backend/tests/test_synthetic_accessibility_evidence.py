from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    AccessibilityEvidenceContractCode,
    AccessibilityEvidenceContractError,
    AccessibilityEvidenceDisposition,
    AccessibilityEvidenceReason,
    SyntheticAccessibilityArea,
    SyntheticAccessibilityDefinition,
    SyntheticAccessibilityObservation,
    SyntheticAccessibilityObservationState,
    build_synthetic_accessibility_manifest,
    evaluate_synthetic_accessibility_evidence,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
BUILD_SHA = "d" * 40
NOW = datetime(2026, 11, 1, 17, 0, tzinfo=UTC)


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


def definition(area: SyntheticAccessibilityArea) -> SyntheticAccessibilityDefinition:
    return SyntheticAccessibilityDefinition(
        area=area,
        definition_version="engineering.v1",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        source_evidence_hash=HASH_B,
        checklist_hash=HASH_C,
        created_at=NOW,
    )


def observation(
    item: SyntheticAccessibilityDefinition,
    *,
    build_sha: str = BUILD_SHA,
    config_hash: str = HASH_A,
    source_evidence_hash: str = HASH_B,
    checklist_hash: str = HASH_C,
) -> SyntheticAccessibilityObservation:
    return SyntheticAccessibilityObservation(
        observation_id="syn_accessibility_observation_alpha",
        area=item.area,
        definition_fingerprint=item.fingerprint,
        build_sha=build_sha,
        config_hash=config_hash,
        source_evidence_hash=source_evidence_hash,
        checklist_hash=checklist_hash,
        state=SyntheticAccessibilityObservationState.METADATA_RECORDED,
        captured_at=NOW + timedelta(minutes=1),
    )


def definitions() -> tuple[SyntheticAccessibilityDefinition, ...]:
    return tuple(definition(area) for area in reversed(tuple(SyntheticAccessibilityArea)))


def test_manifest_builder_canonicalizes_all_eight_areas_deterministically() -> None:
    first = build_synthetic_accessibility_manifest(
        definitions(),
        manifest_id="syn_accessibility_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    second = build_synthetic_accessibility_manifest(
        tuple(reversed(definitions())),
        manifest_id="syn_accessibility_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )

    assert first == second
    assert len(first.definitions) == 8


def test_manifest_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(9))

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        build_synthetic_accessibility_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_accessibility_manifest_alpha",
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        build_synthetic_accessibility_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_accessibility_manifest_alpha",
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.PROTECTED_ENVIRONMENT


def test_exact_observation_returns_consistent_metadata_not_a_pass() -> None:
    item = definition(SyntheticAccessibilityArea.KEYBOARD_AND_FOCUS)
    result = evaluate_synthetic_accessibility_evidence(
        item,
        observation(item),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )

    assert result.disposition is AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT
    assert result.reason is AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA
    assert "PASS" not in result.disposition.value
    assert result.review_state.value == "HUMAN_REVIEW_REQUIRED"


@pytest.mark.parametrize(
    "drift",
    [
        {"build_sha": "e" * 40},
        {"config_hash": "e" * 64},
        {"source_evidence_hash": "e" * 64},
        {"checklist_hash": "e" * 64},
    ],
)
def test_scope_drift_abstains(drift: dict[str, str]) -> None:
    item = definition(SyntheticAccessibilityArea.SEMANTICS_AND_ANNOUNCEMENTS)
    result = evaluate_synthetic_accessibility_evidence(
        item,
        observation(item, **drift),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.TEST,
    )

    assert result.disposition is AccessibilityEvidenceDisposition.ABSTAINED
    assert result.reason is AccessibilityEvidenceReason.SCOPE_MISMATCH


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_evaluator_rejects_protected_environment_before_input_inspection(
    environment: Environment,
) -> None:
    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        evaluate_synthetic_accessibility_evidence(
            HostileInput(),  # type: ignore[arg-type]
            HostileInput(),  # type: ignore[arg-type]
            evaluated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.PROTECTED_ENVIRONMENT


def test_evaluator_rejects_loose_environment_type() -> None:
    item = definition(SyntheticAccessibilityArea.CONTRAST_AND_DISPLAY)

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        evaluate_synthetic_accessibility_evidence(
            item,
            observation(item),
            evaluated_at=NOW + timedelta(minutes=2),
            environment="test",  # type: ignore[arg-type]
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INVALID_TYPE


def test_validation_foundation_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "accessibility" not in module_ids
    assert all("accessibility" not in path for path in route_paths)


def test_receipt_exposes_no_audit_outcome_or_authority_surface() -> None:
    item = definition(SyntheticAccessibilityArea.LANGUAGE)
    result = evaluate_synthetic_accessibility_evidence(
        item,
        observation(item),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.TEST,
    )

    for prohibited in (
        "approve",
        "audit_result",
        "certify",
        "defect",
        "finding",
        "patient_id",
        "persist",
        "release",
        "remediate",
        "severity",
        "wcag_conformance",
    ):
        assert not hasattr(result, prohibited)
        assert not hasattr(result.definition, prohibited)
        assert not hasattr(result.observation, prohibited)
