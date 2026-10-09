"""Common error-envelope tests."""

from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.api.errors import ApplicationError, ErrorCode
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
            status_code=409,
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
