"""Deterministic offline demonstration of detached synthetic admin governance."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from app.config import Environment
from app.modules.admin_governance.contracts import (
    SyntheticAdminAction,
    SyntheticAdminDecision,
    SyntheticAdminGrant,
    SyntheticAdminRequest,
)
from app.modules.admin_governance.governance_evidence import (
    build_synthetic_governance_audit_snapshot,
    evaluate_synthetic_maker_checker,
)
from app.modules.admin_governance.governance_evidence_contracts import (
    SyntheticCheckerSubmission,
    SyntheticGovernanceAuditSnapshot,
    SyntheticGovernanceChangeKind,
    SyntheticGovernanceProposal,
    SyntheticMakerCheckerReceipt,
)
from app.modules.admin_governance.preflight import evaluate_synthetic_admin_preflight
from app.modules.admin_governance.review_queue import build_synthetic_review_queue
from app.modules.admin_governance.review_queue_contracts import (
    SyntheticReviewItemKind,
    SyntheticReviewItemState,
    SyntheticReviewQueueItem,
    SyntheticReviewQueueSnapshot,
)

_NOW = datetime(2026, 11, 3, 7, 0, tzinfo=UTC)
_HASH = "a" * 64
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class AdminGovernanceDemoCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class AdminGovernanceDemoError(ValueError):
    """Stable failure from the offline demonstration boundary."""

    def __init__(self, code: AdminGovernanceDemoCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class SyntheticAdminGovernanceDemo:
    """Independent synthetic evidence; this is not an executable approval workflow."""

    request: SyntheticAdminRequest
    authorization: SyntheticAdminDecision
    review_queue: SyntheticReviewQueueSnapshot
    proposal: SyntheticGovernanceProposal
    maker_checker: SyntheticMakerCheckerReceipt
    audit_snapshot: SyntheticGovernanceAuditSnapshot


def build_synthetic_admin_governance_demo(
    *,
    environment: Environment,
    mfa_verified: bool = True,
    self_review: bool = False,
) -> SyntheticAdminGovernanceDemo:
    """Build parallel content-free P21 evidence without granting operational authority."""

    if type(environment) is not Environment:
        raise AdminGovernanceDemoError(AdminGovernanceDemoCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise AdminGovernanceDemoError(AdminGovernanceDemoCode.PROTECTED_ENVIRONMENT)
    if type(mfa_verified) is not bool or type(self_review) is not bool:
        raise AdminGovernanceDemoError(AdminGovernanceDemoCode.INVALID_TYPE)

    request = SyntheticAdminRequest(
        request_id="syn_admin_request_alpha",
        actor_id="syn_admin_actor_alpha",
        action=SyntheticAdminAction.SYNTHETIC_ACTION_ALPHA,
        object_id="syn_admin_object_alpha",
        object_version="engineering.v1",
        object_hash=_HASH,
        institution_id="syn_admin_institution_alpha",
        source_id="syn_admin_source_alpha",
        purpose_id="syn_admin_purpose_alpha",
        mfa_verified=mfa_verified,
        created_at=_NOW,
    )
    grant = SyntheticAdminGrant(
        grant_id="syn_admin_grant_alpha",
        actor_id=request.actor_id,
        action=request.action,
        object_id=request.object_id,
        object_version=request.object_version,
        object_hash=request.object_hash,
        institution_id=request.institution_id,
        source_id=request.source_id,
        purpose_id=request.purpose_id,
        valid_from=_NOW - timedelta(minutes=1),
        expires_at=_NOW + timedelta(minutes=5),
    )
    authorization = evaluate_synthetic_admin_preflight(
        request,
        (grant,),
        evaluated_at=_NOW,
        environment=environment,
    )

    queue_item = SyntheticReviewQueueItem(
        item_id="syn_review_item_alpha",
        object_id="syn_review_object_alpha",
        object_version="engineering.v1",
        object_hash=_HASH,
        item_kind=SyntheticReviewItemKind.SYNTHETIC_FACT_CANDIDATE,
        state=SyntheticReviewItemState.PENDING_ENGINEERING_REVIEW,
        created_at=_NOW,
    )
    review_queue = build_synthetic_review_queue(
        (queue_item,),
        snapshot_id="syn_review_snapshot_alpha",
        generated_at=_NOW + timedelta(minutes=1),
        environment=environment,
    )

    proposal = SyntheticGovernanceProposal(
        proposal_id="syn_governance_proposal_alpha",
        maker_actor_id="syn_governance_actor_alpha",
        object_id="syn_governance_object_alpha",
        object_version="engineering.v1",
        object_hash=_HASH,
        institution_id="syn_governance_institution_alpha",
        source_id="syn_governance_source_alpha",
        purpose_id="syn_governance_purpose_alpha",
        change_kind=SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_ALPHA,
        created_at=_NOW + timedelta(minutes=1),
    )
    submission = SyntheticCheckerSubmission(
        check_id="syn_governance_check_alpha",
        checker_actor_id=(proposal.maker_actor_id if self_review else "syn_governance_actor_beta"),
        proposal_id=proposal.proposal_id,
        proposal_fingerprint=proposal.fingerprint,
        object_id=proposal.object_id,
        object_version=proposal.object_version,
        object_hash=proposal.object_hash,
        institution_id=proposal.institution_id,
        source_id=proposal.source_id,
        purpose_id=proposal.purpose_id,
        submitted_at=_NOW + timedelta(minutes=2),
    )
    maker_checker = evaluate_synthetic_maker_checker(
        proposal,
        submission,
        evaluated_at=_NOW + timedelta(minutes=3),
        environment=environment,
    )
    audit_snapshot = build_synthetic_governance_audit_snapshot(
        (maker_checker,),
        snapshot_id="syn_governance_audit_alpha",
        generated_at=_NOW + timedelta(minutes=4),
        environment=environment,
    )
    return SyntheticAdminGovernanceDemo(
        request=request,
        authorization=authorization,
        review_queue=review_queue,
        proposal=proposal,
        maker_checker=maker_checker,
        audit_snapshot=audit_snapshot,
    )


def _summary(
    demo: SyntheticAdminGovernanceDemo,
    *,
    environment: Environment,
) -> dict[str, object]:
    return {
        "audit_fingerprint": demo.audit_snapshot.fingerprint,
        "audit_receipt_count": len(demo.audit_snapshot.receipts),
        "authority": demo.authorization.authority.value,
        "authorization_disposition": demo.authorization.disposition.value,
        "authorization_reason": demo.authorization.reason.value,
        "classification": demo.authorization.classification.value,
        "environment": environment.value,
        "independence_disposition": demo.maker_checker.disposition.value,
        "independence_reason": demo.maker_checker.reason.value,
        "matched_grant": demo.authorization.matched_grant_id is not None,
        "proposal_fingerprint": demo.proposal.fingerprint,
        "queue_fingerprint": demo.review_queue.fingerprint,
        "request_fingerprint": demo.request.fingerprint,
        "review_queue_count": len(demo.review_queue.items),
        "verification": demo.authorization.verification.value,
    }


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline engineering-synthetic admin-governance replay."
    )
    parser.add_argument(
        "--environment",
        choices=[environment.value for environment in Environment],
        default=Environment.LOCAL.value,
    )
    parser.add_argument("--mfa-unverified", action="store_true")
    parser.add_argument("--self-review", action="store_true")
    parsed = parser.parse_args(arguments)
    environment = Environment(parsed.environment)
    try:
        demo = build_synthetic_admin_governance_demo(
            environment=environment,
            mfa_verified=not parsed.mfa_unverified,
            self_review=parsed.self_review,
        )
    except AdminGovernanceDemoError as error:
        parser.exit(2, f"{error.code.value}\n")
    print(json.dumps(_summary(demo, environment=environment), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AdminGovernanceDemoCode",
    "AdminGovernanceDemoError",
    "SyntheticAdminGovernanceDemo",
    "build_synthetic_admin_governance_demo",
    "main",
]
