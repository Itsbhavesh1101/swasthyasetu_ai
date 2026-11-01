from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone, tzinfo

import pytest

import app.validation as validation
from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION,
    ReleaseRehearsalApplicability,
    ReleaseRehearsalAuthority,
    ReleaseRehearsalClassification,
    ReleaseRehearsalContractCode,
    ReleaseRehearsalContractError,
    ReleaseRehearsalDecisionState,
    ReleaseRehearsalEligibility,
    ReleaseRehearsalExecutionState,
    ReleaseRehearsalReviewState,
    ReleaseRehearsalVerification,
    SyntheticReleaseRehearsalManifest,
    SyntheticReleaseRehearsalPlan,
    SyntheticReleaseRehearsalScenario,
    build_synthetic_release_rehearsal_manifest,
    snapshot_release_rehearsal_manifest,
    snapshot_release_rehearsal_plan,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64
HASH_F = "f" * 64
BUILD_SHA = "f" * 40
NOW = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)

EXPECTED_SCENARIOS = {
    "APPLICATION_ROLLBACK",
    "BACKUP_RESTORE",
    "INCIDENT_ESCALATION",
    "MODEL_ROLLBACK",
    "POLICY_ROLLBACK",
    "PROVIDER_OUTAGE",
    "PURGE_FAILURE",
    "RESOURCE_DISABLE",
}


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


class HostileTimezone(tzinfo):
    def utcoffset(self, value: datetime | None) -> timedelta:
        raise RuntimeError("secret-patient@example.test")

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(0)

    def tzname(self, value: datetime | None) -> str:
        return "HOSTILE"


class HostileContractTimezone(tzinfo):
    def utcoffset(self, value: datetime | None) -> timedelta:
        error = ReleaseRehearsalContractError(ReleaseRehearsalContractCode.INVALID_VALUE)
        error.args = ("secret-patient@example.test", error.code)
        raise error

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(0)

    def tzname(self, value: datetime | None) -> str:
        return "HOSTILE_CONTRACT"


class AlwaysEqualFingerprint:
    def __eq__(self, other: object) -> bool:
        return True

    def __ne__(self, other: object) -> bool:
        return False


class FingerprintSubclass(str):
    pass


def plan(
    scenario: SyntheticReleaseRehearsalScenario = (
        SyntheticReleaseRehearsalScenario.APPLICATION_ROLLBACK
    ),
    *,
    build_sha: str = BUILD_SHA,
    config_hash: str = HASH_A,
    created_at: datetime = NOW,
) -> SyntheticReleaseRehearsalPlan:
    return SyntheticReleaseRehearsalPlan(
        scenario=scenario,
        applicability=ReleaseRehearsalApplicability.UNDECIDED,
        plan_version="engineering.v1",
        build_sha=build_sha,
        config_hash=config_hash,
        prerequisite_plan_hash=HASH_B,
        failure_injection_plan_hash=HASH_C,
        oracle_plan_hash=HASH_D,
        isolation_cleanup_plan_hash=HASH_E,
        privacy_canary_plan_hash=HASH_F,
        rollback_or_safe_off_plan_hash=HASH_A,
        evidence_plan_hash=HASH_B,
        responsible_roles_hash=HASH_C,
        created_at=created_at,
    )


def plans(
    *,
    build_sha: str = BUILD_SHA,
    config_hash: str = HASH_A,
) -> tuple[SyntheticReleaseRehearsalPlan, ...]:
    return tuple(
        plan(scenario, build_sha=build_sha, config_hash=config_hash)
        for scenario in reversed(tuple(SyntheticReleaseRehearsalScenario))
    )


def test_rehearsal_scenario_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticReleaseRehearsalScenario} == EXPECTED_SCENARIOS
    assert (
        SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION == "synthetic-release-rehearsal-plan.v1"
    )


def test_public_package_exposes_contracts_but_no_operational_authority() -> None:
    for expected in (
        "SyntheticReleaseRehearsalPlan",
        "SyntheticReleaseRehearsalManifest",
        "build_synthetic_release_rehearsal_manifest",
        "snapshot_release_rehearsal_plan",
        "snapshot_release_rehearsal_manifest",
    ):
        assert expected in validation.__all__

    for prohibited in (
        "approve_release_rehearsal",
        "execute_release_rehearsal",
        "record_release_rehearsal_evidence",
        "record_release_rehearsal_result",
        "run_release_rehearsal",
    ):
        assert prohibited not in validation.__all__
        assert not hasattr(validation, prohibited)


