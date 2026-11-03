from __future__ import annotations

import json
import subprocess
import sys

import pytest

from app.config import Environment
from app.modules.admin_governance import (
    AdminDecisionDisposition,
    AdminDecisionReason,
    SyntheticIndependenceDisposition,
    SyntheticIndependenceReason,
)
from app.modules.admin_governance.demo import (
    AdminGovernanceDemoCode,
    AdminGovernanceDemoError,
    build_synthetic_admin_governance_demo,
)


def test_demo_builds_deterministic_independent_governance_evidence() -> None:
    first = build_synthetic_admin_governance_demo(environment=Environment.TEST)
    second = build_synthetic_admin_governance_demo(environment=Environment.TEST)

    assert first == second
    assert first.authorization.disposition is AdminDecisionDisposition.MATCHED_SYNTHETIC_CONTRACT
    assert first.authorization.reason is AdminDecisionReason.EXACT_SYNTHETIC_MATCH
    assert len(first.review_queue.items) == 1
    assert (
        first.maker_checker.disposition is SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED
    )
    assert first.maker_checker.reason is SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION
    assert first.audit_snapshot.receipts == (first.maker_checker,)


def test_demo_preserves_mfa_abstention_without_grant_authority() -> None:
    result = build_synthetic_admin_governance_demo(
        environment=Environment.LOCAL,
        mfa_verified=False,
    )

    assert result.authorization.disposition is AdminDecisionDisposition.ABSTAINED
    assert result.authorization.reason is AdminDecisionReason.MFA_NOT_VERIFIED
    assert result.authorization.matched_grant_id is None


def test_demo_preserves_self_review_abstention_without_approval_authority() -> None:
    result = build_synthetic_admin_governance_demo(
        environment=Environment.TEST,
        self_review=True,
    )

    assert result.maker_checker.disposition is SyntheticIndependenceDisposition.ABSTAINED
    assert result.maker_checker.reason is SyntheticIndependenceReason.SELF_REVIEW
    assert result.audit_snapshot.receipts == (result.maker_checker,)


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_demo_rejects_protected_environment_before_option_validation(
    environment: Environment,
) -> None:
    with pytest.raises(AdminGovernanceDemoError) as captured:
        build_synthetic_admin_governance_demo(
            environment=environment,
            mfa_verified=object(),  # type: ignore[arg-type]
            self_review=object(),  # type: ignore[arg-type]
        )

    assert captured.value.code is AdminGovernanceDemoCode.PROTECTED_ENVIRONMENT


def test_demo_rejects_noncanonical_options() -> None:
    with pytest.raises(AdminGovernanceDemoError) as environment_error:
        build_synthetic_admin_governance_demo(environment="test")  # type: ignore[arg-type]
    assert environment_error.value.code is AdminGovernanceDemoCode.INVALID_TYPE

    with pytest.raises(AdminGovernanceDemoError) as mfa_error:
        build_synthetic_admin_governance_demo(
            environment=Environment.TEST,
            mfa_verified=1,  # type: ignore[arg-type]
        )
    assert mfa_error.value.code is AdminGovernanceDemoCode.INVALID_TYPE


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.modules.admin_governance.demo", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_emits_canonical_content_free_governance_summary() -> None:
    first = _run_cli("--environment", "test")
    second = _run_cli("--environment", "test")

    assert first.returncode == 0
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["authority"] == "ENGINEERING_ONLY"
    assert payload["classification"] == "ENGINEERING_SYNTHETIC"
    assert payload["verification"] == "UNVERIFIED"
    assert payload["environment"] == "test"
    assert payload["authorization_disposition"] == "MATCHED_SYNTHETIC_CONTRACT"
    assert payload["authorization_reason"] == "EXACT_SYNTHETIC_MATCH"
    assert payload["review_queue_count"] == 1
    assert payload["independence_disposition"] == "INDEPENDENCE_CONFIRMED"
    assert payload["independence_reason"] == "DISTINCT_ACTOR_EXACT_REVISION"
    assert payload["audit_receipt_count"] == 1
    assert len(payload["request_fingerprint"]) == 64
    assert len(payload["queue_fingerprint"]) == 64
    assert len(payload["proposal_fingerprint"]) == 64
    assert len(payload["audit_fingerprint"]) == 64
    assert "patient" not in first.stdout.lower()
    assert "clinical" not in first.stdout.lower()
    assert "approved" not in first.stdout.lower()


def test_cli_exposes_mfa_and_self_review_abstentions() -> None:
    completed = _run_cli(
        "--environment",
        "local",
        "--mfa-unverified",
        "--self-review",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["authorization_disposition"] == "ABSTAINED"
    assert payload["authorization_reason"] == "MFA_NOT_VERIFIED"
    assert payload["matched_grant"] is False
    assert payload["independence_disposition"] == "ABSTAINED"
    assert payload["independence_reason"] == "SELF_REVIEW"


def test_cli_rejects_protected_environment_without_output() -> None:
    completed = _run_cli("--environment", "production")

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "PROTECTED_ENVIRONMENT" in completed.stderr
