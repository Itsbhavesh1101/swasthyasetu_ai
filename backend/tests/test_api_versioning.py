"""API v1 router-boundary tests."""

from fastapi import APIRouter
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app


async def test_registered_module_router_is_mounted_below_v1_prefix() -> None:
    module_router = APIRouter()

    @module_router.get("/foundation-probe")
    async def foundation_probe() -> dict[str, str]:
        return {"status": "ok"}

    application = create_app(Settings(_env_file=None), api_v1_routers=(module_router,))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        versioned_response = await test_client.get("/api/v1/foundation-probe")
        unversioned_response = await test_client.get("/foundation-probe")

    assert versioned_response.status_code == 200
    assert unversioned_response.status_code == 404
