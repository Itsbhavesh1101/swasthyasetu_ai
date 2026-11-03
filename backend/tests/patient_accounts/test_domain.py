"""Patient account value and entity invariants."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.patient_accounts.domain import (
    AccountStatus,
    DisplayName,
    EmailAddress,
    PasswordDigest,
    PatientAccount,
    RawPassword,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 10, tzinfo=UTC)


def test_email_is_trimmed_and_normalized_without_exposing_it_in_repr() -> None:
    email = EmailAddress("  Patient.Name+demo@Example.COM  ")

    assert email.display == "Patient.Name+demo@Example.COM"
    assert email.normalized == "patient.name+demo@example.com"
    assert email.display not in repr(email)


@pytest.mark.parametrize(
    "value",
    ["", "patient", "@example.com", "patient@localhost", "patient @example.com", "a" * 321],
)
def test_email_rejects_invalid_or_unbounded_values(value: str) -> None:
    with pytest.raises(ValueError, match="email"):
        EmailAddress(value)


def test_display_name_is_trimmed_and_bounded() -> None:
    assert DisplayName("  Patient Demo  ").value == "Patient Demo"

    with pytest.raises(ValueError, match="display name"):
        DisplayName("   ")
    with pytest.raises(ValueError, match="display name"):
        DisplayName("x" * 121)


def test_raw_password_and_digest_are_always_redacted() -> None:
    raw = RawPassword("correct horse battery staple")
    digest = PasswordDigest("$argon2id$v=19$m=65536,t=3,p=4$synthetic$safe")

    assert raw.value not in repr(raw)
    assert digest.value not in repr(digest)
    assert "redacted" in repr(raw).casefold()
    assert "redacted" in repr(digest).casefold()


@pytest.mark.parametrize("value", ["short", " " * 12, "x" * 129])
def test_raw_password_is_bounded_without_normalizing_the_secret(value: str) -> None:
    with pytest.raises(ValueError, match="password"):
        RawPassword(value)


def test_patient_account_normalizes_aware_timestamps_to_utc() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    account = PatientAccount(
        account_id=OpaqueId.new(),
        actor_id=OpaqueId.new(),
        patient_id=OpaqueId.new(),
        email=EmailAddress("patient@example.com"),
        display_name=DisplayName("Patient Demo"),
        password_digest=PasswordDigest("$argon2id$v=19$m=65536,t=3,p=4$synthetic$safe"),
        status=AccountStatus.ACTIVE,
        created_at=non_utc,
        updated_at=non_utc,
    )

    assert account.created_at == NOW
    assert account.created_at.tzinfo is UTC
    assert account.updated_at.tzinfo is UTC
    assert "patient@example.com" not in repr(account)
    assert account.password_digest.value not in repr(account)


def test_patient_account_rejects_naive_or_reversed_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _account(created_at=NOW.replace(tzinfo=None), updated_at=NOW)
    with pytest.raises(ValueError, match="must not precede"):
        _account(created_at=NOW, updated_at=NOW - timedelta(seconds=1))


def _account(*, created_at: datetime, updated_at: datetime) -> PatientAccount:
    return PatientAccount(
        account_id=OpaqueId.new(),
        actor_id=OpaqueId.new(),
        patient_id=OpaqueId.new(),
        email=EmailAddress("patient@example.com"),
        display_name=DisplayName("Patient Demo"),
        password_digest=PasswordDigest("$argon2id$v=19$m=65536,t=3,p=4$synthetic$safe"),
        status=AccountStatus.ACTIVE,
        created_at=created_at,
        updated_at=updated_at,
    )
