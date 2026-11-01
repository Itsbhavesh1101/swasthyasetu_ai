"""Pure mechanics for detached engineering-synthetic governance evidence."""

from __future__ import annotations

from datetime import UTC, datetime

from app.config import Environment
from app.modules.admin_governance.governance_evidence_contracts import (
    MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS,
    GovernanceEvidenceContractCode,
    GovernanceEvidenceContractError,
    SyntheticCheckerSubmission,
    SyntheticGovernanceAuditSnapshot,
    SyntheticGovernanceProposal,
    SyntheticIndependenceDisposition,
    SyntheticIndependenceReason,
    SyntheticMakerCheckerReceipt,
    snapshot_checker_submission,
    snapshot_governance_proposal,
    snapshot_maker_checker_receipt,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


def _error(code: GovernanceEvidenceContractCode) -> GovernanceEvidenceContractError:
    return GovernanceEvidenceContractError(code)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _scope_matches(
    proposal: SyntheticGovernanceProposal,
    submission: SyntheticCheckerSubmission,
) -> bool:
    return (
        submission.proposal_id == proposal.proposal_id
        and submission.proposal_fingerprint == proposal.fingerprint
        and submission.object_id == proposal.object_id
        and submission.object_version == proposal.object_version
        and submission.object_hash == proposal.object_hash
        and submission.institution_id == proposal.institution_id
        and submission.source_id == proposal.source_id
        and submission.purpose_id == proposal.purpose_id
    )


def evaluate_synthetic_maker_checker(
    proposal: SyntheticGovernanceProposal,
    submission: SyntheticCheckerSubmission,
    *,
    evaluated_at: datetime,
    environment: Environment,
) -> SyntheticMakerCheckerReceipt:
    """Evaluate metadata independence only; never approve or execute a change."""

    if type(environment) is not Environment:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(GovernanceEvidenceContractCode.PROTECTED_ENVIRONMENT)

    safe_proposal = snapshot_governance_proposal(proposal)
    safe_submission = snapshot_checker_submission(submission)
    safe_evaluated_at = _utc(evaluated_at)
    if safe_submission.submitted_at < safe_proposal.created_at:
        raise _error(GovernanceEvidenceContractCode.INVALID_CHRONOLOGY)
    if safe_evaluated_at < safe_submission.submitted_at:
        raise _error(GovernanceEvidenceContractCode.INVALID_CHRONOLOGY)

    if safe_submission.checker_actor_id == safe_proposal.maker_actor_id:
        disposition = SyntheticIndependenceDisposition.ABSTAINED
        reason = SyntheticIndependenceReason.SELF_REVIEW
    elif not _scope_matches(safe_proposal, safe_submission):
        disposition = SyntheticIndependenceDisposition.ABSTAINED
        reason = SyntheticIndependenceReason.SCOPE_MISMATCH
    else:
        disposition = SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED
        reason = SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION

    return SyntheticMakerCheckerReceipt(
        proposal=safe_proposal,
        submission=safe_submission,
        disposition=disposition,
        reason=reason,
        evaluated_at=safe_evaluated_at,
    )


def build_synthetic_governance_audit_snapshot(
    receipts: tuple[SyntheticMakerCheckerReceipt, ...],
    *,
    snapshot_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticGovernanceAuditSnapshot:
    """Build a content-free evidence snapshot; never expose a live audit view."""

    if type(environment) is not Environment:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(GovernanceEvidenceContractCode.PROTECTED_ENVIRONMENT)
    if type(receipts) is not tuple:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    if len(receipts) > MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS:
        raise _error(GovernanceEvidenceContractCode.LIMIT_EXCEEDED)
    safe_receipts = tuple(
        sorted(
            (snapshot_maker_checker_receipt(item) for item in receipts),
            key=lambda item: item.check_id,
        )
    )
    return SyntheticGovernanceAuditSnapshot(
        snapshot_id=snapshot_id,
        generated_at=generated_at,
        receipts=safe_receipts,
    )


__all__ = [
    "build_synthetic_governance_audit_snapshot",
    "evaluate_synthetic_maker_checker",
]
