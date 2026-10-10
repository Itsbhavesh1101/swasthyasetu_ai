"""Common error-envelope tests."""

import pytest
from fastapi import APIRouter, Body
from httpx import ASGITransport, AsyncClient

from app.api.errors import ApplicationError, DependencyError, ErrorCode, SwasthyaSetuError
from app.api.errors.handlers import HTTP_STATUS_BY_ERROR_CODE
from app.api.middleware import REQUEST_ID_HEADER
from app.config import Settings
from app.main import create_app


async def test_unknown_route_uses_canonical_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "The requested resource was not found.",
            "request_id": response.headers[REQUEST_ID_HEADER],
            "details": {},
        }
    }


async def test_typed_application_error_does_not_leak_internal_details() -> None:
    router = APIRouter()

    @router.get("/failure")
    async def failure() -> None:
        raise ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="The resource is not in the required state.",
        )

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        response = await test_client.get("/api/v1/failure")

    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "RESOURCE_CONFLICT"
    assert body["error"]["request_id"] == response.headers[REQUEST_ID_HEADER]
    assert "traceback" not in response.text.lower()
    assert "ApplicationError" not in response.text


def test_error_code_registry_matches_canonical_contract() -> None:
    assert {code.value for code in ErrorCode} == {
        "VALIDATION_ERROR",
        "AUTHENTICATION_REQUIRED",
        "AUTHORIZATION_DENIED",
        "RESOURCE_NOT_FOUND",
        "RESOURCE_CONFLICT",
        "INVALID_STATE_TRANSITION",
        "FEATURE_DISABLED",
        "CONSENT_REQUIRED",
        "SESSION_EXPIRED",
        "RATE_LIMITED",
        "DEPENDENCY_TIMEOUT",
        "DEPENDENCY_UNAVAILABLE",
        "PROCESSING_FAILED",
        "POLICY_UNAVAILABLE",
        "INSUFFICIENT_INFORMATION",
        "UNSUPPORTED_MEDIA_TYPE",
        "PAYLOAD_TOO_LARGE",
    }


def test_shared_error_base_is_framework_independent() -> None:
    assert SwasthyaSetuError.__mro__ == (SwasthyaSetuError, Exception, BaseException, object)
    assert SwasthyaSetuError.__module__ == "app.shared.errors.base"


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        (ErrorCode.DEPENDENCY_TIMEOUT, 503),
        (ErrorCode.DEPENDENCY_UNAVAILABLE, 503),
        (ErrorCode.PAYLOAD_TOO_LARGE, 413),
        (ErrorCode.UNSUPPORTED_MEDIA_TYPE, 415),
    ],
)
def test_explicit_http_error_mapping(code: ErrorCode, expected_status: int) -> None:
    assert HTTP_STATUS_BY_ERROR_CODE[code] == expected_status


async def test_dependency_error_maps_to_safe_envelope() -> None:
    router = APIRouter()

    @router.get("/dependency-timeout")
    async def dependency_timeout() -> None:
        raise DependencyError(
            code=ErrorCode.DEPENDENCY_TIMEOUT,
            message="A required service timed out.",
            details={"operation": "synthetic"},
            cause=TimeoutError("internal provider detail"),
        )

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        response = await test_client.get("/api/v1/dependency-timeout")

    assert response.status_code == 503
    assert response.json()["error"]["details"] == {"operation": "synthetic"}
    assert "internal provider detail" not in response.text


async def test_validation_error_does_not_echo_submitted_value() -> None:
    router = APIRouter()

    @router.post("/validated")
    async def validated(value: int = Body(embed=True)) -> dict[str, int]:
        return {"value": value}

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        response = await test_client.post(
            "/api/v1/validated", json={"value": "synthetic-secret-value"}
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "synthetic-secret-value" not in response.text


async def test_unhandled_error_does_not_expose_exception_or_stack_trace() -> None:
    router = APIRouter()

    @router.get("/unexpected-failure")
    async def unexpected_failure() -> None:
        raise RuntimeError("sensitive-internal-detail")

    application = create_app(Settings(_env_file=None), api_v1_routers=(router,))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        response = await test_client.get("/api/v1/unexpected-failure")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "PROCESSING_FAILED"
    assert "sensitive-internal-detail" not in response.text
    assert "traceback" not in response.text.lower()
