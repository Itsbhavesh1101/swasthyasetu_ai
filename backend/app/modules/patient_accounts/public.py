"""Stable exports and explicit composition for patient accounts."""

from collections.abc import Callable
from datetime import datetime

from fastapi import APIRouter

from app.config import PatientAccountSettings
from app.modules.identity.infrastructure import PostgresActorRepository
from app.modules.patient_accounts.api import build_patient_accounts_router
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
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime
from app.shared.types import utc_now

PATIENT_ACCOUNTS_AUTHENTICATE = CapabilityKey[PatientAccountService](
    CapabilityIdentifier("patient_accounts.authenticate")
)
PATIENT_ACCOUNTS_CURRENT = CapabilityKey[PatientAccountService](
    CapabilityIdentifier("patient_accounts.current")
)
PATIENT_ACCOUNTS_LOGOUT = CapabilityKey[PatientAccountService](
    CapabilityIdentifier("patient_accounts.logout")
)

PATIENT_ACCOUNTS_MANIFEST = ModuleManifest(
    module_id=ModuleId("patient_accounts"),
    version=1,
    provided_capabilities=frozenset(
        key.identifier
        for key in (
            PATIENT_ACCOUNTS_AUTHENTICATE,
            PATIENT_ACCOUNTS_CURRENT,
            PATIENT_ACCOUNTS_LOGOUT,
        )
    ),
    api_prefixes=("/accounts",),
    required_permissions=("patient:read:self",),
    configuration_keys=("patient_accounts",),
    data_ownership=("patient_accounts",),
)


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


def build_patient_accounts_registration(
    *, service: PatientAccountService
) -> ModuleRegistration[APIRouter]:
    return ModuleRegistration(
        manifest=PATIENT_ACCOUNTS_MANIFEST,
        routers=(build_patient_accounts_router(service=service),),
        capability_bindings=(
            PATIENT_ACCOUNTS_AUTHENTICATE.bind(service),
            PATIENT_ACCOUNTS_CURRENT.bind(service),
            PATIENT_ACCOUNTS_LOGOUT.bind(service),
        ),
    )


__all__ = [
    "AccountSession",
    "AccountStatus",
    "CurrentAccount",
    "DisplayName",
    "EmailAddress",
    "LoginPatient",
    "PATIENT_ACCOUNTS_AUTHENTICATE",
    "PATIENT_ACCOUNTS_CURRENT",
    "PATIENT_ACCOUNTS_LOGOUT",
    "PATIENT_ACCOUNTS_MANIFEST",
    "PatientAccountService",
    "RawPassword",
    "RegisterPatient",
    "build_patient_account_service",
    "build_patient_accounts_registration",
]
