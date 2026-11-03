"""Patient account HTTP contract and authentication-boundary tests."""

from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.errors import register_error_handlers
from app.modules.patient_accounts.api import build_patient_accounts_router
from app.modules.patient_accounts.contracts import AccountSession, CurrentAccount
from app.modules.patient_accounts.domain import AccountStatus
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 10, tzinfo=UTC)
ACCOUNT_ID = OpaqueId.new()
ACTOR_ID = OpaqueId.new()
PATIENT_ID = OpaqueId.new()
SESSION_ID = OpaqueId.new()
TOKEN = "opaque-patient-account-token"


class FakeAccountService:
    def __init__(self) -> None:
        self.closed = False
        self.authenticated = False

    async def register(self, command: object) -> AccountSession:
        return _account_session()

    async def login(self, command: object) -> AccountSession:
        return _account_session()

    async def authenticate(self, token: str) -> ActorContext:
        assert token == TOKEN
        self.authenticated = True
        return ActorContext(
            actor_id=ACTOR_ID,
            actor_type="PATIENT",
            roles=frozenset({"patient"}),
            subject_id=PATIENT_ID,
            session_id=SESSION_ID,
            is_authenticated=True,
        )

    async def get_current_account(self, token: str) -> CurrentAccount:
        assert token == TOKEN
        return _current_account()

    async def close_session(self, token: str) -> None:
        assert token == TOKEN
        self.closed = True


def _current_account() -> CurrentAccount:
    return CurrentAccount(
        account_id=ACCOUNT_ID,
        actor_id=ACTOR_ID,
        patient_id=PATIENT_ID,
        email="Patient@Example.com",
        display_name="Patient Demo",
        status=AccountStatus.ACTIVE,
    )


def _account_session() -> AccountSession:
    return AccountSession(
        account=_current_account(),
        session=Session(
            session_id=SESSION_ID,
            session_type=SessionType.AUTHENTICATED,
            language_preference="en",
            status=SessionStatus.ACTIVE,
            created_at=NOW,
            expires_at=NOW + timedelta(hours=12),
            closed_at=None,
            updated_at=NOW,
            actor_id=ACTOR_ID,
            patient_id=PATIENT_ID,
        ),
        session_token=TOKEN,
    )


def _app(service: FakeAccountService) -> FastAPI:
    application = FastAPI()
    register_error_handlers(application)
    application.include_router(build_patient_accounts_router(service=service), prefix="/api/v1")
    return application


async def test_register_and_login_return_only_minimized_session_credentials() -> None:
    secret = "correct horse battery staple"
    service = FakeAccountService()
    transport = ASGITransport(app=_app(service))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": " Patient@Example.com ",
                "display_name": " Patient Demo ",
                "password": secret,
                "preferred_language": "en",
            },
        )
        login = await client.post(
            "/api/v1/accounts/login",
            json={"email": "patient@example.com", "password": secret},
        )

    assert register.status_code == 201
    assert login.status_code == 200
    for response in (register, login):
        assert response.headers["cache-control"] == "no-store"
        assert response.json() == {
            "session_id": str(SESSION_ID),
            "session_token": TOKEN,
            "expires_at": "2026-11-03T22:00:00Z",
        }
        assert secret not in response.text
        assert "password_hash" not in response.text


async def test_me_and_logout_require_bearer_and_install_trusted_context() -> None:
    service = FakeAccountService()
    transport = ASGITransport(app=_app(service))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        missing = await client.get("/api/v1/accounts/me")
        me = await client.get("/api/v1/accounts/me", headers={"Authorization": f"Bearer {TOKEN}"})
        logout = await client.post(
            "/api/v1/accounts/logout", headers={"Authorization": f"Bearer {TOKEN}"}
        )

    assert missing.status_code == 401
    assert TOKEN not in missing.text
    assert me.status_code == 200
    assert me.headers["cache-control"] == "no-store"
    assert me.json() == {
        "account_id": str(ACCOUNT_ID),
        "patient_id": str(PATIENT_ID),
        "email": "Patient@Example.com",
        "display_name": "Patient Demo",
    }
    assert service.authenticated is True
    assert logout.status_code == 204
    assert logout.content == b""
    assert service.closed is True


async def test_account_requests_are_strict_and_validation_never_echoes_password() -> None:
    secret = "correct horse battery staple"
    transport = ASGITransport(app=_app(FakeAccountService()))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "patient@example.com",
                "display_name": "Patient Demo",
                "password": secret,
                "unexpected": True,
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.headers["cache-control"] == "no-store"
    assert secret not in response.text
