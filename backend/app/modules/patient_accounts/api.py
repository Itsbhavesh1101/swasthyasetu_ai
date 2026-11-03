"""Versioned HTTP transport for patient accounts."""

from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.api.security.bearer import parse_bearer
from app.api.security.patient_authentication import authenticate_patient
from app.modules.patient_accounts.contracts import (
    AccountSession,
    CurrentAccount,
    LoginPatient,
    RegisterPatient,
)
from app.modules.patient_accounts.domain import DisplayName, EmailAddress, RawPassword
from app.shared.security import ActorContext


class PatientAccountHttpService(Protocol):
    async def register(self, command: RegisterPatient) -> AccountSession: ...
    async def login(self, command: LoginPatient) -> AccountSession: ...
    async def authenticate(self, token: str) -> ActorContext: ...
    async def get_current_account(self, token: str) -> CurrentAccount: ...
    async def close_session(self, token: str) -> None: ...


class RegisterAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=120)
    password: SecretStr
    preferred_language: str | None = Field(default=None, min_length=2, max_length=35)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return EmailAddress(value).display

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return DisplayName(value).value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        RawPassword(value.get_secret_value())
        return value


class LoginAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)
    password: SecretStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return EmailAddress(value).display

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        RawPassword(value.get_secret_value())
        return value


class AccountSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: UUID
    session_token: str
    expires_at: datetime


class CurrentAccountResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: UUID
    patient_id: UUID
    email: str
    display_name: str


def _session_response(value: AccountSession) -> AccountSessionResponse:
    return AccountSessionResponse(
        session_id=value.session.session_id.value,
        session_token=value.session_token,
        expires_at=value.session.expires_at,
    )


def _current_response(value: CurrentAccount) -> CurrentAccountResponse:
    return CurrentAccountResponse(
        account_id=value.account_id.value,
        patient_id=value.patient_id.value,
        email=value.email,
        display_name=value.display_name,
    )


def build_patient_accounts_router(*, service: PatientAccountHttpService) -> APIRouter:
    router = APIRouter(prefix="/accounts", tags=["patient-accounts"])

    async def require_patient(
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> ActorContext:
        return await authenticate_patient(request, authorization, authenticator=service)

    patient_dependency: Callable[..., object] = require_patient

    @router.post(
        "/register",
        response_model=AccountSessionResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_account(
        payload: RegisterAccountRequest, response: Response
    ) -> AccountSessionResponse:
        response.headers["Cache-Control"] = "no-store"
        result = await service.register(
            RegisterPatient(
                email=EmailAddress(payload.email),
                display_name=DisplayName(payload.display_name),
                password=RawPassword(payload.password.get_secret_value()),
                preferred_language=payload.preferred_language,
            )
        )
        return _session_response(result)

    @router.post("/login", response_model=AccountSessionResponse)
    async def login_account(
        payload: LoginAccountRequest, response: Response
    ) -> AccountSessionResponse:
        response.headers["Cache-Control"] = "no-store"
        result = await service.login(
            LoginPatient(
                email=EmailAddress(payload.email),
                password=RawPassword(payload.password.get_secret_value()),
            )
        )
        return _session_response(result)

    @router.get(
        "/me",
        response_model=CurrentAccountResponse,
        dependencies=[Depends(patient_dependency)],
    )
    async def current_account(
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> CurrentAccountResponse:
        response.headers["Cache-Control"] = "no-store"
        return _current_response(await service.get_current_account(parse_bearer(authorization)))

    @router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(patient_dependency)],
    )
    async def logout_account(
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> None:
        response.headers["Cache-Control"] = "no-store"
        await service.close_session(parse_bearer(authorization))

    return router
