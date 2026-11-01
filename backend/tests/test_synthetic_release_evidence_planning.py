from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.validation import (
    ReleaseDecisionState,
    ReleaseEvidenceAuthority,
    ReleaseEvidenceClassification,
    ReleaseEvidenceContractCode,
    ReleaseEvidenceContractError,
    ReleaseEvidenceEligibility,
    ReleaseEvidenceExecutionState,
    ReleaseEvidenceReviewState,
    ReleaseEvidenceVerification,
    SyntheticReleaseEvidenceCategory,
    SyntheticReleaseEvidenceManifest,
    SyntheticReleaseEvidenceRequirement,
    build_synthetic_release_evidence_manifest,
    snapshot_release_evidence_manifest,
    snapshot_release_evidence_requirement,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
BUILD_SHA = "f" * 40
NOW = datetime(2026, 11, 1, 21, 0, tzinfo=UTC)

EXPECTED_CATEGORIES = {
    "CLINICAL_POLICY_SIGN_OFF",
    "CONSENT_TEXT",
    "DATA_RETENTION_POLICY",
    "DATASET_CARDS",
    "INCIDENT_RUNBOOK",
    "MENTAL_HEALTH_POLICY_SIGN_OFF",
    "MODEL_CARDS",
    "PILOT_PROTOCOL",
    "PRIVACY_NOTICE",
    "RELEASE_CHECKLIST",
    "SELF_CARE_CONTENT_APPROVAL",
    "THREAT_MODEL",
    "VERIFIED_RESOURCE_REGISTRY",
}


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


def requirement(
    category: SyntheticReleaseEvidenceCategory = (
        SyntheticReleaseEvidenceCategory.CLINICAL_POLICY_SIGN_OFF
    ),
    *,
    build_sha: str = BUILD_SHA,
    created_at: datetime = NOW,
) -> SyntheticReleaseEvidenceRequirement:
    return SyntheticReleaseEvidenceRequirement(
        category=category,
        requirement_version="engineering.v1",
        build_sha=build_sha,
        requirement_hash=HASH_A,
        acceptance_criteria_hash=HASH_B,
        negative_test_plan_hash=HASH_C,
        responsible_roles_hash=HASH_D,
        created_at=created_at,
    )


def requirements() -> tuple[SyntheticReleaseEvidenceRequirement, ...]:
    return tuple(
        requirement(category) for category in reversed(tuple(SyntheticReleaseEvidenceCategory))
    )


def manifest() -> SyntheticReleaseEvidenceManifest:
    return build_synthetic_release_evidence_manifest(
        requirements(),
        manifest_id="syn_release_evidence_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_B,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )


def test_pre_pilot_category_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticReleaseEvidenceCategory} == EXPECTED_CATEGORIES
    assert len(SyntheticReleaseEvidenceCategory) == 13


def test_requirement_is_unverified_unexecuted_ineligible_and_human_gated() -> None:
    item = requirement()

    assert item.authority is ReleaseEvidenceAuthority.ENGINEERING_ONLY
    assert item.classification is ReleaseEvidenceClassification.ENGINEERING_SYNTHETIC
    assert item.verification is ReleaseEvidenceVerification.UNVERIFIED
    assert item.execution_state is ReleaseEvidenceExecutionState.NOT_EXECUTED
    assert item.eligibility is ReleaseEvidenceEligibility.NOT_ELIGIBLE
    assert item.review_state is (
        ReleaseEvidenceReviewState.HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED
    )
    assert item.decision_state is ReleaseDecisionState.NOT_RECORDED
    assert len(item.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", "CLINICAL_POLICY_SIGN_OFF"),
        ("requirement_version", "v1"),
        ("build_sha", "f" * 39),
        ("requirement_hash", "A" * 64),
        ("acceptance_criteria_hash", "b" * 63),
        ("negative_test_plan_hash", "not-a-hash"),
        ("responsible_roles_hash", "d" * 65),
        ("created_at", NOW.replace(tzinfo=None)),
        ("verification", "UNVERIFIED"),
        ("decision_state", "GO"),
    ],
)
def test_requirement_rejects_loose_malformed_or_authoritative_values(
    field: str, value: object
) -> None:
    values: dict[str, object] = {
        "category": SyntheticReleaseEvidenceCategory.CLINICAL_POLICY_SIGN_OFF,
        "requirement_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "requirement_hash": HASH_A,
        "acceptance_criteria_hash": HASH_B,
        "negative_test_plan_hash": HASH_C,
        "responsible_roles_hash": HASH_D,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(ReleaseEvidenceContractError):
        SyntheticReleaseEvidenceRequirement(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_and_requirement_is_immutable() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = requirement(created_at=non_utc)

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        item.category = SyntheticReleaseEvidenceCategory.CONSENT_TEXT  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("build_sha", "e" * 40),
        ("requirement_hash", HASH_B),
        ("acceptance_criteria_hash", HASH_C),
        ("negative_test_plan_hash", HASH_D),
        ("responsible_roles_hash", HASH_A),
    ],
)
def test_fingerprint_binds_every_build_and_evidence_plan_hash(field: str, value: str) -> None:
    values = {
        "category": SyntheticReleaseEvidenceCategory.CLINICAL_POLICY_SIGN_OFF,
        "requirement_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "requirement_hash": HASH_A,
        "acceptance_criteria_hash": HASH_B,
        "negative_test_plan_hash": HASH_C,
        "responsible_roles_hash": HASH_D,
        "created_at": NOW,
    }
    values[field] = value

    assert (
        SyntheticReleaseEvidenceRequirement(**values).fingerprint  # type: ignore[arg-type]
        != requirement().fingerprint
    )


