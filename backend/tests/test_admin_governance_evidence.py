from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.config import Environment
from app.modules.admin_governance import (
    MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS,
    GovernanceEvidenceContractCode,
    GovernanceEvidenceContractError,
    SyntheticCheckerSubmission,
    SyntheticGovernanceAuditSnapshot,
    SyntheticGovernanceChangeKind,
    SyntheticGovernanceProposal,
    SyntheticIndependenceDisposition,
    SyntheticIndependenceReason,
    SyntheticMakerCheckerReceipt,
    build_synthetic_governance_audit_snapshot,
    evaluate_synthetic_maker_checker,
)

NOW = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)


def proposal(suffix: str = "alpha", **changes: object) -> SyntheticGovernanceProposal:
    values: dict[str, object] = {
        "proposal_id": f"syn_governance_proposal_{suffix}",
        "maker_actor_id": f"syn_governance_actor_{suffix}",
        "object_id": f"syn_governance_object_{suffix}",
        "object_version": "engineering.v1",
        "object_hash": suffix[0] * 64,
        "institution_id": f"syn_governance_institution_{suffix}",
        "source_id": f"syn_governance_source_{suffix}",
        "purpose_id": f"syn_governance_purpose_{suffix}",
        "change_kind": SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_ALPHA,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticGovernanceProposal(**values)  # type: ignore[arg-type]


def submission(
    value: SyntheticGovernanceProposal,
    *,
    suffix: str = "alpha",
    **changes: object,
) -> SyntheticCheckerSubmission:
    values: dict[str, object] = {
        "check_id": f"syn_governance_check_{suffix}",
        "checker_actor_id": "syn_governance_actor_beta",
        "proposal_id": value.proposal_id,
        "proposal_fingerprint": value.fingerprint,
        "object_id": value.object_id,
        "object_version": value.object_version,
        "object_hash": value.object_hash,
        "institution_id": value.institution_id,
        "source_id": value.source_id,
        "purpose_id": value.purpose_id,
        "submitted_at": NOW + timedelta(minutes=1),
    }
    values.update(changes)
    return SyntheticCheckerSubmission(**values)  # type: ignore[arg-type]


def evaluate(
    value: SyntheticGovernanceProposal,
    check: SyntheticCheckerSubmission,
    *,
    evaluated_at: datetime = NOW + timedelta(minutes=2),
    environment: Environment = Environment.TEST,
) -> SyntheticMakerCheckerReceipt:
    return evaluate_synthetic_maker_checker(
        value,
        check,
        evaluated_at=evaluated_at,
        environment=environment,
    )


def build(
    receipts: tuple[SyntheticMakerCheckerReceipt, ...],
    *,
    generated_at: datetime = NOW + timedelta(minutes=3),
    environment: Environment = Environment.TEST,
) -> SyntheticGovernanceAuditSnapshot:
    return build_synthetic_governance_audit_snapshot(
        receipts,
        snapshot_id="syn_governance_audit_alpha",
        generated_at=generated_at,
        environment=environment,
    )


def test_exact_distinct_actor_metadata_confirms_only_independence() -> None:
    value = proposal()
    check = submission(value)
    offset = timezone(timedelta(hours=5, minutes=30))

    result = evaluate(value, check, evaluated_at=(NOW + timedelta(minutes=2)).astimezone(offset))

    assert result.disposition is SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED
    assert result.reason is SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION
    assert result.proposal_fingerprint == value.fingerprint
    assert result.submission_fingerprint == check.fingerprint
    assert result.evaluated_at.tzinfo is UTC


def test_self_review_abstains_even_when_all_metadata_matches() -> None:
    value = proposal()
    check = submission(value, checker_actor_id=value.maker_actor_id)

    result = evaluate(value, check)

    assert result.disposition is SyntheticIndependenceDisposition.ABSTAINED
    assert result.reason is SyntheticIndependenceReason.SELF_REVIEW


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("proposal_id", "syn_governance_proposal_beta"),
        ("proposal_fingerprint", "b" * 64),
        ("object_id", "syn_governance_object_beta"),
        ("object_version", "engineering.v2"),
        ("object_hash", "b" * 64),
        ("institution_id", "syn_governance_institution_beta"),
        ("source_id", "syn_governance_source_beta"),
        ("purpose_id", "syn_governance_purpose_beta"),
    ],
)
def test_any_exact_revision_or_scope_drift_abstains(field: str, value: object) -> None:
    proposal_value = proposal()
    result = evaluate(
        proposal_value,
        cast(Any, submission)(proposal_value, **{field: value}),
    )

    assert result.disposition is SyntheticIndependenceDisposition.ABSTAINED
    assert result.reason is SyntheticIndependenceReason.SCOPE_MISMATCH


