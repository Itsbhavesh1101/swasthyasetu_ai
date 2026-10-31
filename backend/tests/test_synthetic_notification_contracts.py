from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.notifications.domain import (
    NotificationDomainCode,
    NotificationDomainError,
    SafeSyntheticVariable,
    SyntheticFailureCode,
    SyntheticFailureReceipt,
    SyntheticNotificationAuthority,
    SyntheticNotificationClassification,
    SyntheticNotificationFailure,
    SyntheticNotificationIntent,
    SyntheticNotificationTemplate,
    SyntheticNotificationVerification,
    record_synthetic_failure,
)

NOW = datetime(2026, 10, 31, 14, 0, tzinfo=UTC)
HASH = "e" * 64


def variable(
    key: str = "syn_var_reference",
    value: str = "syn_value_alpha",
) -> SafeSyntheticVariable:
    return SafeSyntheticVariable(key=key, value=value)


def template(*keys: str) -> SyntheticNotificationTemplate:
    return SyntheticNotificationTemplate(
        template_id="syn_notification_template_fixture",
        template_version="v1",
        artifact_hash=HASH,
        allowed_variable_keys=keys or ("syn_var_reference",),
        created_at=NOW,
    )


def intent(*variables: SafeSyntheticVariable) -> SyntheticNotificationIntent:
    return SyntheticNotificationIntent(
        notification_id="syn_notification_alpha",
        correlation_id="syn_notification_correlation_alpha",
        template_id="syn_notification_template_fixture",
        template_version="v1",
        template_artifact_hash=HASH,
        variables=variables or (variable(),),
        created_at=NOW + timedelta(seconds=1),
    )


def failure(
    code: SyntheticFailureCode = SyntheticFailureCode.SIMULATED_UNAVAILABLE,
) -> SyntheticNotificationFailure:
    return SyntheticNotificationFailure(
        failure_id="syn_notification_failure_alpha",
        notification_id="syn_notification_alpha",
        code=code,
        occurred_at=NOW + timedelta(seconds=2),
    )


def test_records_only_a_synthetic_failure_without_delivery_claim() -> None:
    receipt = record_synthetic_failure(intent(), template(), failure())

    assert receipt.failure_id == "syn_notification_failure_alpha"
    assert receipt.code is SyntheticFailureCode.SIMULATED_UNAVAILABLE
    assert receipt.authority is SyntheticNotificationAuthority.ENGINEERING_ONLY
    assert receipt.classification is SyntheticNotificationClassification.ENGINEERING_SYNTHETIC
    assert receipt.verification is SyntheticNotificationVerification.UNVERIFIED
    assert receipt.recorded_at == NOW + timedelta(seconds=2)
    with pytest.raises(FrozenInstanceError):
        receipt.code = SyntheticFailureCode.SIMULATED_TIMEOUT  # type: ignore[misc]


def test_intent_and_template_are_canonicalized_without_free_text() -> None:
    configured_template = template("syn_var_zeta", "syn_var_alpha")
    notification = intent(
        variable("syn_var_zeta", "syn_value_zeta"),
        variable("syn_var_alpha", "syn_value_alpha"),
    )

    receipt = record_synthetic_failure(notification, configured_template, failure())

    assert configured_template.allowed_variable_keys == ("syn_var_alpha", "syn_var_zeta")
    assert tuple(item.key for item in notification.variables) == (
        "syn_var_alpha",
        "syn_var_zeta",
    )
    assert (
        receipt.intent_fingerprint
        == record_synthetic_failure(notification, configured_template, failure()).intent_fingerprint
    )


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("reference", "syn_value_alpha"),
        ("syn_var_reference", "patient has condition"),
        ("syn_var_reference", "https://example.invalid"),
        ("syn_var_reference", "syn_value_alpha\nsecret"),
        ("syn_var_" + "x" * 100, "syn_value_alpha"),
    ],
)
def test_variable_rejects_non_synthetic_or_content_bearing_values(key: str, value: str) -> None:
    with pytest.raises(NotificationDomainError):
        SafeSyntheticVariable(key=key, value=value)


