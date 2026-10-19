"""Fail-closed safety policy metadata registry tests."""

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Any

import pytest

from app.config.settings import Environment
from app.main import create_app
from app.modules.safety.policies import (
    SYNTHETIC_PHYSICAL_SAFETY_METADATA,
    ActivePolicySelection,
    AmbiguousPolicySelectionError,
    DuplicatePolicyRegistrationError,
    InvalidPolicyMetadataError,
    PolicyActivationState,
    PolicyApprovalState,
    PolicyEnvironmentRejectedError,
    PolicyUnavailableError,
    SafetyPolicyMetadata,
    SafetyPolicyRegistry,
    SafetyPolicyType,
    UnknownPolicyError,
    build_default_policy_registry,
    build_synthetic_policy_registry,
)


def inactive_metadata(policy_id: str = "future-policy") -> SafetyPolicyMetadata:
    return SafetyPolicyMetadata.create(
        policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
        policy_id=policy_id,
        policy_version="draft.1",
        approval_state=PolicyApprovalState.CLINICAL_APPROVAL_REQUIRED,
        activation_state=PolicyActivationState.INACTIVE,
        supported_environments=(),
        reason_code_namespace="FUTURE_",
    )


def selection_for(policy: SafetyPolicyMetadata) -> ActivePolicySelection:
    return ActivePolicySelection(
        policy_type=policy.policy_type,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
    )


def test_fixture_is_visibly_synthetic_metadata_not_clinical_authority() -> None:
    fixture = SYNTHETIC_PHYSICAL_SAFETY_METADATA
    assert "synthetic" in fixture.policy_id
    assert "engineering" in fixture.policy_version
    assert fixture.approval_state is PolicyApprovalState.ENGINEERING_ONLY
    assert fixture.activation_state is PolicyActivationState.ENGINEERING_TEST_ONLY
    assert set(fixture.supported_environments) == {Environment.LOCAL, Environment.TEST}
    assert not hasattr(PolicyApprovalState, "APPROVED")
    assert not hasattr(fixture, "rules")
    assert not hasattr(fixture, "thresholds")


def test_metadata_is_frozen_and_checksum_is_deterministic() -> None:
    fixture = SYNTHETIC_PHYSICAL_SAFETY_METADATA
    recreated = SafetyPolicyMetadata.create(
        policy_type=fixture.policy_type,
        policy_id=fixture.policy_id,
        policy_version=fixture.policy_version,
        approval_state=fixture.approval_state,
        activation_state=fixture.activation_state,
        supported_environments=fixture.supported_environments,
        reason_code_namespace=fixture.reason_code_namespace,
    )
    assert recreated == fixture
    with pytest.raises(FrozenInstanceError):
        fixture.policy_id = "changed"  # type: ignore[misc]


def test_checksum_tampering_and_identity_change_fail_closed() -> None:
    fixture = SYNTHETIC_PHYSICAL_SAFETY_METADATA
    with pytest.raises(InvalidPolicyMetadataError, match="checksum"):
        replace(fixture, metadata_checksum="0" * 64)
    with pytest.raises(InvalidPolicyMetadataError, match="checksum"):
        replace(fixture, policy_version="engineering.2")


def test_registry_revalidates_a_tampered_metadata_instance() -> None:
    metadata = inactive_metadata()
    object.__setattr__(metadata, "policy_version", "draft.2")
    with pytest.raises(InvalidPolicyMetadataError, match="checksum"):
        SafetyPolicyRegistry(policies=(metadata,))


@pytest.mark.parametrize(
    "change",
    [
        {"policy_type": "PHYSICAL_SAFETY"},
        {"policy_id": "UPPERCASE"},
        {"policy_version": " bad "},
        {"approval_state": "ENGINEERING_ONLY"},
        {"activation_state": "ENGINEERING_TEST_ONLY"},
        {"supported_environments": [Environment.LOCAL]},
        {"reason_code_namespace": "not-machine"},
        {"metadata_checksum": "nope"},
    ],
)
def test_malformed_or_unknown_metadata_fails_closed(change: dict[str, Any]) -> None:
    values: dict[str, Any] = {
        "policy_type": SafetyPolicyType.PHYSICAL_SAFETY,
        "policy_id": "future-policy",
        "policy_version": "draft.1",
        "approval_state": PolicyApprovalState.CLINICAL_APPROVAL_REQUIRED,
        "activation_state": PolicyActivationState.INACTIVE,
        "supported_environments": (),
        "reason_code_namespace": "FUTURE_",
    }
    values.update(change)
    if "metadata_checksum" not in values:
        values["metadata_checksum"] = "0" * 64
    with pytest.raises(InvalidPolicyMetadataError):
        SafetyPolicyMetadata(**values)


def test_factory_rejects_unsupported_primitive_policy_type_with_typed_error() -> None:
    with pytest.raises(InvalidPolicyMetadataError):
        SafetyPolicyMetadata.create(
            policy_type="PHYSICAL_SAFETY",  # type: ignore[arg-type]
            policy_id="future-policy",
            policy_version="draft.1",
            approval_state=PolicyApprovalState.CLINICAL_APPROVAL_REQUIRED,
            activation_state=PolicyActivationState.INACTIVE,
            supported_environments=(),
            reason_code_namespace="FUTURE_",
        )


