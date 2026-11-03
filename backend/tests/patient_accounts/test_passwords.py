"""Argon2id password hashing behavior."""

import pytest

from app.modules.patient_accounts.domain import PasswordDigest, RawPassword
from app.modules.patient_accounts.passwords import Argon2PasswordHasher


def test_argon2id_hash_uses_library_salt_and_verifies() -> None:
    hasher = Argon2PasswordHasher()
    password = RawPassword("correct horse battery staple")

    first = hasher.hash(password)
    second = hasher.hash(password)

    assert isinstance(first, PasswordDigest)
    assert first.value.startswith("$argon2id$")
    assert first != second
    assert hasher.verify(password, first) is True
    assert hasher.verify(RawPassword("a different secure password"), first) is False


def test_invalid_password_digest_fails_closed_without_leaking() -> None:
    hasher = Argon2PasswordHasher()
    malformed = PasswordDigest.from_persisted("not-an-argon2-hash")

    assert hasher.verify(RawPassword("correct horse battery staple"), malformed) is False
    assert malformed.value not in repr(malformed)


def test_normal_constructor_rejects_non_argon2id_digest() -> None:
    with pytest.raises(ValueError, match="Argon2id"):
        PasswordDigest("not-an-argon2-hash")
