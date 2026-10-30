from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.referrals.domain import (
    ReferralApplicationDisposition,
    ReferralDomainCode,
    ReferralDomainError,
    ReferralTransitionCommand,
    ReferralTransitionPair,
    ReferralTransitionReceipt,
    SyntheticReferral,
    SyntheticReferralAuthority,
    SyntheticReferralClassification,
    SyntheticReferralStatus,
    SyntheticTransitionPolicy,
    apply_synthetic_transition,
)

NOW = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)
HASH = "c" * 64


def referral(
    *,
    version: int = 1,
    status: SyntheticReferralStatus = SyntheticReferralStatus.OFFERED,
    updated_at: datetime = NOW,
) -> SyntheticReferral:
    return SyntheticReferral(
        referral_id="syn_referral_alpha",
        version=version,
        status=status,
        created_at=NOW,
        updated_at=updated_at,
    )


def pair(
    from_status: SyntheticReferralStatus = SyntheticReferralStatus.OFFERED,
    to_status: SyntheticReferralStatus = SyntheticReferralStatus.CANCELLED,
) -> ReferralTransitionPair:
    return ReferralTransitionPair(from_status=from_status, to_status=to_status)


def policy(*pairs: ReferralTransitionPair) -> SyntheticTransitionPolicy:
    return SyntheticTransitionPolicy(
        policy_id="syn_referral_policy_fixture",
        policy_version="v1",
        artifact_hash=HASH,
        allowed_transitions=pairs or (pair(),),
        activated_at=NOW,
    )


def command(
    *,
    command_id: str = "syn_referral_command_alpha",
    idempotency_key: str = "syn_referral_idem_alpha",
    expected_version: int = 1,
    from_status: SyntheticReferralStatus = SyntheticReferralStatus.OFFERED,
    to_status: SyntheticReferralStatus = SyntheticReferralStatus.CANCELLED,
    occurred_at: datetime = NOW + timedelta(seconds=1),
) -> ReferralTransitionCommand:
    return ReferralTransitionCommand(
        command_id=command_id,
        referral_id="syn_referral_alpha",
        idempotency_key=idempotency_key,
        expected_version=expected_version,
        from_status=from_status,
        to_status=to_status,
        occurred_at=occurred_at,
    )


def test_canonical_status_vocabulary_is_closed_but_grants_no_transition_policy() -> None:
    assert {item.value for item in SyntheticReferralStatus} == {
        "OFFERED",
        "CONSENTED",
        "SENT",
        "ACKNOWLEDGED",
        "SCHEDULED",
        "COMPLETED",
        "DECLINED",
        "UNREACHABLE",
        "EXPIRED",
        "FAILED",
        "CANCELLED",
    }
    import app.modules.referrals.domain as domain

    assert not hasattr(domain, "DEFAULT_TRANSITION_POLICY")
    assert not hasattr(domain, "PRODUCTION_TRANSITION_POLICY")


def test_explicit_synthetic_policy_applies_one_transition_immutably() -> None:
    application = apply_synthetic_transition(referral(), command(), policy())

    assert application.disposition is ReferralApplicationDisposition.APPLIED
    assert application.referral.status is SyntheticReferralStatus.CANCELLED
    assert application.referral.version == 2
    assert application.referral.updated_at == NOW + timedelta(seconds=1)
    assert application.receipt.previous_version == 1
    assert application.receipt.result_version == 2
    assert application.receipt.policy_artifact_hash == HASH
    assert application.referral.authority is SyntheticReferralAuthority.ENGINEERING_ONLY
    assert (
        application.referral.classification is SyntheticReferralClassification.ENGINEERING_SYNTHETIC
    )
    with pytest.raises(FrozenInstanceError):
        application.referral.version = 3  # type: ignore[misc]