def test_manifest_builder_is_complete_canonical_and_deterministic() -> None:
    first = manifest()
    second = build_synthetic_release_evidence_manifest(
        tuple(reversed(requirements())),
        manifest_id="syn_release_evidence_alpha",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        proposed_scope_hash=HASH_B,
        generated_at=NOW + timedelta(minutes=1),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert tuple(item.category.value for item in first.requirements) == tuple(
        sorted(EXPECTED_CATEGORIES)
    )
    assert first.decision_state is ReleaseDecisionState.NOT_RECORDED
    assert first.eligibility is ReleaseEvidenceEligibility.NOT_ELIGIBLE


def test_direct_manifest_rejects_duplicate_category_at_exact_cardinality() -> None:
    items = tuple(
        requirement(item)
        for item in sorted(SyntheticReleaseEvidenceCategory, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseEvidenceContractError) as captured:
        SyntheticReleaseEvidenceManifest(
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            requirements=items[:-1] + items[:1],
        )

    assert captured.value.code is ReleaseEvidenceContractCode.DUPLICATE_CATEGORY


def test_direct_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(ReleaseEvidenceContractError) as captured:
        SyntheticReleaseEvidenceManifest(
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            requirements=requirements(),
        )

    assert captured.value.code is ReleaseEvidenceContractCode.INVALID_ORDER


def test_manifest_rejects_requirement_for_a_different_build() -> None:
    items = tuple(
        requirement(
            category,
            build_sha="e" * 40
            if category is SyntheticReleaseEvidenceCategory.THREAT_MODEL
            else BUILD_SHA,
        )
        for category in sorted(SyntheticReleaseEvidenceCategory, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseEvidenceContractError) as captured:
        SyntheticReleaseEvidenceManifest(
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            requirements=items,
        )

    assert captured.value.code is ReleaseEvidenceContractCode.INVALID_VALUE


def test_manifest_rejects_requirement_created_after_manifest() -> None:
    items = tuple(
        requirement(
            category,
            created_at=NOW + timedelta(minutes=2)
            if category is SyntheticReleaseEvidenceCategory.PILOT_PROTOCOL
            else NOW,
        )
        for category in sorted(SyntheticReleaseEvidenceCategory, key=lambda x: x.value)
    )

    with pytest.raises(ReleaseEvidenceContractError) as captured:
        SyntheticReleaseEvidenceManifest(
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW + timedelta(minutes=1),
            requirements=items,
        )

    assert captured.value.code is ReleaseEvidenceContractCode.INVALID_CHRONOLOGY


def test_builder_rejects_wrong_cardinality_before_item_inspection() -> None:
    hostile_items = tuple(HostileInput() for _ in range(14))

    with pytest.raises(ReleaseEvidenceContractError) as captured:
        build_synthetic_release_evidence_manifest(
            hostile_items,  # type: ignore[arg-type]
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is ReleaseEvidenceContractCode.INCOMPLETE_INVENTORY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_input_inspection(environment: Environment) -> None:
    with pytest.raises(ReleaseEvidenceContractError) as captured:
        build_synthetic_release_evidence_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_release_evidence_alpha",
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is ReleaseEvidenceContractCode.PROTECTED_ENVIRONMENT


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = requirement()
    inventory = manifest()
    object.__setattr__(item, "requirement_hash", HASH_D)
    object.__setattr__(inventory, "generated_at", NOW)

    with pytest.raises(ReleaseEvidenceContractError):
        snapshot_release_evidence_requirement(item)
    with pytest.raises(ReleaseEvidenceContractError):
        snapshot_release_evidence_manifest(inventory)


def test_errors_and_representations_are_content_free() -> None:
    hostile = "secret-patient@example.test"

    with pytest.raises(ReleaseEvidenceContractError) as captured:
        SyntheticReleaseEvidenceManifest(
            manifest_id=hostile,
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            proposed_scope_hash=HASH_B,
            generated_at=NOW,
            requirements=(),
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    assert HASH_A not in repr(requirement())
    assert HASH_A not in repr(manifest())


def test_contract_exposes_no_approval_release_or_operational_authority() -> None:
    item = manifest()
    for prohibited in (
        "approve",
        "conditional_go",
        "deploy",
        "execute",
        "go",
        "no_go",
        "persist",
        "promote",
        "publish",
        "release",
        "rollback",
        "run",
        "sign",
        "start_pilot",
        "waive",
    ):
        assert not hasattr(item, prohibited)


def test_release_evidence_planning_has_no_runtime_registration_or_route() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "release-readiness" not in module_ids
    assert all("release" not in path and "pilot" not in path for path in route_paths)
