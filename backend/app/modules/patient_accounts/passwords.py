"""Argon2id password hashing adapter."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from argon2.low_level import Type

from app.modules.patient_accounts.domain import PasswordDigest, RawPassword


class Argon2PasswordHasher:
    """Use argon2-cffi's managed salt and parameter encoding."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher(type=Type.ID)

    def hash(self, password: RawPassword) -> PasswordDigest:
        return PasswordDigest(self._hasher.hash(password.value))

    def verify(self, password: RawPassword, digest: PasswordDigest) -> bool:
        try:
            return self._hasher.verify(digest.value, password.value)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False
