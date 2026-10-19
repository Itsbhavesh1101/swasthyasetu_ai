"""Compile-time nonclinical fixture for P9-B mechanical verification only."""

from __future__ import annotations

from typing import Final

from app.modules.safety.contracts import (
    InvalidSyntheticRuleSetError,
    SyntheticRule,
    SyntheticRuleKind,
    SyntheticRuleSet,
    SyntheticSignal,
)
from app.modules.safety.domain import SafetyRoute
from app.modules.safety.policies import (
    SYNTHETIC_PHYSICAL_SAFETY_METADATA,
    PolicyApprovalState,
    SafetyPolicyType,
)

SYNTHETIC_FIXTURE_ID: Final = "synthetic-safety-mechanics.v1"
TRUSTED_SYNTHETIC_RULES_CHECKSUM: Final = (
    "7e7f570a631eabd4e91a62fdfdc0031b763535340d55cea86f2a54186f34398f"
)

_SYNTHETIC_RULES: Final = (
    SyntheticRule(
        rule_id="synthetic-rule-ambiguous-a",
        signal=SyntheticSignal.SYNTHETIC_AMBIGUOUS_A,
        kind=SyntheticRuleKind.CLARIFICATION,
        route=SafetyRoute.CLARIFICATION_REQUIRED,
        reason_code="SYNTHETIC_AMBIGUOUS_A",
        requires_clarification=True,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-exclude-a",
        signal=SyntheticSignal.SYNTHETIC_EXCLUDE_A,
        kind=SyntheticRuleKind.SELF_CARE_EXCLUSION,
        route=SafetyRoute.ROUTINE_CARE,
        reason_code="SYNTHETIC_EXCLUDE_A",
        requires_clarification=False,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-missing-a",
        signal=SyntheticSignal.SYNTHETIC_MISSING_A,
        kind=SyntheticRuleKind.CLARIFICATION,
        route=SafetyRoute.CLARIFICATION_REQUIRED,
        reason_code="SYNTHETIC_MISSING_A",
        requires_clarification=True,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-override-a",
        signal=SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        kind=SyntheticRuleKind.HARD_OVERRIDE,
        route=SafetyRoute.EMERGENCY,
        reason_code="SYNTHETIC_OVERRIDE_A",
        requires_clarification=False,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-override-b",
        signal=SyntheticSignal.SYNTHETIC_OVERRIDE_B,
        kind=SyntheticRuleKind.HARD_OVERRIDE,
        route=SafetyRoute.EMERGENCY,
        reason_code="SYNTHETIC_OVERRIDE_B",
        requires_clarification=False,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-priority-a",
        signal=SyntheticSignal.SYNTHETIC_PRIORITY_A,
        kind=SyntheticRuleKind.PRIORITY_ROUTE,
        route=SafetyRoute.PRIORITY_REVIEW,
        reason_code="SYNTHETIC_PRIORITY_A",
        requires_clarification=False,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-routine-a",
        signal=SyntheticSignal.SYNTHETIC_ROUTINE_A,
        kind=SyntheticRuleKind.ROUTINE_ROUTE,
        route=SafetyRoute.ROUTINE_CARE,
        reason_code="SYNTHETIC_ROUTINE_A",
        requires_clarification=False,
        blocks_self_care=True,
    ),
    SyntheticRule(
        rule_id="synthetic-rule-self-care-a",
        signal=SyntheticSignal.SYNTHETIC_SELF_CARE_A,
        kind=SyntheticRuleKind.SELF_CARE_ROUTE,
        route=SafetyRoute.SUPPORTED_SELF_CARE,
        reason_code="SYNTHETIC_SELF_CARE_A",
        requires_clarification=False,
        blocks_self_care=False,
    ),
)

SYNTHETIC_RULE_SET: Final = SyntheticRuleSet.create(
    fixture_id=SYNTHETIC_FIXTURE_ID,
    policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
    policy_id=SYNTHETIC_PHYSICAL_SAFETY_METADATA.policy_id,
    policy_version=SYNTHETIC_PHYSICAL_SAFETY_METADATA.policy_version,
    approval_state=PolicyApprovalState.ENGINEERING_ONLY,
    reason_code_namespace=SYNTHETIC_PHYSICAL_SAFETY_METADATA.reason_code_namespace,
    rules=_SYNTHETIC_RULES,
)

if SYNTHETIC_RULE_SET.rules_checksum != TRUSTED_SYNTHETIC_RULES_CHECKSUM:
    raise InvalidSyntheticRuleSetError("synthetic fixture manifest mismatch")

SYNTHETIC_RULES_CHECKSUM: Final = TRUSTED_SYNTHETIC_RULES_CHECKSUM
