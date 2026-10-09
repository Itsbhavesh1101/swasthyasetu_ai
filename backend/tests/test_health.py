"""Canonical health endpoint contract tests."""

from httpx import AsyncClient


async def test_liveness_is_dependency_free(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_reports_only_current_dependencies(client: AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "required": {}, "optional": {}}