def test_environment_metadata_must_be_unique_ordered_and_non_protected() -> None:
    create = SafetyPolicyMetadata.create
    common: dict[str, Any] = {
        "policy_type": SafetyPolicyType.PHYSICAL_SAFETY,
        "policy_id": "synthetic-policy",
        "policy_version": "engineering.1",
        "approval_state": PolicyApprovalState.ENGINEERING_ONLY,
        "activation_state": PolicyActivationState.ENGINEERING_TEST_ONLY,
        "reason_code_namespace": "SYNTHETIC_",
    }
    for environments in (
        (Environment.TEST, Environment.LOCAL),
        (Environment.LOCAL, Environment.LOCAL),
        (Environment.PRODUCTION,),
        (),
    ):
        with pytest.raises(InvalidPolicyMetadataError):
            create(supported_environments=environments, **common)


def test_inactive_metadata_cannot_claim_supported_environments() -> None:
    with pytest.raises(InvalidPolicyMetadataError):
        SafetyPolicyMetadata.create(
            policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
            policy_id="future-policy",
            policy_version="draft.1",
            approval_state=PolicyApprovalState.CLINICAL_APPROVAL_REQUIRED,
            activation_state=PolicyActivationState.INACTIVE,
            supported_environments=(Environment.LOCAL,),
            reason_code_namespace="FUTURE_",
        )


def test_default_registry_has_no_implicit_or_low_risk_policy() -> None:
    registry = build_default_policy_registry()
    assert registry.all() == ()
    for environment in Environment:
        with pytest.raises(PolicyUnavailableError):
            registry.get_active_policy(
                policy_type=SafetyPolicyType.PHYSICAL_SAFETY, environment=environment
            )


@pytest.mark.parametrize("environment", [Environment.LOCAL, Environment.TEST])
def test_explicit_synthetic_registry_exposes_metadata_only_in_engineering_environments(
    environment: Environment,
) -> None:
    assert (
        build_synthetic_policy_registry().get_active_policy(
            policy_type=SafetyPolicyType.PHYSICAL_SAFETY, environment=environment
        )
        is SYNTHETIC_PHYSICAL_SAFETY_METADATA
    )


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_actual_selection_boundary_always_rejects_fixture_in_protected_environments(
    environment: Environment,
) -> None:
    registry = build_synthetic_policy_registry()
    with pytest.raises(PolicyEnvironmentRejectedError):
        registry.get_active_policy(
            policy_type=SafetyPolicyType.PHYSICAL_SAFETY, environment=environment
        )


def test_duplicate_registration_and_selection_are_rejected() -> None:
    fixture = SYNTHETIC_PHYSICAL_SAFETY_METADATA
    with pytest.raises(DuplicatePolicyRegistrationError):
        SafetyPolicyRegistry(policies=(fixture, fixture))
    selected = selection_for(fixture)
    with pytest.raises(AmbiguousPolicySelectionError):
        SafetyPolicyRegistry(policies=(fixture,), selections=(selected, selected))


def test_unknown_mismatched_and_inactive_selection_are_rejected() -> None:
    fixture = SYNTHETIC_PHYSICAL_SAFETY_METADATA
    with pytest.raises(UnknownPolicyError):
        SafetyPolicyRegistry(
            policies=(fixture,),
            selections=(replace(selection_for(fixture), policy_version="engineering.2"),),
        )
    inactive = inactive_metadata()
    with pytest.raises(PolicyUnavailableError):
        SafetyPolicyRegistry(policies=(inactive,), selections=(selection_for(inactive),))
    with pytest.raises(UnknownPolicyError):
        SafetyPolicyRegistry(policies=(fixture,)).require(
            policy_id=fixture.policy_id, policy_version="missing"
        )


def test_registration_listing_is_deterministic() -> None:
    first = inactive_metadata("alpha-policy")
    second = inactive_metadata("zulu-policy")
    assert SafetyPolicyRegistry(policies=(second, first)).all() == (first, second)


def test_registry_itself_is_immutable() -> None:
    registry = build_default_policy_registry()
    with pytest.raises(FrozenInstanceError):
        registry._policies = {}  # type: ignore[misc]


def test_registry_rejects_dynamic_container_and_primitive_environment() -> None:
    with pytest.raises(InvalidPolicyMetadataError):
        SafetyPolicyRegistry(policies=[SYNTHETIC_PHYSICAL_SAFETY_METADATA])  # type: ignore[arg-type]
    with pytest.raises(InvalidPolicyMetadataError):
        build_synthetic_policy_registry().get_active_policy(
            policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
            environment="local",  # type: ignore[arg-type]
        )


def test_p9a_adds_no_route_table_or_runtime_registration() -> None:
    paths = create_app().openapi()["paths"]
    assert not any("safety" in path for path in paths)

    source_root = Path(__file__).parents[1] / "app"
    main_source = (source_root / "main.py").read_text(encoding="utf-8")
    assert "modules.safety" not in main_source

    safety_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((source_root / "modules" / "safety").glob("*.py"))
    )
    for forbidden in (
        "fastapi",
        "sqlalchemy",
        "httpx",
        "ClinicalIntakeRepository",
        "AIOrchestrationService",
    ):
        assert forbidden not in safety_source

    migration_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (source_root.parent / "migrations" / "versions").glob("*.py")
    )
    assert "safety_decisions" not in migration_source
    assert "policy_versions" not in migration_source