def test_intent_requires_exact_template_variable_set() -> None:
    with pytest.raises(NotificationDomainError) as missing:
        record_synthetic_failure(
            intent(), template("syn_var_reference", "syn_var_second"), failure()
        )
    assert missing.value.code is NotificationDomainCode.TEMPLATE_MISMATCH

    with pytest.raises(NotificationDomainError) as extra:
        record_synthetic_failure(
            intent(variable(), variable("syn_var_second", "syn_value_second")),
            template(),
            failure(),
        )
    assert extra.value.code is NotificationDomainCode.TEMPLATE_MISMATCH


def test_template_and_intent_reject_duplicate_variable_keys() -> None:
    with pytest.raises(NotificationDomainError) as template_duplicate:
        template("syn_var_reference", "syn_var_reference")
    assert template_duplicate.value.code is NotificationDomainCode.DUPLICATE_IDENTITY

    with pytest.raises(NotificationDomainError) as intent_duplicate:
        intent(variable(), variable(value="syn_value_second"))
    assert intent_duplicate.value.code is NotificationDomainCode.DUPLICATE_IDENTITY


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("template_id", "template_fixture"),
        ("template_version", "latest/current"),
        ("artifact_hash", "not-a-hash"),
        ("allowed_variable_keys", ["syn_var_reference"]),
        ("allowed_variable_keys", ()),
        ("created_at", datetime(2026, 10, 31, 14, 0)),
        ("authority", "PRODUCTION"),
        ("classification", "REAL_DATA"),
        ("verification", "VERIFIED"),
    ],
)
def test_template_rejects_invalid_or_live_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "template_id": "syn_notification_template_fixture",
        "template_version": "v1",
        "artifact_hash": HASH,
        "allowed_variable_keys": ("syn_var_reference",),
        "created_at": NOW,
    }
    values[field] = value
    with pytest.raises(NotificationDomainError):
        SyntheticNotificationTemplate(**cast(Any, values))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("notification_id", "notification_alpha"),
        ("correlation_id", "correlation_alpha"),
        ("template_id", "template_fixture"),
        ("template_version", "latest/current"),
        ("template_artifact_hash", "not-a-hash"),
        ("variables", [variable()]),
        ("created_at", datetime(2026, 10, 31, 14, 0, 1)),
        ("authority", "PRODUCTION"),
    ],
)
def test_intent_rejects_invalid_or_live_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "notification_id": "syn_notification_alpha",
        "correlation_id": "syn_notification_correlation_alpha",
        "template_id": "syn_notification_template_fixture",
        "template_version": "v1",
        "template_artifact_hash": HASH,
        "variables": (variable(),),
        "created_at": NOW + timedelta(seconds=1),
    }
    values[field] = value
    with pytest.raises(NotificationDomainError):
        SyntheticNotificationIntent(**cast(Any, values))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("failure_id", "failure_alpha"),
        ("notification_id", "notification_alpha"),
        ("code", "TIMEOUT"),
        ("occurred_at", datetime(2026, 10, 31, 14, 0, 2)),
        ("authority", "PRODUCTION"),
    ],
)
def test_failure_rejects_invalid_or_live_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "failure_id": "syn_notification_failure_alpha",
        "notification_id": "syn_notification_alpha",
        "code": SyntheticFailureCode.SIMULATED_UNAVAILABLE,
        "occurred_at": NOW + timedelta(seconds=2),
    }
    values[field] = value
    with pytest.raises(NotificationDomainError):
        SyntheticNotificationFailure(**cast(Any, values))


def test_template_binding_and_chronology_fail_closed() -> None:
    with pytest.raises(NotificationDomainError) as identity:
        record_synthetic_failure(
            replace(intent(), template_version="v2"),
            template(),
            failure(),
        )
    assert identity.value.code is NotificationDomainCode.TEMPLATE_MISMATCH

    with pytest.raises(NotificationDomainError) as template_time:
        record_synthetic_failure(
            replace(intent(), created_at=NOW - timedelta(seconds=1)),
            template(),
            failure(),
        )
    assert template_time.value.code is NotificationDomainCode.INVALID_CHRONOLOGY

    with pytest.raises(NotificationDomainError) as failure_time:
        record_synthetic_failure(
            intent(),
            template(),
            replace(failure(), occurred_at=NOW),
        )
    assert failure_time.value.code is NotificationDomainCode.INVALID_CHRONOLOGY


