"""Response-header and default-deny cross-origin security regressions."""

from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient, Response

from app.config import Settings
from app.config.settings import Environment
from app.main import create_app


async def _response(*, environment: Environment = Environment.TEST) -> Response:
    application = create_app(
        Settings(environment=environment, _env_file=None), module_registrations=()
    )
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="https://test"
    ) as client:
        return await client.get("/health/live")


async def test_api_security_headers_are_explicit_and_hsts_is_environment_bound() -> None:
    response = await _response()

    assert response.status_code == 200
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    )
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), geolocation=(), microphone=(), payment=(), usb=()"
    )
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert "strict-transport-security" not in response.headers

    production = await _response(environment=Environment.PRODUCTION)
    assert production.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )


async def test_cross_origin_requests_receive_no_cors_authority() -> None:
    application = create_app(Settings(_env_file=None), module_registrations=())
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="https://api.example"
    ) as client:
        simple = await client.get("/health/live", headers={"Origin": "https://attacker.invalid"})
        preflight = await client.options(
            "/api/v1/synthetic",
            headers={
                "Origin": "https://attacker.invalid",
                "Access-Control-Request-Method": "POST",
            },
        )

    for response in (simple, preflight):
        assert "access-control-allow-origin" not in response.headers
        assert "access-control-allow-credentials" not in response.headers


async def test_security_headers_cover_sanitized_unexpected_errors() -> None:
    router = APIRouter()

    @router.get("/synthetic-failure")
    async def synthetic_failure() -> None:
        raise RuntimeError("private synthetic detail")

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="https://test"
    ) as client:
        response = await client.get("/api/v1/synthetic-failure")

    assert response.status_code == 500
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"].startswith("default-src 'none'")
    assert "private synthetic detail" not in response.text
