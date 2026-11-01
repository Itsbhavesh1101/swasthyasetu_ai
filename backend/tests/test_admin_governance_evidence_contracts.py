from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.admin_governance.governance_evidence_contracts import (
    SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION,
    GovernanceEvidenceContractCode,
    GovernanceEvidenceContractError,
    SyntheticCheckerSubmission,
    SyntheticGovernanceAuditSnapshot,
    SyntheticGovernanceChangeKind,
    SyntheticGovernanceProposal,
    SyntheticIndependenceDisposition,
    SyntheticIndependenceReason,
    SyntheticMakerCheckerReceipt,
    snapshot_checker_submission,
    snapshot_governance_audit,
    snapshot_governance_proposal,
    snapshot_maker_checker_receipt,
)

NOW = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)
HASH_A = "a" * 64


def proposal(suffix: str = "alpha", **changes: object) -> SyntheticGovernanceProposal:
    values: dict[str, object] = {
        "proposal_id": f"syn_governance_proposal_{suffix}",
        "maker_actor_id": f"syn_governance_actor_{suffix}",
        "object_id": f"syn_governance_object_{suffix}",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "institution_id": f"syn_governance_institution_{suffix}",
        "source_id": f"syn_governance_source_{suffix}",
        "purpose_id": f"syn_governance_purpose_{suffix}",
        "change_kind": SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_ALPHA,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticGovernanceProposal(**values)  # type: ignore[arg-type]


def submission(
    value: SyntheticGovernanceProposal | None = None,
    *,
    suffix: str = "alpha",
    **changes: object,
) -> SyntheticCheckerSubmission:
    bound = value or proposal()
    values: dict[str, object] = {
        "check_id": f"syn_governance_check_{suffix}",
        "checker_actor_id": "syn_governance_actor_beta",
        "proposal_id": bound.proposal_id,
        "proposal_fingerprint": bound.fingerprint,
        "object_id": bound.object_id,
        "object_version": bound.object_version,
        "object_hash": bound.object_hash,
        "institution_id": bound.institution_id,
        "source_id": bound.source_id,
        "purpose_id": bound.purpose_id,
        "submitted_at": NOW + timedelta(minutes=1),
    }
    values.update(changes)
    return SyntheticCheckerSubmission(**values)  # type: ignore[arg-type]


def receipt(
    value: SyntheticGovernanceProposal | None = None,
    check: SyntheticCheckerSubmission | None = None,
    **changes: object,
) -> SyntheticMakerCheckerReceipt:
    bound = value or proposal()
    bound_check = check or submission(bound)
    values: dict[str, object] = {
        "check_id": bound_check.check_id,
        "proposal_id": bound.proposal_id,
        "proposal_fingerprint": bound.fingerprint,
        "submission_fingerprint": bound_check.fingerprint,
        "maker_actor_id": bound.maker_actor_id,
        "checker_actor_id": bound_check.checker_actor_id,
        "disposition": SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED,
        "reason": SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION,
        "evaluated_at": NOW + timedelta(minutes=2),
    }
    values.update(changes)
    return SyntheticMakerCheckerReceipt(**values)  # type: ignore[arg-type]


def audit(
    *receipts: SyntheticMakerCheckerReceipt, **changes: object
) -> SyntheticGovernanceAuditSnapshot:
    values: dict[str, object] = {
        "snapshot_id": "syn_governance_audit_alpha",
        "generated_at": NOW + timedelta(minutes=3),
        "receipts": receipts,
    }
    values.update(changes)
    return SyntheticGovernanceAuditSnapshot(**values)  # type: ignore[arg-type]


def test_proposal_is_immutable_utc_normalized_and_fingerprinted() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = proposal(created_at=NOW.astimezone(offset))

    assert value.created_at == NOW
    assert value.created_at.tzinfo is UTC
    assert len(value.fingerprint) == 64
    with pytest.raises(FrozenInstanceError):
        value.object_id = "syn_governance_object_beta"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("proposal_id", "proposal-alpha"),
        ("maker_actor_id", "actor-real"),
        ("object_id", "patient-123"),
        ("object_version", "production.v1"),
        ("object_hash", "not-a-hash"),
        ("institution_id", "hospital-1"),
        ("source_id", "source-1"),
        ("purpose_id", "purpose-1"),
        ("change_kind", "SYNTHETIC_CHANGE_ALPHA"),
        ("created_at", datetime(2026, 11, 1, 15, 0)),
    ],
)
def test_proposal_rejects_non_synthetic_or_non_strict_values(field: str, invalid: object) -> None:
    with pytest.raises(GovernanceEvidenceContractError):
        cast(Any, proposal)(**{field: invalid})


def test_proposal_fingerprint_binds_every_governance_field() -> None:
    original = proposal()
    variants = (
        proposal("beta", object_id="syn_governance_object_alpha"),
        proposal(object_version="engineering.v2"),
        proposal(object_hash="b" * 64),
        proposal(institution_id="syn_governance_institution_beta"),
        proposal(source_id="syn_governance_source_beta"),
        proposal(purpose_id="syn_governance_purpose_beta"),
        proposal(change_kind=SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_BETA),
        proposal(created_at=NOW + timedelta(seconds=1)),
    )

    assert len({original.fingerprint, *(value.fingerprint for value in variants)}) == 9


