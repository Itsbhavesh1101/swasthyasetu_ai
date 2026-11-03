"""Stable exports and explicit composition for patient accounts."""

from collections.abc import Callable
from datetime import datetime

from app.config import PatientAccountSettings
from app.modules.identity.infrastructure import PostgresActorRepository
from app.modules.patient_accounts.application import PatientAccountService
from app.modules.patient_accounts.contracts import (
    AccountSession,
    CurrentAccount,
    LoginPatient,
    RegisterPatient,
)
from app.modules.patient_accounts.domain import (
    AccountStatus,
    DisplayName,
    EmailAddress,
    RawPassword,
)
from app.modules.patient_accounts.infrastructure import PostgresPatientAccountRepository
from app.modules.patient_accounts.passwords import Argon2PasswordHasher
from app.modules.patients.infrastructure import PostgresPatientRepository
from app.modules.sessions.infrastructure import PostgresSessionRepository
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now


def build_patient_account_service(
    *,
    database: DatabaseRuntime | None,
    settings: PatientAccountSettings,
    clock: Callable[[], datetime] | None = None,
) -> PatientAccountService:
    return PatientAccountService(
        database=database,
        settings=settings,
        accounts=PostgresPatientAccountRepository(),
        actors=PostgresActorRepository(),
        patients=PostgresPatientRepository(),
        sessions=PostgresSessionRepository(),
        passwords=Argon2PasswordHasher(),
        clock=utc_now if clock is None else clock,
    )


__all__ = [
    "AccountSession",
    "AccountStatus",
    "CurrentAccount",
    "DisplayName",
    "EmailAddress",
    "LoginPatient",
    "PatientAccountService",
    "RawPassword",
    "RegisterPatient",
    "build_patient_account_service",
]
