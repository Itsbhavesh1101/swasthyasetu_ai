"""Fail-closed evaluator for detached engineering-synthetic admin contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from app.config import Environment
from app.modules.admin_governance.contracts import (
    MAX_SYNTHETIC_GRANTS,
    AdminContractCode,
    AdminContractError,
    AdminDecisionDisposition,
    AdminDecisionReason,
    SyntheticAdminDecision,
    SyntheticAdminGrant,
    SyntheticAdminRequest,
    snapshot_admin_grant,
    snapshot_admin_request,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


def _error(code: AdminContractCode) -> AdminContractError:
    return AdminContractError(code)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(AdminContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _matches(request: SyntheticAdminRequest, grant: SyntheticAdminGrant) -> bool:
    return (
        request.actor_id == grant.actor_id
        and request.action is grant.action
        and request.object_id == grant.object_id
        and request.object_version == grant.object_version
        and request.object_hash == grant.object_hash
        and request.institution_id == grant.institution_id
        and request.source_id == grant.source_id
        and request.purpose_id == grant.purpose_id
    )


def _decision(
    request: SyntheticAdminRequest,
    *,
    disposition: AdminDecisionDisposition,
    reason: AdminDecisionReason,
    matched_grant_id: str | None,
    evaluated_at: datetime,
) -> SyntheticAdminDecision:
    return SyntheticAdminDecision(
        request_id=request.request_id,
        request_fingerprint=request.fingerprint,
        disposition=disposition,
        reason=reason,
        matched_grant_id=matched_grant_id,
        evaluated_at=evaluated_at,
    )


def evaluate_synthetic_admin_preflight(
    request: SyntheticAdminRequest,
    grants: tuple[SyntheticAdminGrant, ...],
    *,
    evaluated_at: datetime,
    environment: Environment,
) -> SyntheticAdminDecision:
    """Match an exact active synthetic grant; never authorize a runtime operation."""

    if type(environment) is not Environment:
        raise _error(AdminContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(AdminContractCode.PROTECTED_ENVIRONMENT)

    safe_request = snapshot_admin_request(request)
    safe_evaluated_at = _utc(evaluated_at)
    if safe_evaluated_at < safe_request.created_at:
        raise _error(AdminContractCode.INVALID_CHRONOLOGY)

    if not safe_request.mfa_verified:
        return _decision(
            safe_request,
            disposition=AdminDecisionDisposition.ABSTAINED,
            reason=AdminDecisionReason.MFA_NOT_VERIFIED,
            matched_grant_id=None,
            evaluated_at=safe_evaluated_at,
        )

    if type(grants) is not tuple or len(grants) > MAX_SYNTHETIC_GRANTS:
        raise _error(AdminContractCode.INVALID_TYPE)
    safe_grants = tuple(
        sorted((snapshot_admin_grant(item) for item in grants), key=lambda item: item.grant_id)
    )
    if len({item.grant_id for item in safe_grants}) != len(safe_grants):
        raise _error(AdminContractCode.DUPLICATE_GRANT)

    matches = tuple(
        item
        for item in safe_grants
        if item.valid_from <= safe_evaluated_at < item.expires_at and _matches(safe_request, item)
    )
    if len(matches) > 1:
        raise _error(AdminContractCode.AMBIGUOUS_GRANT)
    if not matches:
        return _decision(
            safe_request,
            disposition=AdminDecisionDisposition.ABSTAINED,
            reason=AdminDecisionReason.NO_EXACT_ACTIVE_GRANT,
            matched_grant_id=None,
            evaluated_at=safe_evaluated_at,
        )
    return _decision(
        safe_request,
        disposition=AdminDecisionDisposition.MATCHED_SYNTHETIC_CONTRACT,
        reason=AdminDecisionReason.EXACT_SYNTHETIC_MATCH,
        matched_grant_id=matches[0].grant_id,
        evaluated_at=safe_evaluated_at,
    )


__all__ = ["evaluate_synthetic_admin_preflight"]