def test_submission_is_strict_immutable_and_fingerprinted() -> None:
    bound = proposal()
    value = submission(bound)

    assert value.proposal_fingerprint == bound.fingerprint
    assert len(value.fingerprint) == 64
    with pytest.raises(FrozenInstanceError):
        value.checker_actor_id = bound.maker_actor_id  # type: ignore[misc]
    with pytest.raises(GovernanceEvidenceContractError):
        submission(bound, checker_actor_id="reviewer@example.test")
    with pytest.raises(GovernanceEvidenceContractError):
        submission(bound, proposal_fingerprint="A" * 64)


def test_receipt_constructor_enforces_closed_consistency() -> None:
    bound = proposal()
    check = submission(bound)

    with pytest.raises(GovernanceEvidenceContractError) as same_actor_confirmed:
        receipt(bound, check, checker_actor_id=bound.maker_actor_id)
    with pytest.raises(GovernanceEvidenceContractError) as wrong_reason:
        receipt(bound, check, reason=SyntheticIndependenceReason.SELF_REVIEW)
    abstained = receipt(
        bound,
        check,
        checker_actor_id=bound.maker_actor_id,
        disposition=SyntheticIndependenceDisposition.ABSTAINED,
        reason=SyntheticIndependenceReason.SELF_REVIEW,
    )

    assert same_actor_confirmed.value.code is GovernanceEvidenceContractCode.INCONSISTENT_RECEIPT
    assert wrong_reason.value.code is GovernanceEvidenceContractCode.INCONSISTENT_RECEIPT
    assert abstained.disposition is SyntheticIndependenceDisposition.ABSTAINED


def test_snapshot_helpers_reconstruct_and_detect_forced_mutation() -> None:
    bound = proposal()
    check = submission(bound)
    result = receipt(bound, check)
    view = audit(result)

    assert snapshot_governance_proposal(bound) == bound
    assert snapshot_checker_submission(check) == check
    assert snapshot_maker_checker_receipt(result) == result
    assert snapshot_governance_audit(view) == view

    object.__setattr__(bound, "object_id", "patient-123")
    object.__setattr__(check, "object_id", "patient-123")
    object.__setattr__(result, "proposal_fingerprint", "b" * 64)
    object.__setattr__(view.receipts[0], "proposal_fingerprint", "b" * 64)

    for value, snapshotter in (
        (bound, snapshot_governance_proposal),
        (check, snapshot_checker_submission),
        (result, snapshot_maker_checker_receipt),
        (view, snapshot_governance_audit),
    ):
        with pytest.raises(GovernanceEvidenceContractError):
            snapshotter(value)


def test_audit_snapshot_requires_canonical_unique_receipts_and_chronology() -> None:
    alpha_proposal = proposal()
    alpha = receipt(alpha_proposal, submission(alpha_proposal))
    beta_proposal = proposal(
        "beta",
        object_hash="b" * 64,
        created_at=NOW + timedelta(seconds=1),
    )
    beta = receipt(
        beta_proposal,
        submission(
            beta_proposal,
            suffix="beta",
            checker_actor_id="syn_governance_actor_gamma",
            submitted_at=NOW + timedelta(minutes=1, seconds=1),
        ),
        evaluated_at=NOW + timedelta(minutes=2, seconds=1),
    )

    value = audit(alpha, beta)
    assert value.contract_version == SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION
    assert len(value.fingerprint) == 64
    with pytest.raises(GovernanceEvidenceContractError) as unordered:
        audit(beta, alpha)
    with pytest.raises(GovernanceEvidenceContractError) as duplicate:
        audit(alpha, alpha)
    with pytest.raises(GovernanceEvidenceContractError) as alias:
        audit(alpha, replace(alpha, check_id="syn_governance_check_beta"))
    with pytest.raises(GovernanceEvidenceContractError) as early:
        audit(alpha, generated_at=alpha.evaluated_at - timedelta(microseconds=1))

    assert unordered.value.code is GovernanceEvidenceContractCode.INVALID_VALUE
    assert duplicate.value.code is GovernanceEvidenceContractCode.DUPLICATE_RECEIPT
    assert alias.value.code is GovernanceEvidenceContractCode.AMBIGUOUS_RECEIPT
    assert early.value.code is GovernanceEvidenceContractCode.INVALID_CHRONOLOGY


def test_contract_version_drift_and_hostile_values_fail_content_free() -> None:
    hostile = "patient@example.test/clinical-secret"
    with pytest.raises(GovernanceEvidenceContractError) as version:
        replace(audit(), contract_version="synthetic-governance-evidence.v2")
    with pytest.raises(GovernanceEvidenceContractError) as captured:
        proposal(object_id=hostile)

    assert version.value.code is GovernanceEvidenceContractCode.INVALID_VALUE
    assert hostile not in str(captured.value)
