"""Adversarial fixture, privacy, and architecture boundaries for P9-B/P9-C."""

from dataclasses import fields, replace
from pathlib import Path
from traceback import format_exception
from typing import Any

import pytest

from app.main import create_app
from app.modules.safety.contracts import (
    InvalidSyntheticRuleSetError,
    InvalidSyntheticSafetyInputError,
    SyntheticAdvisory,
    SyntheticRule,
    SyntheticRuleSet,
    SyntheticSafetyInput,
    SyntheticSignal,
)
from app.modules.safety.domain import SafetyDecision, SafetyRoute
from app.modules.safety.policies import PolicyApprovalState, SafetyPolicyType
from app.modules.safety.synthetic import (
    SYNTHETIC_FIXTURE_ID,
    SYNTHETIC_RULE_SET,
    SYNTHETIC_RULES_CHECKSUM,
    TRUSTED_SYNTHETIC_RULES_CHECKSUM,
)


def cloned_rule(**changes: Any) -> SyntheticRule:
    return replace(SYNTHETIC_RULE_SET.rules[0], **changes)


def create_rule_set(*, rules: tuple[SyntheticRule, ...]) -> SyntheticRuleSet:
    return SyntheticRuleSet.create(
        fixture_id=SYNTHETIC_FIXTURE_ID,
        policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
        policy_id="synthetic-physical-safety-metadata",
        policy_version="engineering.1",
        approval_state=PolicyApprovalState.ENGINEERING_ONLY,
        reason_code_namespace="SYNTHETIC_",
        rules=rules,
    )


def test_contract_shapes_have_no_patient_or_free_text_authority() -> None:
    assert tuple(item.name for item in fields(SyntheticSafetyInput)) == (
        "signals",
        "advisory",
    )
    assert tuple(item.name for item in fields(SyntheticRule)) == (
        "rule_id",
        "signal",
        "kind",
        "route",
        "reason_code",
        "requires_clarification",
        "blocks_self_care",
    )
    forbidden = {
        "patient_id",
        "encounter_id",
        "symptoms",
        "vitals",
        "diagnosis",
        "treatment",
        "free_text",
        "model_score",
        "callback",
        "expression",
    }
    assert forbidden.isdisjoint(item.name for item in fields(SyntheticSafetyInput))
    assert forbidden.isdisjoint(item.name for item in fields(SyntheticRule))
    assert "diagnosis" not in {item.name for item in fields(SafetyDecision)}


def test_fixture_identity_is_visibly_synthetic_and_metadata_bound() -> None:
    assert SYNTHETIC_RULE_SET.fixture_id == "synthetic-safety-mechanics.v1"
    assert SYNTHETIC_RULE_SET.policy_id == "synthetic-physical-safety-metadata"
    assert SYNTHETIC_RULE_SET.policy_version == "engineering.1"
    assert SYNTHETIC_RULE_SET.approval_state is PolicyApprovalState.ENGINEERING_ONLY
    assert SYNTHETIC_RULE_SET.reason_code_namespace == "SYNTHETIC_"
    assert not hasattr(PolicyApprovalState, "APPROVED")


def test_rule_set_checksum_covers_canonical_rules_not_clinical_approval() -> None:
    assert TRUSTED_SYNTHETIC_RULES_CHECKSUM == (
        "7e7f570a631eabd4e91a62fdfdc0031b763535340d55cea86f2a54186f34398f"
    )
    assert SYNTHETIC_RULES_CHECKSUM == TRUSTED_SYNTHETIC_RULES_CHECKSUM
    reversed_set = create_rule_set(rules=tuple(reversed(SYNTHETIC_RULE_SET.rules)))
    assert reversed_set.rules_checksum == SYNTHETIC_RULE_SET.rules_checksum
    changed = tuple(
        replace(rule, reason_code="SYNTHETIC_CHANGED_A")
        if rule.signal is SyntheticSignal.SYNTHETIC_PRIORITY_A
        else rule
        for rule in SYNTHETIC_RULE_SET.rules
    )
    changed_set = create_rule_set(rules=changed)
    assert changed_set.rules_checksum != SYNTHETIC_RULE_SET.rules_checksum


@pytest.mark.parametrize(
    "changes",
    [
        {"rule_id": "not-synthetic"},
        {"signal": "SYNTHETIC_OVERRIDE_A"},
        {"kind": "HARD_OVERRIDE"},
        {"route": "EMERGENCY"},
        {"reason_code": "PATIENT_FREE_TEXT"},
        {"reason_code": "SYNTHETIC_" + "A" * 64},
        {"requires_clarification": 1},
        {"blocks_self_care": 0},
        {"route": SafetyRoute.EMERGENCY},
    ],
)
def test_invalid_rule_metadata_or_contradictory_outcome_is_rejected(
    changes: dict[str, Any],
) -> None:
    with pytest.raises(InvalidSyntheticRuleSetError):
        cloned_rule(**changes)


