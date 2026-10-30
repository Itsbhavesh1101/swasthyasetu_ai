from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from fastapi import APIRouter, FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.middleware import RateLimitMiddleware
from app.config import Environment, RateLimitSettings, Settings
from app.main import create_app
from app.shared.rate_limits import (
    InMemorySlidingWindowRateLimiter,
    RateLimitDecision,
    RateLimiter,
    RateLimitSubject,
)


class RecordingLimiter:
    def __init__(self, decision: RateLimitDecision | None = None) -> None:
        self.calls: list[tuple[RateLimitSubject, ...]] = []
        self._decision = decision or RateLimitDecision.allowed_request()

    async def check(self, subjects: Sequence[RateLimitSubject]) -> RateLimitDecision:
        captured = tuple(subjects)
        self.calls.append(captured)
        return self._decision


class FalseyRecordingLimiter(RecordingLimiter):
    def __bool__(self) -> bool:
        return False


class FailingLimiter:
    async def check(self, subjects: Sequence[RateLimitSubject]) -> RateLimitDecision:
        raise RuntimeError("private limiter failure")


def router() -> APIRouter:
    probe = APIRouter()

    @probe.get("/probe")
    async def read_probe() -> dict[str, bool]:
        return {"ok": True}

    @probe.post("/probe")
    async def mutate_probe() -> dict[str, bool]:
        return {"ok": True}

    @probe.post("/sessions")
    async def create_session_probe() -> dict[str, bool]:
        return {"ok": True}

    return probe


def settings(**overrides: int) -> Settings:
    budgets = {
        "process_requests": 100,
        "peer_requests": 80,
        "credential_requests": 60,
        "mutation_peer_requests": 40,
        "mutation_credential_requests": 20,
        "session_creation_peer_requests": 10,
        **overrides,
    }
    return Settings(
        environment=Environment.TEST,
        rate_limits=RateLimitSettings(**budgets),
        _env_file=None,
    )


async def client_for(limiter: RateLimiter, *, configured: Settings | None = None) -> AsyncClient:
    application = create_app(
        configured or settings(),
        api_v1_routers=(router(),),
        module_registrations=(),
        rate_limiter=limiter,
    )
    return AsyncClient(transport=ASGITransport(app=application), base_url="http://test")


@pytest.mark.asyncio
async def test_health_and_non_api_paths_are_exempt() -> None:
    limiter = RecordingLimiter()
    async with await client_for(limiter) as client:
        assert (await client.get("/health/live")).status_code == 200
        assert (await client.get("/missing")).status_code == 404

    assert limiter.calls == []


@pytest.mark.asyncio
async def test_explicit_falsey_limiter_is_not_replaced() -> None:
    limiter = FalseyRecordingLimiter()
    async with await client_for(limiter) as client:
        assert (await client.get("/api/v1/probe")).status_code == 200

    assert len(limiter.calls) == 1


def test_empty_explicit_fingerprint_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="fingerprint key"):
        RateLimitMiddleware(
            FastAPI(),
            limiter=RecordingLimiter(),
            settings=settings().rate_limits,
            api_v1_prefix="/api/v1",
            fingerprint_key=b"",
        )


def test_container_entrypoint_disables_uvicorn_proxy_header_rewriting() -> None:
    dockerfile = (
        Path(__file__).resolve().parents[2] / "infra" / "docker" / "backend.Dockerfile"
    ).read_text(encoding="utf-8")

    assert '"--no-proxy-headers"' in dockerfile


@pytest.mark.asyncio
async def test_api_read_uses_process_peer_and_hmac_credential_layers() -> None:
    limiter = RecordingLimiter()
    async with await client_for(limiter) as client:
        response = await client.get(
            "/api/v1/probe",
            headers={
                "Authorization": "Bearer super-secret-value",
                "X-Forwarded-For": "198.51.100.99",
            },
        )

    assert response.status_code == 200
    captured = limiter.calls[0]
    assert [item.rule.name for item in captured] == ["process", "peer", "credential"]
    assert captured[0].key == "all"
    assert captured[1].key == "127.0.0.1"
    assert captured[1].key != "198.51.100.99"
    assert len(captured[2].key) == 64
    assert "super-secret-value" not in repr(captured)


@pytest.mark.asyncio
async def test_mutation_and_session_creation_add_stricter_layers() -> None:
    limiter = RecordingLimiter()
    async with await client_for(limiter) as client:
        await client.post("/api/v1/probe", headers={"Authorization": "Bearer opaque"})
        await client.post("/api/v1/sessions")

    assert [item.rule.name for item in limiter.calls[0]] == [
        "process",
        "peer",
        "credential",
        "mutation_peer",
        "mutation_credential",
    ]
    assert [item.rule.name for item in limiter.calls[1]] == [
        "process",
        "peer",
        "mutation_peer",
        "session_creation_peer",
    ]


@pytest.mark.asyncio
async def test_malformed_authorization_cannot_create_credential_bucket() -> None:
    limiter = RecordingLimiter()
    async with await client_for(limiter) as client:
        await client.get("/api/v1/probe", headers={"Authorization": "Bearer "})

    assert [item.rule.name for item in limiter.calls[0]] == ["process", "peer"]


@pytest.mark.asyncio
async def test_denial_uses_canonical_private_response_and_outer_headers() -> None:
    limiter = RecordingLimiter(RateLimitDecision.denied_request(1.2))
    async with await client_for(limiter) as client:
        response = await client.post(
            "/api/v1/probe",
            headers={"X-Request-ID": "req_0123456789abcdef0123456789abcdef"},
        )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "2"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Request-ID"] == "req_0123456789abcdef0123456789abcdef"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.json() == {
        "error": {
            "code": "RATE_LIMITED",
            "details": {},
            "message": "Too many requests.",
            "request_id": "req_0123456789abcdef0123456789abcdef",
        }
    }


@pytest.mark.asyncio
async def test_real_limiter_enforces_configured_api_budget() -> None:
    configured = settings(
        process_requests=2,
        peer_requests=2,
        credential_requests=2,
        mutation_peer_requests=2,
        mutation_credential_requests=2,
        session_creation_peer_requests=2,
    )
    limiter = InMemorySlidingWindowRateLimiter(max_tracked_keys=16)
    async with await client_for(limiter, configured=configured) as client:
        assert (await client.get("/api/v1/probe")).status_code == 200
        assert (await client.get("/api/v1/probe")).status_code == 200
        assert (await client.get("/api/v1/probe")).status_code == 429


@pytest.mark.asyncio
async def test_limiter_failure_fails_closed_without_raw_diagnostics() -> None:
    async with await client_for(FailingLimiter()) as client:
        response = await client.get("/api/v1/probe")

    assert response.status_code == 500
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "private limiter failure" not in response.text
    assert response.json()["error"]["code"] == "PROCESSING_FAILED"
