from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    ReleaseSafetyDecisionState,
    ReleaseSafetyPlanAuthority,
    ReleaseSafetyPlanClassification,
    ReleaseSafetyPlanContractCode,
    ReleaseSafetyPlanContractError,
    ReleaseSafetyPlanEligibility,
    ReleaseSafetyPlanExecutionState,
    ReleaseSafetyPlanReviewState,
    ReleaseSafetyPlanVerification,
    SyntheticReleaseSafetyArea,
    SyntheticReleaseSafetyManifest,
    SyntheticReleaseSafetyPlan,
    build_synthetic_release_safety_manifest,
    snapshot_release_safety_manifest,
    snapshot_release_safety_plan,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
BUILD_SHA = "f" * 40
NOW = datetime(2026, 11, 1, 22, 0, tzinfo=UTC)

EXPECTED_AREAS = {
    "CLARIFICATION_UTILITY",
    "CLINICIAN_AUTHORED_SAFETY_SET",
    "CRITICAL_FALSE_NEGATIVES",
    "MULTILINGUAL_SAFETY_SET",
    "RESOURCE_CORRECTNESS",
    "ROUTE_CONCORDANCE",
}


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


def plan(
    area: SyntheticReleaseSafetyArea = SyntheticReleaseSafetyArea.CLINICIAN_AUTHORED_SAFETY_SET,
    *,
    build_sha: str = BUILD_SHA,
    created_at: datetime = NOW,
) -> SyntheticReleaseSafetyPlan:
    return SyntheticReleaseSafetyPlan(
        area=area,
        plan_version="engineering.v1",
        build_sha=build_sha,
        synthetic_fixture_plan_hash=HASH_A,
        oracle_plan_hash=HASH_B,
        metric_plan_hash=HASH_C,
        analysis_plan_hash=HASH_D,
        privacy_plan_hash=HASH_A,
        negative_test_plan_hash=HASH_B,
        responsible_roles_hash=HASH_C,
        created_at=created_at,
    )


def plans() -> tuple[SyntheticReleaseSafetyPlan, ...]:
    return tuple(plan(area) for area in reversed(tuple(SyntheticReleaseSafetyArea)))


def manifest() -> SyntheticReleaseSafetyManifest:
    return build_synthetic_release_safety_manifest(
        plans(),
        manifest_id="syn_release_safety_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_B,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )


def test_safety_evaluation_area_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticReleaseSafetyArea} == EXPECTED_AREAS
    assert len(SyntheticReleaseSafetyArea) == 6


def test_plan_is_unverified_unexecuted_ineligible_and_human_gated() -> None:
    item = plan()

    assert item.authority is ReleaseSafetyPlanAuthority.ENGINEERING_ONLY
    assert item.classification is ReleaseSafetyPlanClassification.ENGINEERING_SYNTHETIC
    assert item.verification is ReleaseSafetyPlanVerification.UNVERIFIED
    assert item.execution_state is ReleaseSafetyPlanExecutionState.NOT_EXECUTED
    assert item.eligibility is ReleaseSafetyPlanEligibility.NOT_ELIGIBLE
    assert item.review_state is ReleaseSafetyPlanReviewState.HUMAN_METRIC_AND_APPROVAL_REQUIRED
    assert item.decision_state is ReleaseSafetyDecisionState.NOT_RECORDED
    assert len(item.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("area", "ROUTE_CONCORDANCE"),
        ("plan_version", "v1"),
        ("build_sha", "f" * 39),
        ("synthetic_fixture_plan_hash", "A" * 64),
        ("oracle_plan_hash", "b" * 63),
        ("metric_plan_hash", "not-a-hash"),
        ("analysis_plan_hash", "d" * 65),
        ("privacy_plan_hash", "A" * 64),
        ("negative_test_plan_hash", "secret"),
        ("responsible_roles_hash", "c" * 65),
        ("created_at", NOW.replace(tzinfo=None)),
        ("execution_state", "EXECUTED"),
        ("decision_state", "GO"),
    ],
)
def test_plan_rejects_loose_malformed_or_authoritative_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "area": SyntheticReleaseSafetyArea.CLINICIAN_AUTHORED_SAFETY_SET,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "synthetic_fixture_plan_hash": HASH_A,
        "oracle_plan_hash": HASH_B,
        "metric_plan_hash": HASH_C,
        "analysis_plan_hash": HASH_D,
        "privacy_plan_hash": HASH_A,
        "negative_test_plan_hash": HASH_B,
        "responsible_roles_hash": HASH_C,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(ReleaseSafetyPlanContractError):
        SyntheticReleaseSafetyPlan(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_and_plan_is_immutable() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = plan(created_at=non_utc)

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        item.area = SyntheticReleaseSafetyArea.ROUTE_CONCORDANCE  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("build_sha", "e" * 40),
        ("synthetic_fixture_plan_hash", HASH_B),
        ("oracle_plan_hash", HASH_C),
        ("metric_plan_hash", HASH_D),
        ("analysis_plan_hash", HASH_A),
        ("privacy_plan_hash", HASH_B),
        ("negative_test_plan_hash", HASH_C),
        ("responsible_roles_hash", HASH_D),
    ],
)
def test_fingerprint_binds_every_build_and_plan_hash(field: str, value: str) -> None:
    values = {
        "area": SyntheticReleaseSafetyArea.CLINICIAN_AUTHORED_SAFETY_SET,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "synthetic_fixture_plan_hash": HASH_A,
        "oracle_plan_hash": HASH_B,
        "metric_plan_hash": HASH_C,
        "analysis_plan_hash": HASH_D,
        "privacy_plan_hash": HASH_A,
        "negative_test_plan_hash": HASH_B,
        "responsible_roles_hash": HASH_C,
        "created_at": NOW,
    }
    values[field] = value

    assert (
        SyntheticReleaseSafetyPlan(**values).fingerprint  # type: ignore[arg-type]
        != plan().fingerprint
    )


