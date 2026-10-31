"""Closed test-only rule mapping for P14-C mechanical verification."""

from datetime import datetime

from app.modules.mental_health.contracts import SyntheticSignalCode, SyntheticSignalState
from app.modules.mental_health.policy import (
    SyntheticPolicyArtifact,
    SyntheticPolicyReasonCode,
    SyntheticPolicyRule,
    SyntheticPolicyState,
    SyntheticRouteState,
    SyntheticRuleKind,
)


def synthetic_policy_fixture(
    *,
    effective_at: datetime,
    expires_at: datetime,
    state: SyntheticPolicyState = SyntheticPolicyState.TEST_ONLY_ENABLED,
) -> SyntheticPolicyArtifact:
    rules = (
        SyntheticPolicyRule(
            rule_id="syn_mh_policy_rule_alpha",
            signal_code=SyntheticSignalCode.ALPHA,
            signal_state=SyntheticSignalState.PRESENT,
            kind=SyntheticRuleKind.STANDARD,
            route=SyntheticRouteState.ALPHA,
            reason_code=SyntheticPolicyReasonCode.ALPHA,
        ),
        SyntheticPolicyRule(
            rule_id="syn_mh_policy_rule_beta",
            signal_code=SyntheticSignalCode.BETA,
            signal_state=SyntheticSignalState.PRESENT,
            kind=SyntheticRuleKind.STANDARD,
            route=SyntheticRouteState.BETA,
            reason_code=SyntheticPolicyReasonCode.BETA,
        ),
        SyntheticPolicyRule(
            rule_id="syn_mh_policy_rule_delta",
            signal_code=SyntheticSignalCode.DELTA,
            signal_state=SyntheticSignalState.PRESENT,
            kind=SyntheticRuleKind.OVERRIDE,
            route=SyntheticRouteState.GAMMA,
            reason_code=SyntheticPolicyReasonCode.DELTA,
        ),
        SyntheticPolicyRule(
            rule_id="syn_mh_policy_rule_gamma",
            signal_code=SyntheticSignalCode.GAMMA,
            signal_state=SyntheticSignalState.UNCERTAIN,
            kind=SyntheticRuleKind.CLARIFICATION,
            route=SyntheticRouteState.CLARIFICATION_REQUIRED,
            reason_code=SyntheticPolicyReasonCode.GAMMA,
        ),
    )
    return SyntheticPolicyArtifact.create(
        policy_id="syn_mh_policy_fixture",
        policy_version="engineering.v1",
        effective_at=effective_at,
        expires_at=expires_at,
        state=state,
        rules=rules,
    )


__all__ = ["synthetic_policy_fixture"]
