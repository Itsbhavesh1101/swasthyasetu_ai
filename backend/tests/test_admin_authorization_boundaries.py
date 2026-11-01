from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.modules.admin_governance import (
    AdminContractCode,
    AdminContractError,
    AdminDecisionReason,
    SyntheticAdminAction,
    SyntheticAdminDecision,
    SyntheticAdminGrant,
    SyntheticAdminRequest,
    evaluate_synthetic_admin_preflight,
)

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
HASH_A = "a" * 64


def request(**changes: object) -> SyntheticAdminRequest:
    values: dict[str, object] = {
        "request_id": "syn_admin_request_alpha",
        "actor_id": "syn_admin_actor_alpha",
        "action": SyntheticAdminAction.SYNTHETIC_ACTION_ALPHA,
        "object_id": "syn_admin_object_alpha",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "institution_id": "syn_admin_institution_alpha",
        "source_id": "syn_admin_source_alpha",
        "purpose_id": "syn_admin_purpose_alpha",
        "mfa_verified": True,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticAdminRequest(**values)  # type: ignore[arg-type]


def grant(suffix: str, **changes: object) -> SyntheticAdminGrant:
    values: dict[str, object] = {
        "grant_id": f"syn_admin_grant_{suffix}",
        "actor_id": "syn_admin_actor_alpha",
        "action": SyntheticAdminAction.SYNTHETIC_ACTION_ALPHA,
        "object_id": "syn_admin_object_alpha",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "institution_id": "syn_admin_institution_alpha",
        "source_id": "syn_admin_source_alpha",
        "purpose_id": "syn_admin_purpose_alpha",
        "valid_from": NOW - timedelta(minutes=5),
        "expires_at": NOW + timedelta(minutes=5),
    }
    values.update(changes)
    return SyntheticAdminGrant(**values)  # type: ignore[arg-type]


def evaluate(
    value: SyntheticAdminRequest, grants: tuple[SyntheticAdminGrant, ...]
) -> SyntheticAdminDecision:
    return evaluate_synthetic_admin_preflight(
        value,
        grants,
        evaluated_at=NOW,
        environment=Environment.TEST,
    )


def test_overlapping_semantic_grant_aliases_are_rejected_even_at_a_time_boundary() -> None:
    expired_at_boundary = grant(
        "alpha",
        valid_from=NOW - timedelta(minutes=10),
        expires_at=NOW,
    )
    active = grant(
        "beta",
        valid_from=NOW - timedelta(minutes=5),
        expires_at=NOW + timedelta(minutes=5),
    )

    with pytest.raises(AdminContractError) as captured:
        evaluate(request(), (expired_at_boundary, active))

    assert captured.value.code is AdminContractCode.AMBIGUOUS_GRANT


def test_forced_grant_mutation_is_revalidated_at_the_boundary() -> None:
    value = grant("alpha")
    object.__setattr__(value, "object_id", "patient-123")

    with pytest.raises(AdminContractError) as captured:
        evaluate(request(), (value,))

    assert captured.value.code is AdminContractCode.INVALID_VALUE


def test_scope_mismatches_have_one_nonenumerating_abstention_surface() -> None:
    actor_mismatch = evaluate(request(), (grant("alpha", actor_id="syn_admin_actor_beta"),))
    source_mismatch = evaluate(request(), (grant("alpha", source_id="syn_admin_source_beta"),))

    assert actor_mismatch.reason is AdminDecisionReason.NO_EXACT_ACTIVE_GRANT
    assert source_mismatch.reason is AdminDecisionReason.NO_EXACT_ACTIVE_GRANT
    assert actor_mismatch.matched_grant_id is source_mismatch.matched_grant_id is None


def test_foundation_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "admin_governance" not in module_ids
    assert "admin" not in module_ids
    assert all("admin" not in path and "governance" not in path for path in route_paths)


def test_decision_has_no_runtime_authorization_or_execution_surface() -> None:
    decision = evaluate(request(), (grant("alpha"),))

    for prohibited in (
        "activate",
        "approve",
        "authorize",
        "execute",
        "persist",
        "publish",
        "register",
        "revoke",
        "write",
    ):
        assert not hasattr(decision, prohibited)

    assert not hasattr(decision, "actor_id")
    assert not hasattr(decision, "object_id")
    assert not hasattr(decision, "institution_id")