def test_manifest_builder_is_complete_canonical_and_deterministic() -> None:
    first = manifest()
    second = build_synthetic_release_safety_manifest(
        tuple(reversed(plans())),
        manifest_id="syn_release_safety_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_B,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert tuple(item.area.value for item in first.plans) == tuple(sorted(EXPECTED_AREAS))
    assert first.decision_state is ReleaseSafetyDecisionState.NOT_RECORDED
    assert first.eligibility is ReleaseSafetyPlanEligibility.NOT_ELIGIBLE


def test_direct_manifest_rejects_duplicate_area_at_exact_cardinality() -> None:
    items = tuple(plan(item) for item in sorted(SyntheticReleaseSafetyArea, key=lambda x: x.value))

    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        SyntheticReleaseSafetyManifest(
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            plans=items[:-1] + items[:1],
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.DUPLICATE_AREA


def test_direct_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        SyntheticReleaseSafetyManifest(
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            plans=plans(),
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.INVALID_ORDER


def test_manifest_rejects_plan_for_a_different_build() -> None:
    items = tuple(
        plan(
            area,
            build_sha="e" * 40
            if area is SyntheticReleaseSafetyArea.RESOURCE_CORRECTNESS
            else BUILD_SHA,
        )
        for area in sorted(SyntheticReleaseSafetyArea, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        SyntheticReleaseSafetyManifest(
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            plans=items,
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.INVALID_VALUE


def test_manifest_rejects_plan_created_after_manifest() -> None:
    items = tuple(
        plan(
            area,
            created_at=NOW + timedelta(minutes=2)
            if area is SyntheticReleaseSafetyArea.CLARIFICATION_UTILITY
            else NOW,
        )
        for area in sorted(SyntheticReleaseSafetyArea, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        SyntheticReleaseSafetyManifest(
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            plans=items,
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.INVALID_CHRONOLOGY


def test_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(7))

    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        build_synthetic_release_safety_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        build_synthetic_release_safety_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_release_safety_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is ReleaseSafetyPlanContractCode.PROTECTED_ENVIRONMENT


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = plan()
    inventory = manifest()
    object.__setattr__(item, "metric_plan_hash", HASH_A)
    object.__setattr__(inventory, "generated_at", NOW)

    with pytest.raises(ReleaseSafetyPlanContractError):
        snapshot_release_safety_plan(item)
    with pytest.raises(ReleaseSafetyPlanContractError):
        snapshot_release_safety_manifest(inventory)


def test_errors_and_representations_are_content_free() -> None:
    hostile = "secret-patient@example.test"

    with pytest.raises(ReleaseSafetyPlanContractError) as captured:
        SyntheticReleaseSafetyManifest(
            manifest_id=hostile,
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            plans=(),
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    assert HASH_A not in repr(plan())
    assert HASH_A not in repr(manifest())


def test_contract_exposes_no_evaluation_clinical_or_release_authority() -> None:
    item = manifest()
    for prohibited in (
        "approve",
        "calculate",
        "clinical_result",
        "conditional_go",
        "deploy",
        "evaluate",
        "execute",
        "go",
        "measure",
        "no_go",
        "pass_result",
        "persist",
        "publish",
        "release",
        "result",
        "run",
        "score",
        "sign",
        "start_pilot",
        "threshold",
    ):
        assert not hasattr(item, prohibited)


def test_release_safety_planning_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "release-safety" not in module_ids
    assert all("release" not in path and "pilot" not in path for path in route_paths)