def test_plan_is_unexecuted_unverified_ineligible_and_human_gated() -> None:
    item = plan()

    assert item.authority is ReleaseRehearsalAuthority.ENGINEERING_ONLY
    assert item.classification is ReleaseRehearsalClassification.ENGINEERING_SYNTHETIC
    assert item.verification is ReleaseRehearsalVerification.UNVERIFIED
    assert item.execution_state is ReleaseRehearsalExecutionState.NOT_EXECUTED
    assert item.eligibility is ReleaseRehearsalEligibility.NOT_ELIGIBLE
    assert item.review_state is (
        ReleaseRehearsalReviewState.HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED
    )
    assert item.decision_state is ReleaseRehearsalDecisionState.NOT_RECORDED
    assert item.applicability is ReleaseRehearsalApplicability.UNDECIDED
    assert len(item.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("scenario", "APPLICATION_ROLLBACK"),
        ("applicability", "UNDECIDED"),
        ("plan_version", "v1"),
        ("build_sha", "f" * 39),
        ("config_hash", "A" * 64),
        ("prerequisite_plan_hash", "not-a-hash"),
        ("failure_injection_plan_hash", "c" * 63),
        ("oracle_plan_hash", "D" * 64),
        ("isolation_cleanup_plan_hash", "e" * 65),
        ("privacy_canary_plan_hash", "secret"),
        ("rollback_or_safe_off_plan_hash", "0" * 63),
        ("evidence_plan_hash", True),
        ("responsible_roles_hash", 1),
        ("created_at", NOW.replace(tzinfo=None)),
        ("execution_state", "NOT_EXECUTED"),
    ],
)
def test_plan_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "scenario": SyntheticReleaseRehearsalScenario.APPLICATION_ROLLBACK,
        "applicability": ReleaseRehearsalApplicability.UNDECIDED,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "prerequisite_plan_hash": HASH_B,
        "failure_injection_plan_hash": HASH_C,
        "oracle_plan_hash": HASH_D,
        "isolation_cleanup_plan_hash": HASH_E,
        "privacy_canary_plan_hash": HASH_F,
        "rollback_or_safe_off_plan_hash": HASH_A,
        "evidence_plan_hash": HASH_B,
        "responsible_roles_hash": HASH_C,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(ReleaseRehearsalContractError):
        SyntheticReleaseRehearsalPlan(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_and_plan_is_immutable() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = plan(created_at=non_utc)

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        item.scenario = SyntheticReleaseRehearsalScenario.BACKUP_RESTORE  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("build_sha", "e" * 40),
        ("config_hash", HASH_B),
        ("prerequisite_plan_hash", HASH_C),
        ("failure_injection_plan_hash", HASH_D),
        ("oracle_plan_hash", HASH_E),
        ("isolation_cleanup_plan_hash", HASH_F),
        ("privacy_canary_plan_hash", HASH_A),
        ("rollback_or_safe_off_plan_hash", HASH_B),
        ("evidence_plan_hash", HASH_C),
        ("responsible_roles_hash", HASH_D),
    ],
)
def test_fingerprint_binds_every_build_config_and_plan_hash(field: str, value: str) -> None:
    values = {
        "scenario": SyntheticReleaseRehearsalScenario.APPLICATION_ROLLBACK,
        "applicability": ReleaseRehearsalApplicability.UNDECIDED,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "prerequisite_plan_hash": HASH_B,
        "failure_injection_plan_hash": HASH_C,
        "oracle_plan_hash": HASH_D,
        "isolation_cleanup_plan_hash": HASH_E,
        "privacy_canary_plan_hash": HASH_F,
        "rollback_or_safe_off_plan_hash": HASH_A,
        "evidence_plan_hash": HASH_B,
        "responsible_roles_hash": HASH_C,
        "created_at": NOW,
    }
    values[field] = value

    assert SyntheticReleaseRehearsalPlan(**values).fingerprint != plan().fingerprint  # type: ignore[arg-type]


def test_plan_snapshot_rejects_forced_mutation() -> None:
    item = plan()
    object.__setattr__(item, "oracle_plan_hash", HASH_A)

    with pytest.raises(ReleaseRehearsalContractError):
        snapshot_release_rehearsal_plan(item)


@pytest.mark.parametrize(
    "created_at",
    [
        datetime(2026, 11, 2, 9, 0, tzinfo=HostileTimezone()),
        datetime.min.replace(tzinfo=timezone(timedelta(hours=14))),
    ],
)
def test_invalid_aware_clock_becomes_content_free_contract_error(created_at: datetime) -> None:
    with pytest.raises(ReleaseRehearsalContractError) as captured:
        plan(created_at=created_at)

    assert captured.value.code is ReleaseRehearsalContractCode.INVALID_TYPE
    assert str(captured.value) == "INVALID_TYPE"
    assert captured.value.__cause__ is None