def test_failure_must_bind_the_exact_notification() -> None:
    with pytest.raises(NotificationDomainError) as raised:
        record_synthetic_failure(
            intent(),
            template(),
            replace(failure(), notification_id="syn_notification_beta"),
        )
    assert raised.value.code is NotificationDomainCode.IDENTITY_MISMATCH


@pytest.mark.parametrize(
    "reserved_id",
    [
        "syn_notification_template_alpha",
        "syn_notification_correlation_alpha",
        "syn_notification_failure_alpha",
    ],
)
def test_notification_identity_cannot_use_another_contract_namespace(
    reserved_id: str,
) -> None:
    with pytest.raises(NotificationDomainError) as intent_error:
        replace(intent(), notification_id=reserved_id)
    assert intent_error.value.code is NotificationDomainCode.INVALID_VALUE

    with pytest.raises(NotificationDomainError) as failure_error:
        replace(failure(), notification_id=reserved_id)
    assert failure_error.value.code is NotificationDomainCode.INVALID_VALUE


def test_aware_non_utc_timestamps_normalize_to_utc() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    configured_template = replace(template(), created_at=NOW.astimezone(offset))
    notification = replace(intent(), created_at=(NOW + timedelta(seconds=1)).astimezone(offset))
    simulated_failure = replace(
        failure(), occurred_at=(NOW + timedelta(seconds=2)).astimezone(offset)
    )

    receipt = record_synthetic_failure(notification, configured_template, simulated_failure)

    assert configured_template.created_at.tzinfo is UTC
    assert notification.created_at.tzinfo is UTC
    assert simulated_failure.occurred_at.tzinfo is UTC
    assert receipt.recorded_at.tzinfo is UTC


def test_nested_forced_mutation_is_revalidated() -> None:
    hostile_variable = variable()
    object.__setattr__(hostile_variable, "value", "patient has condition")
    hostile_intent = intent()
    object.__setattr__(hostile_intent, "variables", (hostile_variable,))
    with pytest.raises(NotificationDomainError):
        record_synthetic_failure(hostile_intent, template(), failure())

    hostile_template = template()
    object.__setattr__(hostile_template, "artifact_hash", "not-a-hash")
    with pytest.raises(NotificationDomainError):
        record_synthetic_failure(intent(), hostile_template, failure())

    hostile_failure = failure()
    object.__setattr__(hostile_failure, "code", "DELIVERED")
    with pytest.raises(NotificationDomainError):
        record_synthetic_failure(intent(), template(), hostile_failure)


def test_contracts_have_no_recipient_channel_copy_delivery_or_retry_fields() -> None:
    values = {
        "notification_id": "syn_notification_alpha",
        "correlation_id": "syn_notification_correlation_alpha",
        "template_id": "syn_notification_template_fixture",
        "template_version": "v1",
        "template_artifact_hash": HASH,
        "variables": (variable(),),
        "created_at": NOW + timedelta(seconds=1),
    }
    for forbidden in (
        "recipient",
        "contact",
        "channel",
        "subject_ref",
        "message",
        "locale",
        "provider",
        "delivery_status",
        "retryable",
        "attempt_number",
        "referral_id",
    ):
        with pytest.raises(TypeError):
            cast(Any, SyntheticNotificationIntent)(**values, **{forbidden: "value"})


def test_module_exposes_no_send_port_success_or_delivery_receipt() -> None:
    import app.modules.notifications.domain as domain

    for forbidden in (
        "NotificationPort",
        "send",
        "DeliveredNotification",
        "DeliveryReceipt",
        "DEFAULT_TEMPLATE",
    ):
        assert not hasattr(domain, forbidden)


def test_receipt_repr_hides_fingerprints_and_has_no_referral_state() -> None:
    receipt = record_synthetic_failure(intent(), template(), failure())

    assert type(receipt) is SyntheticFailureReceipt
    assert receipt.intent_fingerprint not in repr(receipt)
    assert not hasattr(receipt, "referral_status")
    assert not hasattr(receipt, "delivered")