def test_evaluator_rejects_naive_or_reversed_chronology() -> None:
    value = proposal()
    with pytest.raises(GovernanceEvidenceContractError) as submission_before_proposal:
        evaluate(
            value,
            submission(value, submitted_at=NOW - timedelta(microseconds=1)),
        )
    with pytest.raises(GovernanceEvidenceContractError) as evaluation_before_submission:
        evaluate(value, submission(value), evaluated_at=NOW)
    with pytest.raises(GovernanceEvidenceContractError) as naive:
        evaluate(value, submission(value), evaluated_at=NOW.replace(tzinfo=None))

    assert (
        submission_before_proposal.value.code is GovernanceEvidenceContractCode.INVALID_CHRONOLOGY
    )
    assert (
        evaluation_before_submission.value.code is GovernanceEvidenceContractCode.INVALID_CHRONOLOGY
    )
    assert naive.value.code is GovernanceEvidenceContractCode.INVALID_TYPE


def test_evaluator_revalidates_forced_mutation() -> None:
    value = proposal()
    check = submission(value)
    object.__setattr__(check, "object_id", "patient-123")

    with pytest.raises(GovernanceEvidenceContractError) as captured:
        evaluate(value, check)

    assert captured.value.code is GovernanceEvidenceContractCode.INVALID_VALUE


def test_audit_builder_orders_reconstructed_receipts_deterministically() -> None:
    alpha_proposal = proposal()
    alpha = evaluate(alpha_proposal, submission(alpha_proposal))
    beta_proposal = proposal("beta", created_at=NOW + timedelta(seconds=1))
    beta = evaluate(
        beta_proposal,
        submission(
            beta_proposal,
            suffix="beta",
            checker_actor_id="syn_governance_actor_gamma",
            submitted_at=NOW + timedelta(minutes=1, seconds=1),
        ),
        evaluated_at=NOW + timedelta(minutes=2, seconds=1),
    )

    assert build((beta, alpha)) == build((alpha, beta))
    assert tuple(item.check_id for item in build((beta, alpha)).receipts) == (
        "syn_governance_check_alpha",
        "syn_governance_check_beta",
    )


def test_audit_builder_rejects_duplicates_aliases_and_capacity_first() -> None:
    value = proposal()
    result = evaluate(value, submission(value))
    with pytest.raises(GovernanceEvidenceContractError) as duplicate:
        build((result, result))
    alias = SyntheticMakerCheckerReceipt(
        check_id="syn_governance_check_beta",
        proposal_id=result.proposal_id,
        proposal_fingerprint=result.proposal_fingerprint,
        submission_fingerprint="b" * 64,
        maker_actor_id=result.maker_actor_id,
        checker_actor_id="syn_governance_actor_gamma",
        disposition=SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED,
        reason=SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION,
        evaluated_at=result.evaluated_at,
    )
    with pytest.raises(GovernanceEvidenceContractError) as ambiguous:
        build((result, alias))

    hostile = tuple(object() for _ in range(MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS + 1))
    with pytest.raises(GovernanceEvidenceContractError) as capacity:
        build_synthetic_governance_audit_snapshot(
            cast(tuple[SyntheticMakerCheckerReceipt, ...], hostile),
            snapshot_id="syn_governance_audit_alpha",
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert duplicate.value.code is GovernanceEvidenceContractCode.DUPLICATE_RECEIPT
    assert ambiguous.value.code is GovernanceEvidenceContractCode.AMBIGUOUS_RECEIPT
    assert capacity.value.code is GovernanceEvidenceContractCode.LIMIT_EXCEEDED


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_any_input_is_inspected(
    environment: Environment,
) -> None:
    with pytest.raises(GovernanceEvidenceContractError) as evaluator:
        evaluate_synthetic_maker_checker(
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            evaluated_at=object(),  # type: ignore[arg-type]
            environment=environment,
        )
    with pytest.raises(GovernanceEvidenceContractError) as builder:
        build_synthetic_governance_audit_snapshot(
            object(),  # type: ignore[arg-type]
            snapshot_id=object(),  # type: ignore[arg-type]
            generated_at=object(),  # type: ignore[arg-type]
            environment=environment,
        )

    assert evaluator.value.code is GovernanceEvidenceContractCode.PROTECTED_ENVIRONMENT
    assert builder.value.code is GovernanceEvidenceContractCode.PROTECTED_ENVIRONMENT
