from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.admin_governance import (
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


def grant(**changes: object) -> SyntheticAdminGrant:
    values: dict[str, object] = {
        "grant_id": "syn_admin_grant_alpha",
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


def test_request_is_immutable_canonical_and_fingerprinted() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = request(created_at=NOW.astimezone(offset))

    assert value.created_at == NOW
    assert value.created_at.tzinfo is UTC
    assert len(value.fingerprint) == 64
    assert value.authority is AdminAuthority.ENGINEERING_ONLY
    assert value.classification is AdminClassification.ENGINEERING_SYNTHETIC
    assert value.verification is AdminVerification.UNVERIFIED
    with pytest.raises(FrozenInstanceError):
        value.actor_id = "syn_admin_actor_beta"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("request_id", "request_alpha"),
        ("actor_id", "patient-123"),
        ("object_id", "syn_admin_object_epsilon"),
        ("object_version", "live.v1"),
        ("object_hash", "not-a-hash"),
        ("institution_id", "hospital-1"),
        ("source_id", "registry-1"),
        ("purpose_id", "treatment"),
        ("mfa_verified", 1),
        ("created_at", datetime(2026, 11, 1, 12, 0)),
    ],
)
def test_request_rejects_non_synthetic_or_invalid_values(field: str, invalid: object) -> None:
    with pytest.raises(AdminContractError):
        request(**{field: invalid})


def test_request_fingerprint_changes_for_each_scope_dimension() -> None:
    original = request()
    variants = (
        request(actor_id="syn_admin_actor_beta"),
        request(action=SyntheticAdminAction.SYNTHETIC_ACTION_BETA),
        request(object_id="syn_admin_object_beta"),
        request(object_version="engineering.v2"),
        request(object_hash="b" * 64),
        request(institution_id="syn_admin_institution_beta"),
        request(source_id="syn_admin_source_beta"),
        request(purpose_id="syn_admin_purpose_beta"),
        request(mfa_verified=False),
    )

    assert len({original.fingerprint, *(item.fingerprint for item in variants)}) == 10


def test_grant_normalizes_aware_clocks_and_rejects_invalid_chronology() -> None:
    offset = timezone(timedelta(hours=-4))
    value = grant(
        valid_from=(NOW - timedelta(minutes=5)).astimezone(offset),
        expires_at=(NOW + timedelta(minutes=5)).astimezone(offset),
    )

    assert value.valid_from.tzinfo is UTC
    assert value.expires_at.tzinfo is UTC
    with pytest.raises(AdminContractError) as captured:
        grant(valid_from=NOW, expires_at=NOW)
    assert captured.value.code is AdminContractCode.INVALID_CHRONOLOGY


def test_snapshots_reconstruct_and_detect_forced_mutation() -> None:
    safe_request = request()
    safe_grant = grant()
    assert snapshot_admin_request(safe_request) == safe_request
    assert snapshot_admin_grant(safe_grant) == safe_grant

    object.__setattr__(safe_request, "actor_id", "patient-123")
    object.__setattr__(safe_grant, "purpose_id", "treatment")
    with pytest.raises(AdminContractError):
        snapshot_admin_request(safe_request)
    with pytest.raises(AdminContractError):
        snapshot_admin_grant(safe_grant)


def test_decision_requires_a_consistent_content_free_shape() -> None:
    matched = SyntheticAdminDecision(
        request_id="syn_admin_request_alpha",
        request_fingerprint="c" * 64,
        disposition=AdminDecisionDisposition.MATCHED_SYNTHETIC_CONTRACT,
        reason=AdminDecisionReason.EXACT_SYNTHETIC_MATCH,
        matched_grant_id="syn_admin_grant_alpha",
        evaluated_at=NOW,
    )
    abstained = replace(
        matched,
        disposition=AdminDecisionDisposition.ABSTAINED,
        reason=AdminDecisionReason.NO_EXACT_ACTIVE_GRANT,
        matched_grant_id=None,
    )

    assert matched.contract_version == SYNTHETIC_ADMIN_CONTRACT_VERSION
    assert abstained.matched_grant_id is None
    with pytest.raises(AdminContractError) as captured:
        replace(matched, matched_grant_id=None)
    assert captured.value.code is AdminContractCode.INCONSISTENT_DECISION


@pytest.mark.parametrize("invalid", ["synthetic-admin-authorization.v2", 1])
def test_decision_rejects_noncanonical_contract_versions(invalid: object) -> None:
    with pytest.raises(AdminContractError) as captured:
        SyntheticAdminDecision(
            request_id="syn_admin_request_alpha",
            request_fingerprint="c" * 64,
            disposition=AdminDecisionDisposition.ABSTAINED,
            reason=AdminDecisionReason.NO_EXACT_ACTIVE_GRANT,
            matched_grant_id=None,
            evaluated_at=NOW,
            contract_version=invalid,  # type: ignore[arg-type]
        )
    assert captured.value.code is AdminContractCode.INVALID_VALUE
