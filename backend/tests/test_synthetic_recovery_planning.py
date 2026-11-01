from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    RecoveryPlanApplicability,
    RecoveryPlanAuthority,
    RecoveryPlanClassification,
    RecoveryPlanContractCode,
    RecoveryPlanContractError,
    RecoveryPlanExecutionState,
    RecoveryPlanReviewState,
    RecoveryPlanVerification,
    SyntheticRecoveryManifest,
    SyntheticRecoveryPlan,
    SyntheticRecoveryScenario,
    build_synthetic_recovery_manifest,
    snapshot_recovery_manifest,
    snapshot_recovery_plan,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64
BUILD_SHA = "f" * 40
NOW = datetime(2026, 11, 1, 19, 0, tzinfo=UTC)

EXPECTED_SCENARIOS = {
    "DUPLICATE_EVENT",
    "OUTBOX_RECOVERY",
    "PROJECTION_REBUILD_IF_APPLICABLE",
    "RETRY",
    "WORKER_RESTART",
}


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


def expected_applicability(scenario: SyntheticRecoveryScenario) -> RecoveryPlanApplicability:
    if scenario is SyntheticRecoveryScenario.PROJECTION_REBUILD_IF_APPLICABLE:
        return RecoveryPlanApplicability.UNDECIDED
    return RecoveryPlanApplicability.PROPOSED_UNAPPROVED


def plan(
    scenario: SyntheticRecoveryScenario = SyntheticRecoveryScenario.WORKER_RESTART,
    *,
    applicability: RecoveryPlanApplicability | None = None,
    created_at: datetime = NOW,
) -> SyntheticRecoveryPlan:
    return SyntheticRecoveryPlan(
        scenario=scenario,
        applicability=applicability or expected_applicability(scenario),
        plan_version="engineering.v1",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        failure_injection_plan_hash=HASH_B,
        recovery_oracle_hash=HASH_C,
        isolation_cleanup_hash=HASH_D,
        privacy_canary_hash=HASH_E,
        rollback_plan_hash=HASH_A,
        created_at=created_at,
    )


def plans() -> tuple[SyntheticRecoveryPlan, ...]:
    return tuple(plan(scenario) for scenario in reversed(tuple(SyntheticRecoveryScenario)))


def test_scenario_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticRecoveryScenario} == EXPECTED_SCENARIOS


def test_plan_is_unexecuted_unverified_and_human_gated() -> None:
    item = plan()

    assert item.authority is RecoveryPlanAuthority.ENGINEERING_ONLY
    assert item.classification is RecoveryPlanClassification.ENGINEERING_SYNTHETIC
    assert item.verification is RecoveryPlanVerification.UNVERIFIED
    assert item.execution_state is RecoveryPlanExecutionState.NOT_EXECUTED
    assert item.review_state is RecoveryPlanReviewState.HUMAN_APPROVAL_REQUIRED
    assert len(item.fingerprint) == 64


def test_projection_applicability_remains_undecided() -> None:
    assert plan(SyntheticRecoveryScenario.PROJECTION_REBUILD_IF_APPLICABLE).applicability is (
        RecoveryPlanApplicability.UNDECIDED
    )

    with pytest.raises(RecoveryPlanContractError) as captured:
        plan(
            SyntheticRecoveryScenario.PROJECTION_REBUILD_IF_APPLICABLE,
            applicability=RecoveryPlanApplicability.PROPOSED_UNAPPROVED,
        )

    assert captured.value.code is RecoveryPlanContractCode.INVALID_APPLICABILITY