def test_transition_not_present_in_supplied_policy_fails_closed() -> None:
    with pytest.raises(ReferralDomainError) as raised:
        apply_synthetic_transition(
            referral(),
            command(to_status=SyntheticReferralStatus.DECLINED),
            policy(),
        )
    assert raised.value.code is ReferralDomainCode.TRANSITION_NOT_ALLOWED


def test_engine_does_not_invent_terminal_or_correction_semantics() -> None:
    current = referral(
        version=4,
        status=SyntheticReferralStatus.COMPLETED,
        updated_at=NOW + timedelta(seconds=3),
    )
    fixture_policy = policy(
        pair(SyntheticReferralStatus.COMPLETED, SyntheticReferralStatus.OFFERED)
    )
    fixture_command = command(
        expected_version=4,
        from_status=SyntheticReferralStatus.COMPLETED,
        to_status=SyntheticReferralStatus.OFFERED,
        occurred_at=NOW + timedelta(seconds=4),
    )

    result = apply_synthetic_transition(current, fixture_command, fixture_policy)

    assert result.referral.status is SyntheticReferralStatus.OFFERED
    assert result.referral.version == 5


def test_exact_duplicate_is_noop_after_the_recorded_result() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    replay = apply_synthetic_transition(
        first.referral,
        command(),
        policy(),
        prior_receipts=(first.receipt,),
    )

    assert replay.disposition is ReferralApplicationDisposition.IDEMPOTENT_REPLAY
    assert replay.referral == first.referral
    assert replay.receipt == first.receipt


def test_exact_duplicate_never_rolls_back_a_later_synthetic_state() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    later = replace(
        first.referral,
        version=3,
        status=SyntheticReferralStatus.FAILED,
        updated_at=NOW + timedelta(seconds=2),
    )

    replay = apply_synthetic_transition(
        later,
        command(),
        policy(),
        prior_receipts=(first.receipt,),
    )

    assert replay.disposition is ReferralApplicationDisposition.IDEMPOTENT_REPLAY
    assert replay.referral == later


def test_replay_rejects_missing_applied_state_and_idempotency_collision() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    with pytest.raises(ReferralDomainError) as stale:
        apply_synthetic_transition(referral(), command(), policy(), prior_receipts=(first.receipt,))
    assert stale.value.code is ReferralDomainCode.STALE_STATE

    with pytest.raises(ReferralDomainError) as collision:
        apply_synthetic_transition(
            first.referral,
            command(to_status=SyntheticReferralStatus.DECLINED),
            policy(pair(SyntheticReferralStatus.OFFERED, SyntheticReferralStatus.DECLINED)),
            prior_receipts=(first.receipt,),
        )
    assert collision.value.code is ReferralDomainCode.IDEMPOTENCY_CONFLICT


def test_duplicate_idempotency_keys_in_receipt_history_fail_closed() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    with pytest.raises(ReferralDomainError) as raised:
        apply_synthetic_transition(
            first.referral,
            command(
                command_id="syn_referral_command_beta", idempotency_key="syn_referral_idem_beta"
            ),
            policy(),
            prior_receipts=(first.receipt, first.receipt),
        )
    assert raised.value.code is ReferralDomainCode.DUPLICATE_IDENTITY


def test_duplicate_command_ids_and_cross_referral_receipts_fail_closed() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    duplicate_command = replace(
        first.receipt,
        idempotency_key="syn_referral_idem_beta",
        command_fingerprint="d" * 64,
    )
    with pytest.raises(ReferralDomainError) as duplicate:
        apply_synthetic_transition(
            first.referral,
            command(
                command_id="syn_referral_command_beta", idempotency_key="syn_referral_idem_beta"
            ),
            policy(),
            prior_receipts=(first.receipt, duplicate_command),
        )
    assert duplicate.value.code is ReferralDomainCode.DUPLICATE_IDENTITY

    cross_referral = replace(
        first.receipt,
        command_id="syn_referral_command_beta",
        referral_id="syn_referral_beta",
        idempotency_key="syn_referral_idem_beta",
        command_fingerprint="d" * 64,
    )
    with pytest.raises(ReferralDomainError) as mismatch:
        apply_synthetic_transition(
            first.referral,
            command(
                command_id="syn_referral_command_beta", idempotency_key="syn_referral_idem_beta"
            ),
            policy(),
            prior_receipts=(first.receipt, cross_referral),
        )
    assert mismatch.value.code is ReferralDomainCode.IDENTITY_MISMATCH