def test_duplicate_rule_ids_and_duplicate_signal_definitions_are_rejected() -> None:
    first = SYNTHETIC_RULE_SET.rules[0]
    duplicate_id = replace(
        SYNTHETIC_RULE_SET.rules[1],
        rule_id=first.rule_id,
    )
    with pytest.raises(InvalidSyntheticRuleSetError, match="duplicate"):
        create_rule_set(rules=(first, duplicate_id))

    duplicate_signal = replace(
        SYNTHETIC_RULE_SET.rules[1],
        signal=first.signal,
    )
    with pytest.raises(InvalidSyntheticRuleSetError, match="contradictory"):
        create_rule_set(rules=(first, duplicate_signal))


@pytest.mark.parametrize(
    "changes",
    [
        {"fixture_id": "real-policy"},
        {"policy_type": "PHYSICAL_SAFETY"},
        {"policy_id": "not allowed"},
        {"policy_version": ""},
        {"approval_state": "APPROVED"},
        {"reason_code_namespace": "REAL_"},
        {"rules": []},
    ],
)
def test_invalid_rule_set_metadata_fails_with_typed_error(changes: dict[str, Any]) -> None:
    values: dict[str, Any] = {
        "fixture_id": SYNTHETIC_FIXTURE_ID,
        "policy_type": SafetyPolicyType.PHYSICAL_SAFETY,
        "policy_id": SYNTHETIC_RULE_SET.policy_id,
        "policy_version": SYNTHETIC_RULE_SET.policy_version,
        "approval_state": PolicyApprovalState.ENGINEERING_ONLY,
        "reason_code_namespace": "SYNTHETIC_",
        "rules": SYNTHETIC_RULE_SET.rules,
    }
    values.update(changes)
    with pytest.raises(InvalidSyntheticRuleSetError):
        SyntheticRuleSet.create(**values)


def test_unknown_input_and_advisory_primitives_are_rejected_without_echo() -> None:
    privacy_canary = "private-patient-narrative-canary"
    with pytest.raises(InvalidSyntheticSafetyInputError) as caught:
        SyntheticSafetyInput(signals=(privacy_canary,))  # type: ignore[arg-type]
    rendered = "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )
    assert privacy_canary not in str(caught.value)
    assert privacy_canary not in rendered
    with pytest.raises(InvalidSyntheticSafetyInputError):
        SyntheticSafetyInput(
            signals=(SyntheticSignal.SYNTHETIC_COMPLETE_A,),
            advisory="LOW_RISK",  # type: ignore[arg-type]
        )


def test_signal_and_advisory_vocabularies_are_closed_and_nonmedical() -> None:
    assert tuple(signal.value for signal in SyntheticSignal) == (
        "SYNTHETIC_COMPLETE_A",
        "SYNTHETIC_OVERRIDE_A",
        "SYNTHETIC_OVERRIDE_B",
        "SYNTHETIC_MISSING_A",
        "SYNTHETIC_AMBIGUOUS_A",
        "SYNTHETIC_EXCLUDE_A",
        "SYNTHETIC_PRIORITY_A",
        "SYNTHETIC_ROUTINE_A",
        "SYNTHETIC_SELF_CARE_A",
    )
    assert tuple(item.value for item in SyntheticAdvisory) == ("LOW_RISK",)
    with pytest.raises(ValueError):
        SyntheticSignal("PATIENT_SYMPTOM")


def test_safety_code_has_no_runtime_provider_network_or_persistence_imports() -> None:
    module_root = Path(__file__).parents[1] / "app" / "modules" / "safety"
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(module_root.glob("*.py"))
    ).lower()
    for forbidden in (
        "fastapi",
        "sqlalchemy",
        "httpx",
        "requests",
        "urllib",
        "socket",
        "ai_orchestration",
        "clinical_intake",
        "provenance",
        "qiskit",
        "pennylane",
    ):
        assert forbidden not in source


def test_safety_engine_and_presentation_have_no_api_binding_table_or_frontend_route() -> None:
    repository_root = Path(__file__).parents[2]
    application_root = repository_root / "backend" / "app"
    paths = create_app().openapi()["paths"]
    assert not any("safety" in path or path.endswith("/messages") for path in paths)
    assert "modules.safety" not in (application_root / "main.py").read_text(encoding="utf-8")

    migrations = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (repository_root / "backend" / "migrations" / "versions").glob("*.py")
    )
    assert "safety_decisions" not in migrations
    assert "policy_versions" not in migrations

    patient_app = repository_root / "apps" / "patient-web"
    safety_files = {
        path.relative_to(patient_app).as_posix()
        for root in (
            patient_app / "components" / "safety",
            patient_app / "lib" / "safety",
        )
        for path in root.rglob("*")
        if path.is_file()
    }
    safety_files.update(
        path.relative_to(patient_app).as_posix()
        for path in (patient_app / "tests").glob("*safety*")
        if path.is_file()
    )
    assert safety_files == {
        "components/safety/synthetic-safety-preview.tsx",
        "lib/safety/presentation.ts",
        "tests/safety-presentation.test.tsx",
    }
    assert not (patient_app / "app" / "safety").exists()
    assert not (patient_app / "app" / "api" / "safety").exists()

    route_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in (patient_app / "app").rglob("*.tsx")
    )
    assert "SyntheticSafetyPreview" not in route_sources
    assert "projectSyntheticSafetyPresentation" not in route_sources
