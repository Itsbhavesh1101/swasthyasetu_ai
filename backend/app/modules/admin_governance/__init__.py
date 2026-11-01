"""Detached engineering-synthetic admin authorization contracts."""

from app.modules.admin_governance.contracts import (
    MAX_SYNTHETIC_GRANTS,
    SYNTHETIC_ADMIN_CONTRACT_VERSION,
    AdminAuthority,
    AdminClassification,
    AdminContractCode,
    AdminContractError,
    AdminDecisionDisposition,
    AdminDecisionReason,
    AdminVerification,
    SyntheticAdminAction,
    SyntheticAdminDecision,
    SyntheticAdminGrant,
    SyntheticAdminRequest,
    snapshot_admin_grant,
    snapshot_admin_request,
)
from app.modules.admin_governance.preflight import evaluate_synthetic_admin_preflight

__all__ = [
    "MAX_SYNTHETIC_GRANTS",
    "SYNTHETIC_ADMIN_CONTRACT_VERSION",
    "AdminAuthority",
    "AdminClassification",
    "AdminContractCode",
    "AdminContractError",
    "AdminDecisionDisposition",
    "AdminDecisionReason",
    "AdminVerification",
    "SyntheticAdminAction",
    "SyntheticAdminDecision",
    "SyntheticAdminGrant",
    "SyntheticAdminRequest",
    "evaluate_synthetic_admin_preflight",
    "snapshot_admin_grant",
    "snapshot_admin_request",
]