def test_replay_state_cannot_predate_or_disagree_with_receipt_result() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    for invalid in (
        replace(first.referral, updated_at=NOW),
        replace(first.referral, status=SyntheticReferralStatus.FAILED),
    ):
        with pytest.raises(ReferralDomainError):
            apply_synthetic_transition(
                invalid,
                command(),
                policy(),
                prior_receipts=(first.receipt,),
            )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("referral_id", "referral_alpha", ReferralDomainCode.INVALID_VALUE),
        ("version", 0, ReferralDomainCode.LIMIT_EXCEEDED),
        ("version", True, ReferralDomainCode.INVALID_TYPE),
        ("status", "OFFERED", ReferralDomainCode.INVALID_TYPE),
        ("created_at", datetime(2026, 10, 31, 12, 0), ReferralDomainCode.INVALID_TYPE),
        ("authority", "PRODUCTION", ReferralDomainCode.INVALID_TYPE),
        ("classification", "REAL_DATA", ReferralDomainCode.INVALID_TYPE),
    ],
)
def test_referral_rejects_invalid_direct_construction(
    field: str, value: object, code: ReferralDomainCode
) -> None:
    values: dict[str, object] = {
        "referral_id": "syn_referral_alpha",
        "version": 1,
        "status": SyntheticReferralStatus.OFFERED,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values[field] = value
    with pytest.raises(ReferralDomainError) as raised:
        SyntheticReferral(**cast(Any, values))
    assert raised.value.code is code


def test_referral_rejects_update_before_creation_and_normalizes_aware_utc() -> None:
    with pytest.raises(ReferralDomainError) as raised:
        referral(updated_at=NOW - timedelta(seconds=1))
    assert raised.value.code is ReferralDomainCode.INVALID_CHRONOLOGY

    offset = timezone(timedelta(hours=5, minutes=30))
    value = replace(
        referral(), created_at=NOW.astimezone(offset), updated_at=NOW.astimezone(offset)
    )
    assert value.created_at.tzinfo is UTC
    assert value.updated_at.tzinfo is UTC


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("command_id", "command_alpha"),
        ("referral_id", "real_referral"),
        ("idempotency_key", "opaque-key"),
        ("expected_version", 0),
        ("from_status", "OFFERED"),
        ("to_status", "CANCELLED"),
        ("occurred_at", datetime(2026, 10, 31, 12, 0, 1)),
    ],
)
def test_command_rejects_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "command_id": "syn_referral_command_alpha",
        "referral_id": "syn_referral_alpha",
        "idempotency_key": "syn_referral_idem_alpha",
        "expected_version": 1,
        "from_status": SyntheticReferralStatus.OFFERED,
        "to_status": SyntheticReferralStatus.CANCELLED,
        "occurred_at": NOW + timedelta(seconds=1),
    }
    values[field] = value
    with pytest.raises(ReferralDomainError):
        ReferralTransitionCommand(**cast(Any, values))


