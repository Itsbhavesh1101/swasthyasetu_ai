from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.modules.admin_governance import (
    GovernanceEvidenceContractError,
    SyntheticCheckerSubmission,
    SyntheticGovernanceChangeKind,
    SyntheticGovernanceProposal,
    build_synthetic_governance_audit_snapshot,
    evaluate_synthetic_maker_checker,
)

NOW = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)


def proposal() -> SyntheticGovernanceProposal:
    return SyntheticGovernanceProposal(
        proposal_id="syn_governance_proposal_alpha",
        maker_actor_id="syn_governance_actor_alpha",
        object_id="syn_governance_object_alpha",
        object_version="engineering.v1",
        object_hash="a" * 64,
        institution_id="syn_governance_institution_alpha",
        source_id="syn_governance_source_alpha",
        purpose_id="syn_governance_purpose_alpha",
        change_kind=SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_ALPHA,
        created_at=NOW,
    )


def submission(value: SyntheticGovernanceProposal) -> SyntheticCheckerSubmission:
    return SyntheticCheckerSubmission(
        check_id="syn_governance_check_alpha",
        checker_actor_id="syn_governance_actor_beta",
        proposal_id=value.proposal_id,
        proposal_fingerprint=value.fingerprint,
        object_id=value.object_id,
        object_version=value.object_version,
        object_hash=value.object_hash,
        institution_id=value.institution_id,
        source_id=value.source_id,
        purpose_id=value.purpose_id,
        submitted_at=NOW + timedelta(minutes=1),
    )


def test_errors_do_not_echo_hostile_values() -> None:
    hostile = "patient@example.test/clinical-secret"

    with pytest.raises(GovernanceEvidenceContractError) as captured:
        SyntheticGovernanceProposal(
            proposal_id="syn_governance_proposal_alpha",
            maker_actor_id="syn_governance_actor_alpha",
            object_id=hostile,
            object_version="engineering.v1",
            object_hash="a" * 64,
            institution_id="syn_governance_institution_alpha",
            source_id="syn_governance_source_alpha",
            purpose_id="syn_governance_purpose_alpha",
            change_kind=SyntheticGovernanceChangeKind.SYNTHETIC_CHANGE_ALPHA,
            created_at=NOW,
        )

    assert hostile not in str(captured.value)


def test_receipts_and_snapshots_expose_no_governance_action_or_search_surface() -> None:
    value = proposal()
    receipt = evaluate_synthetic_maker_checker(
        value,
        submission(value),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )
    snapshot = build_synthetic_governance_audit_snapshot(
        (receipt,),
        snapshot_id="syn_governance_audit_alpha",
        generated_at=NOW + timedelta(minutes=3),
        environment=Environment.LOCAL,
    )

    for prohibited in (
        "approve",
        "activate",
        "authorize",
        "execute",
        "export",
        "persist",
        "publish",
        "raw_content",
        "reject",
        "rollback",
        "search",
    ):
        assert not hasattr(receipt, prohibited)
        assert not hasattr(snapshot, prohibited)


def test_governance_evidence_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "admin_governance" not in module_ids
    assert "audit" not in module_ids
    assert all("admin" not in path and "audit" not in path for path in route_paths)
