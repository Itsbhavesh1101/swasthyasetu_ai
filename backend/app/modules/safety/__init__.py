"""Physical-safety contracts and synthetic mechanics; no runtime activation."""

from app.modules.safety.contracts import (
    SyntheticAdvisory,
    SyntheticRule,
    SyntheticRuleKind,
    SyntheticRuleSet,
    SyntheticSafetyInput,
    SyntheticSignal,
)
from app.modules.safety.domain import SafetyDecision, SafetyRoute
from app.modules.safety.engine import SyntheticSafetyEngine
from app.modules.safety.policies import (
    ActivePolicySelection,
    PolicyActivationState,
    PolicyApprovalState,
    SafetyPolicyMetadata,
    SafetyPolicyRegistry,
    SafetyPolicyType,
)

__all__ = [
    "ActivePolicySelection",
    "PolicyActivationState",
    "PolicyApprovalState",
    "SafetyDecision",
    "SafetyPolicyMetadata",
    "SafetyPolicyRegistry",
    "SafetyPolicyType",
    "SafetyRoute",
    "SyntheticAdvisory",
    "SyntheticRule",
    "SyntheticRuleKind",
    "SyntheticRuleSet",
    "SyntheticSafetyEngine",
    "SyntheticSafetyInput",
    "SyntheticSignal",
]