def test_pair_rejects_self_transition_and_policy_rejects_duplicate_pairs() -> None:
    with pytest.raises(ReferralDomainError) as self_transition:
        pair(SyntheticReferralStatus.OFFERED, SyntheticReferralStatus.OFFERED)
    assert self_transition.value.code is ReferralDomainCode.INVALID_TRANSITION

    configured_pair = pair()
    with pytest.raises(ReferralDomainError) as duplicate:
        policy(configured_pair, configured_pair)
    assert duplicate.value.code is ReferralDomainCode.DUPLICATE_IDENTITY


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("policy_id", "policy_fixture"),
        ("policy_version", "latest/current"),
        ("artifact_hash", "not-a-hash"),
        ("allowed_transitions", [pair()]),
        ("activated_at", datetime(2026, 10, 31, 12, 0)),
        ("authority", "PRODUCTION"),
    ],
)
def test_policy_rejects_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "policy_id": "syn_referral_policy_fixture",
        "policy_version": "v1",
        "artifact_hash": HASH,
        "allowed_transitions": (pair(),),
        "activated_at": NOW,
    }
    values[field] = value
    with pytest.raises(ReferralDomainError):
        SyntheticTransitionPolicy(**cast(Any, values))


@pytest.mark.parametrize(
    ("current", "transition", "configured_policy", "code"),
    [
        (
            referral(),
            replace(command(), referral_id="syn_referral_beta"),
            policy(),
            ReferralDomainCode.IDENTITY_MISMATCH,
        ),
        (
            referral(),
            command(expected_version=2),
            policy(),
            ReferralDomainCode.STALE_STATE,
        ),
        (
            referral(status=SyntheticReferralStatus.CONSENTED),
            command(),
            policy(),
            ReferralDomainCode.STALE_STATE,
        ),
        (
            referral(),
            command(occurred_at=NOW - timedelta(seconds=1)),
            policy(),
            ReferralDomainCode.INVALID_CHRONOLOGY,
        ),
        (
            referral(),
            command(),
            replace(policy(), activated_at=NOW + timedelta(seconds=2)),
            ReferralDomainCode.INVALID_CHRONOLOGY,
        ),
    ],
)
def test_transition_fails_closed_on_identity_state_and_chronology_errors(
    current: SyntheticReferral,
    transition: ReferralTransitionCommand,
    configured_policy: SyntheticTransitionPolicy,
    code: ReferralDomainCode,
) -> None:
    with pytest.raises(ReferralDomainError) as raised:
        apply_synthetic_transition(current, transition, configured_policy)
    assert raised.value.code is code


def test_engine_revalidates_forcibly_mutated_nested_inputs_and_receipts() -> None:
    hostile_command = command()
    object.__setattr__(hostile_command, "referral_id", "real_referral")
    with pytest.raises(ReferralDomainError):
        apply_synthetic_transition(referral(), hostile_command, policy())

    hostile_policy = policy()
    object.__setattr__(hostile_policy.allowed_transitions[0], "to_status", "CANCELLED")
    with pytest.raises(ReferralDomainError):
        apply_synthetic_transition(referral(), command(), hostile_policy)

    first = apply_synthetic_transition(referral(), command(), policy())
    hostile_receipt = first.receipt
    object.__setattr__(hostile_receipt, "result_version", 99)
    with pytest.raises(ReferralDomainError):
        apply_synthetic_transition(
            first.referral, command(), policy(), prior_receipts=(hostile_receipt,)
        )


def test_referral_contracts_cannot_accept_sensitive_or_external_effect_fields() -> None:
    aggregate_values = {
        "referral_id": "syn_referral_alpha",
        "version": 1,
        "status": SyntheticReferralStatus.OFFERED,
        "created_at": NOW,
        "updated_at": NOW,
    }
    for forbidden in (
        "patient_id",
        "session_id",
        "encounter_id",
        "destination_id",
        "consent_id",
        "payload",
        "contact",
        "external_reference",
    ):
        with pytest.raises(TypeError):
            cast(Any, SyntheticReferral)(**aggregate_values, **{forbidden: "value"})


def test_receipt_type_is_exposed_only_as_synthetic_mechanical_evidence() -> None:
    first = apply_synthetic_transition(referral(), command(), policy())
    assert type(first.receipt) is ReferralTransitionReceipt
    assert first.receipt.authority is SyntheticReferralAuthority.ENGINEERING_ONLY
    assert "syn_referral_idem_alpha" not in repr(first.receipt)
