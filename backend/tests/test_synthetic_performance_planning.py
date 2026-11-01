from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    PerformancePlanAuthority,
    PerformancePlanClassification,
    PerformancePlanContractCode,
    PerformancePlanContractError,
    PerformancePlanExecutionState,
    PerformancePlanReviewState,
    PerformancePlanVerification,
    SyntheticPerformanceManifest,
    SyntheticPerformancePlan,
    SyntheticPerformanceTarget,
    build_synthetic_performance_manifest,
    snapshot_performance_manifest,
    snapshot_performance_plan,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64
BUILD_SHA = "f" * 40
NOW = datetime(2026, 11, 1, 18, 0, tzinfo=UTC)

EXPECTED_TARGETS = {
    "API_LATENCY",
    "DATABASE_QUERY_HOTSPOTS",
    "DOCUMENT_QUEUE",
    "LLM_LATENCY",
    "PROVIDER_SEARCH",
}


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


def plan(
    target: SyntheticPerformanceTarget = SyntheticPerformanceTarget.API_LATENCY,
    *,
    created_at: datetime = NOW,
) -> SyntheticPerformancePlan:
    return SyntheticPerformancePlan(
        target=target,
        plan_version="engineering.v1",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        workload_hash=HASH_B,
        fixture_provenance_hash=HASH_C,
        measurement_method_hash=HASH_D,
        isolation_plan_hash=HASH_E,
        analysis_plan_hash=HASH_A,
        created_at=created_at,
    )


def plans() -> tuple[SyntheticPerformancePlan, ...]:
    return tuple(plan(target) for target in reversed(tuple(SyntheticPerformanceTarget)))


def test_target_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticPerformanceTarget} == EXPECTED_TARGETS


def test_plan_is_explicitly_unexecuted_unverified_and_human_gated() -> None:
    item = plan()

    assert item.authority is PerformancePlanAuthority.ENGINEERING_ONLY
    assert item.classification is PerformancePlanClassification.ENGINEERING_SYNTHETIC
    assert item.verification is PerformancePlanVerification.UNVERIFIED
    assert item.execution_state is PerformancePlanExecutionState.NOT_EXECUTED
    assert item.review_state is PerformancePlanReviewState.HUMAN_APPROVAL_REQUIRED
    assert len(item.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("target", "API_LATENCY"),
        ("plan_version", "v1"),
        ("build_sha", "f" * 39),
        ("config_hash", "A" * 64),
        ("workload_hash", "not-a-hash"),
        ("fixture_provenance_hash", "c" * 63),
        ("measurement_method_hash", "D" * 64),
        ("isolation_plan_hash", "e" * 65),
        ("analysis_plan_hash", "secret"),
        ("created_at", NOW.replace(tzinfo=None)),
        ("execution_state", "NOT_EXECUTED"),
    ],
)
def test_plan_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "target": SyntheticPerformanceTarget.API_LATENCY,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "workload_hash": HASH_B,
        "fixture_provenance_hash": HASH_C,
        "measurement_method_hash": HASH_D,
        "isolation_plan_hash": HASH_E,
        "analysis_plan_hash": HASH_A,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(PerformancePlanContractError):
        SyntheticPerformancePlan(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_and_plan_is_immutable() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = plan(created_at=non_utc)

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        item.target = SyntheticPerformanceTarget.LLM_LATENCY  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("build_sha", "e" * 40),
        ("config_hash", HASH_B),
        ("workload_hash", HASH_C),
        ("fixture_provenance_hash", HASH_D),
        ("measurement_method_hash", HASH_E),
        ("isolation_plan_hash", HASH_A),
        ("analysis_plan_hash", HASH_B),
    ],
)
def test_fingerprint_binds_every_build_and_plan_hash(field: str, value: str) -> None:
    values = {
        "target": SyntheticPerformanceTarget.API_LATENCY,
        "plan_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "workload_hash": HASH_B,
        "fixture_provenance_hash": HASH_C,
        "measurement_method_hash": HASH_D,
        "isolation_plan_hash": HASH_E,
        "analysis_plan_hash": HASH_A,
        "created_at": NOW,
    }
    values[field] = value

    assert SyntheticPerformancePlan(**values).fingerprint != plan().fingerprint  # type: ignore[arg-type]


def test_manifest_builder_is_complete_canonical_and_deterministic() -> None:
    first = build_synthetic_performance_manifest(
        plans(),
        manifest_id="syn_performance_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    second = build_synthetic_performance_manifest(
        tuple(reversed(plans())),
        manifest_id="syn_performance_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert tuple(item.target.value for item in first.plans) == tuple(sorted(EXPECTED_TARGETS))


def test_direct_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(PerformancePlanContractError) as captured:
        SyntheticPerformanceManifest(
            manifest_id="syn_performance_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            plans=plans(),
        )

    assert captured.value.code is PerformancePlanContractCode.INVALID_ORDER


def test_direct_manifest_rejects_duplicate_target_at_exact_cardinality() -> None:
    items = tuple(
        plan(target) for target in sorted(SyntheticPerformanceTarget, key=lambda x: x.value)
    )

    with pytest.raises(PerformancePlanContractError) as captured:
        SyntheticPerformanceManifest(
            manifest_id="syn_performance_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            plans=items[:-1] + items[:1],
        )

    assert captured.value.code is PerformancePlanContractCode.DUPLICATE_TARGET


def test_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(6))

    with pytest.raises(PerformancePlanContractError) as captured:
        build_synthetic_performance_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_performance_manifest_alpha",
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is PerformancePlanContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(PerformancePlanContractError) as captured:
        build_synthetic_performance_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_performance_manifest_alpha",
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is PerformancePlanContractCode.PROTECTED_ENVIRONMENT


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = plan()
    inventory = build_synthetic_performance_manifest(
        plans(),
        manifest_id="syn_performance_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )
    object.__setattr__(item, "workload_hash", HASH_A)
    object.__setattr__(inventory, "generated_at", NOW)

    with pytest.raises(PerformancePlanContractError):
        snapshot_performance_plan(item)
    with pytest.raises(PerformancePlanContractError):
        snapshot_performance_manifest(inventory)


def test_errors_and_representations_are_content_free() -> None:
    hostile = "secret-patient@example.test"

    with pytest.raises(PerformancePlanContractError) as captured:
        SyntheticPerformanceManifest(
            manifest_id=hostile,
            generated_at=NOW,
            plans=(),
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    assert HASH_A not in repr(plan())


def test_plan_exposes_no_measurement_result_or_execution_surface() -> None:
    item = plan()
    for prohibited in (
        "approve",
        "availability",
        "baseline",
        "concurrency",
        "duration",
        "error_budget",
        "execute",
        "latency",
        "measure",
        "p50",
        "p95",
        "p99",
        "result",
        "rps",
        "run",
        "sample_size",
        "slo",
        "threshold",
        "throughput",
    ):
        assert not hasattr(item, prohibited)


def test_performance_planning_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "performance" not in module_ids
    assert all("performance" not in path for path in route_paths)