def test_nonprojection_applicability_cannot_be_undecided() -> None:
    with pytest.raises(RecoveryPlanContractError) as captured:
        plan(
            SyntheticRecoveryScenario.WORKER_RESTART,
            applicability=RecoveryPlanApplicability.UNDECIDED,
        )

    assert captured.value.code is RecoveryPlanContractCode.INVALID_APPLICABILITY


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("scenario", "WORKER_RESTART"),
        ("applicability", "PROPOSED_UNAPPROVED"),
        ("plan_version", "v1"),
        ("build_sha", "f" * 39),
        ("config_hash", "A" * 64),
        ("failure_injection_plan_hash", "not-a-hash"),
        ("recovery_oracle_hash", "c" * 63),
        ("isolation_cleanup_hash", "D" * 64),
        ("privacy_canary_hash", "e" * 65),
        ("rollback_plan_hash", "secret"),
        ("created_at", NOW.replace(tzinfo=None)),
        ("execution_state", "NOT_EXECUTED"),
    ],
)
def test_plan_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "scenario": SyntheticRecoveryScenario.WORKER_RESTART,
        "applicability": RecoveryPlanApplicability.PROPOSED_UNAPPROVED,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "failure_injection_plan_hash": HASH_B,
        "recovery_oracle_hash": HASH_C,
        "isolation_cleanup_hash": HASH_D,
        "privacy_canary_hash": HASH_E,
        "rollback_plan_hash": HASH_A,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(RecoveryPlanContractError):
        SyntheticRecoveryPlan(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_and_plan_is_immutable() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = plan(created_at=non_utc)

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        item.scenario = SyntheticRecoveryScenario.RETRY  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("build_sha", "e" * 40),
        ("config_hash", HASH_B),
        ("failure_injection_plan_hash", HASH_C),
        ("recovery_oracle_hash", HASH_D),
        ("isolation_cleanup_hash", HASH_E),
        ("privacy_canary_hash", HASH_A),
        ("rollback_plan_hash", HASH_B),
    ],
)
def test_fingerprint_binds_every_build_and_plan_hash(field: str, value: str) -> None:
    values = {
        "scenario": SyntheticRecoveryScenario.WORKER_RESTART,
        "applicability": RecoveryPlanApplicability.PROPOSED_UNAPPROVED,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "failure_injection_plan_hash": HASH_B,
        "recovery_oracle_hash": HASH_C,
        "isolation_cleanup_hash": HASH_D,
        "privacy_canary_hash": HASH_E,
        "rollback_plan_hash": HASH_A,
        "created_at": NOW,
    }
    values[field] = value

    assert SyntheticRecoveryPlan(**values).fingerprint != plan().fingerprint  # type: ignore[arg-type]


def test_manifest_builder_is_complete_canonical_and_deterministic() -> None:
    first = build_synthetic_recovery_manifest(
        plans(),
        manifest_id="syn_recovery_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    second = build_synthetic_recovery_manifest(
        tuple(reversed(plans())),
        manifest_id="syn_recovery_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert tuple(item.scenario.value for item in first.plans) == tuple(sorted(EXPECTED_SCENARIOS))


def test_direct_manifest_rejects_duplicate_scenario_at_exact_cardinality() -> None:
    items = tuple(plan(item) for item in sorted(SyntheticRecoveryScenario, key=lambda x: x.value))

    with pytest.raises(RecoveryPlanContractError) as captured:
        SyntheticRecoveryManifest(
            manifest_id="syn_recovery_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            plans=items[:-1] + items[:1],
        )

    assert captured.value.code is RecoveryPlanContractCode.DUPLICATE_SCENARIO


def test_direct_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(RecoveryPlanContractError) as captured:
        SyntheticRecoveryManifest(
            manifest_id="syn_recovery_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            plans=plans(),
        )

    assert captured.value.code is RecoveryPlanContractCode.INVALID_ORDER


def test_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(6))

    with pytest.raises(RecoveryPlanContractError) as captured:
        build_synthetic_recovery_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_recovery_manifest_alpha",
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is RecoveryPlanContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(RecoveryPlanContractError) as captured:
        build_synthetic_recovery_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_recovery_manifest_alpha",
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is RecoveryPlanContractCode.PROTECTED_ENVIRONMENT


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = plan()
    inventory = build_synthetic_recovery_manifest(
        plans(),
        manifest_id="syn_recovery_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__setattr__(item, "recovery_oracle_hash", HASH_A)
    object.__setattr__(inventory, "generated_at", NOW)

    with pytest.raises(RecoveryPlanContractError):
        snapshot_recovery_plan(item)
    with pytest.raises(RecoveryPlanContractError):
        snapshot_recovery_manifest(inventory)


def test_errors_and_representations_are_content_free() -> None:
    hostile = "secret-patient@example.test"

    with pytest.raises(RecoveryPlanContractError) as captured:
        SyntheticRecoveryManifest(manifest_id=hostile, generated_at=NOW, plans=())

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    assert HASH_A not in repr(plan())


def test_plan_exposes_no_execution_result_or_operational_authority() -> None:
    item = plan()
    for prohibited in (
        "approve",
        "backoff",
        "dispatch",
        "execute",
        "exactly_once",
        "inject",
        "kill_switch",
        "lease",
        "pass_result",
        "persist",
        "rebuild",
        "recover",
        "replay",
        "restart",
        "result",
        "retry",
        "rollback",
        "rpo",
        "rto",
        "run",
    ):
        assert not hasattr(item, prohibited)


def test_recovery_planning_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "recovery" not in module_ids
    assert all("recovery" not in path for path in route_paths)
