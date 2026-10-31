"""Compile-time nonclinical P15-B eligibility fixture."""

from datetime import UTC, datetime
from typing import Final

from app.modules.self_care.eligibility import (
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityPolicy,
    SyntheticEligibilityPolicyState,
    SyntheticEligibilityPredicate,
    SyntheticEligibilityRule,
)

TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH: Final = (
    "314e181c42ea1c752ea9b6cb2a3c7804e09eb729f34e93c2746f0e530e7145b0"
)

SYNTHETIC_ELIGIBILITY_POLICY: Final = SyntheticEligibilityPolicy.create(
    policy_id="syn_selfcare_eligibility_fixture",
    policy_version="engineering.v1",
    effective_at=datetime(2026, 10, 31, tzinfo=UTC),
    expires_at=datetime(2027, 10, 31, tzinfo=UTC),
    state=SyntheticEligibilityPolicyState.TEST_ONLY_ACTIVE,
    rules=(
        SyntheticEligibilityRule(
            rule_id="syn_selfcare_eligibility_rule_alpha",
            guidance_id="syn_selfcare_guidance_alpha",
            guidance_version="engineering.v1",
            required_predicate=SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            exclusion_predicate=SyntheticEligibilityPredicate.EXCLUDE_ALPHA,
        ),
        SyntheticEligibilityRule(
            rule_id="syn_selfcare_eligibility_rule_beta",
            guidance_id="syn_selfcare_guidance_beta",
            guidance_version="engineering.v1",
            required_predicate=SyntheticEligibilityPredicate.INCLUDE_BETA,
            exclusion_predicate=SyntheticEligibilityPredicate.EXCLUDE_BETA,
        ),
    ),
)

if SYNTHETIC_ELIGIBILITY_POLICY.content_hash != TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH:
    raise EligibilityContractError(EligibilityContractCode.HASH_MISMATCH)

__all__ = [
    "SYNTHETIC_ELIGIBILITY_POLICY",
    "TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH",
]