def test_hostile_contract_timezone_is_sanitized_at_plan_and_manifest_boundaries() -> None:
    hostile_clock = datetime(2026, 11, 2, 9, 0, tzinfo=HostileContractTimezone())

    with pytest.raises(ReleaseRehearsalContractError) as plan_error:
        plan(created_at=hostile_clock)
    with pytest.raises(ReleaseRehearsalContractError) as manifest_error:
        SyntheticReleaseRehearsalManifest(
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=hostile_clock,
            plans=tuple(
                plan(item)
                for item in sorted(SyntheticReleaseRehearsalScenario, key=lambda x: x.value)
            ),
        )

    for captured in (plan_error.value, manifest_error.value):
        assert captured.code is ReleaseRehearsalContractCode.INVALID_TYPE
        assert str(captured) == "INVALID_TYPE"
        assert captured.__cause__ is None


def test_manifest_builder_is_complete_canonical_and_deterministic() -> None:
    first = build_synthetic_release_rehearsal_manifest(
        plans(),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    second = build_synthetic_release_rehearsal_manifest(
        tuple(reversed(plans())),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert tuple(item.scenario.value for item in first.plans) == tuple(sorted(EXPECTED_SCENARIOS))
    assert first.authority is ReleaseRehearsalAuthority.ENGINEERING_ONLY
    assert first.verification is ReleaseRehearsalVerification.UNVERIFIED
    assert first.execution_state is ReleaseRehearsalExecutionState.NOT_EXECUTED
    assert first.eligibility is ReleaseRehearsalEligibility.NOT_ELIGIBLE
    assert first.decision_state is ReleaseRehearsalDecisionState.NOT_RECORDED


def test_direct_manifest_rejects_duplicate_scenario_at_exact_cardinality() -> None:
    items = tuple(
        plan(item) for item in sorted(SyntheticReleaseRehearsalScenario, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        SyntheticReleaseRehearsalManifest(
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW + timedelta(minutes=1),
            plans=items[:-1] + items[:1],
        )

    assert captured.value.code is ReleaseRehearsalContractCode.DUPLICATE_SCENARIO


def test_direct_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(ReleaseRehearsalContractError) as captured:
        SyntheticReleaseRehearsalManifest(
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW + timedelta(minutes=1),
            plans=plans(),
        )

    assert captured.value.code is ReleaseRehearsalContractCode.INVALID_ORDER


@pytest.mark.parametrize(
    "items",
    [
        (),
        tuple(plan(item) for item in tuple(SyntheticReleaseRehearsalScenario)[:-1]),
    ],
)
def test_direct_manifest_rejects_incomplete_inventory(
    items: tuple[SyntheticReleaseRehearsalPlan, ...],
) -> None:
    with pytest.raises(ReleaseRehearsalContractError) as captured:
        SyntheticReleaseRehearsalManifest(
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW + timedelta(minutes=1),
            plans=items,
        )

    assert captured.value.code is ReleaseRehearsalContractCode.INCOMPLETE_INVENTORY


def test_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(9))

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        build_synthetic_release_rehearsal_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is ReleaseRehearsalContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(ReleaseRehearsalContractError) as captured:
        build_synthetic_release_rehearsal_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="secret-patient@example.test",
            build_sha="secret-patient@example.test",
            config_hash="secret-patient@example.test",
            proposed_scope_hash="secret-patient@example.test",
            generated_at=HostileInput(),  # type: ignore[arg-type]
            environment=environment,
        )

    assert captured.value.code is ReleaseRehearsalContractCode.PROTECTED_ENVIRONMENT


@pytest.mark.parametrize(
    ("build_sha", "config_hash", "expected_code"),
    [
        ("e" * 40, HASH_A, ReleaseRehearsalContractCode.INVALID_VALUE),
        (BUILD_SHA, HASH_B, ReleaseRehearsalContractCode.INVALID_VALUE),
    ],
)
def test_manifest_rejects_nested_build_or_config_drift(
    build_sha: str,
    config_hash: str,
    expected_code: ReleaseRehearsalContractCode,
) -> None:
    with pytest.raises(ReleaseRehearsalContractError) as captured:
        build_synthetic_release_rehearsal_manifest(
            plans(),
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=build_sha,
            config_hash=config_hash,
            proposed_scope_hash=HASH_D,
            generated_at=NOW + timedelta(minutes=1),
            environment=Environment.TEST,
        )

    assert captured.value.code is expected_code


def test_manifest_rejects_plan_created_after_generation() -> None:
    future = tuple(
        plan(item, created_at=NOW + timedelta(minutes=2))
        for item in sorted(SyntheticReleaseRehearsalScenario, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        SyntheticReleaseRehearsalManifest(
            manifest_id="syn_release_rehearsal_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW + timedelta(minutes=1),
            plans=future,
        )

    assert captured.value.code is ReleaseRehearsalContractCode.INVALID_CHRONOLOGY


def test_manifest_snapshot_rejects_forced_nested_and_scalar_mutation() -> None:
    inventory = build_synthetic_release_rehearsal_manifest(
        plans(),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__setattr__(inventory.plans[0], "evidence_plan_hash", HASH_A)

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        snapshot_release_rehearsal_manifest(inventory)

    assert captured.value.code is ReleaseRehearsalContractCode.SNAPSHOT_DRIFT


@pytest.mark.parametrize(
    "substitute",
    [AlwaysEqualFingerprint(), FingerprintSubclass("a" * 64), "not-a-fingerprint"],
)
def test_plan_snapshot_rejects_substituted_stored_fingerprint(substitute: object) -> None:
    item = plan()
    object.__setattr__(item, "_fingerprint", substitute)

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        snapshot_release_rehearsal_plan(item)

    assert captured.value.code is ReleaseRehearsalContractCode.SNAPSHOT_DRIFT


@pytest.mark.parametrize(
    "substitute",
    [AlwaysEqualFingerprint(), FingerprintSubclass("a" * 64), "not-a-fingerprint"],
)
def test_manifest_snapshot_rejects_substituted_stored_fingerprint(substitute: object) -> None:
    inventory = build_synthetic_release_rehearsal_manifest(
        plans(),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__setattr__(inventory, "_fingerprint", substitute)

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        snapshot_release_rehearsal_manifest(inventory)

    assert captured.value.code is ReleaseRehearsalContractCode.SNAPSHOT_DRIFT


def test_snapshots_convert_missing_stored_fingerprints_to_contract_errors() -> None:
    item = plan()
    inventory = build_synthetic_release_rehearsal_manifest(
        plans(),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__delattr__(item, "_fingerprint")
    object.__delattr__(inventory, "_fingerprint")

    for snapshot, value in (
        (snapshot_release_rehearsal_plan, item),
        (snapshot_release_rehearsal_manifest, inventory),
    ):
        with pytest.raises(ReleaseRehearsalContractError) as captured:
            snapshot(value)
        assert captured.value.code is ReleaseRehearsalContractCode.INVALID_TYPE


def test_snapshot_rejects_simultaneous_data_and_fingerprint_substitution() -> None:
    item = plan()
    inventory = build_synthetic_release_rehearsal_manifest(
        plans(),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_D,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__setattr__(item, "oracle_plan_hash", HASH_A)
    object.__setattr__(item, "_fingerprint", AlwaysEqualFingerprint())
    object.__setattr__(inventory, "proposed_scope_hash", HASH_E)
    object.__setattr__(inventory, "_fingerprint", AlwaysEqualFingerprint())

    for snapshot, value in (
        (snapshot_release_rehearsal_plan, item),
        (snapshot_release_rehearsal_manifest, inventory),
    ):
        with pytest.raises(ReleaseRehearsalContractError) as captured:
            snapshot(value)
        assert captured.value.code is ReleaseRehearsalContractCode.SNAPSHOT_DRIFT


def test_errors_and_representations_are_content_free() -> None:
    hostile = "secret-patient@example.test"

    with pytest.raises(ReleaseRehearsalContractError) as captured:
        SyntheticReleaseRehearsalManifest(
            manifest_id=hostile,
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_D,
            generated_at=NOW,
            plans=(),
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    assert HASH_A not in repr(plan())


def test_plan_exposes_no_execution_result_evidence_or_release_authority() -> None:
    item = plan()
    for prohibited in (
        "approve",
        "backup",
        "decision",
        "deploy",
        "disable",
        "drill",
        "evidence",
        "execute",
        "inject",
        "outage",
        "pass_result",
        "persist",
        "purge",
        "release",
        "restore",
        "result",
        "rollback",
        "run",
    ):
        assert not hasattr(item, prohibited)


def test_release_rehearsal_planning_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "release_rehearsal" not in module_ids
    assert all("release-rehearsal" not in path for path in route_paths)
