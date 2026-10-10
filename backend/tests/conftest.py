"""Shared fixtures for backend foundation tests."""

import asyncio
import sys
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Environment, Settings
from app.main import create_app

if sys.platform == "win32":
    policy_factory = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if policy_factory is not None:
        asyncio.set_event_loop_policy(policy_factory())


@pytest.fixture
def test_settings() -> Settings:
    """Return explicit settings without reading a local environment file."""
    return Settings(environment=Environment.TEST, _env_file=None)


@pytest.fixture
async def client(test_settings: Settings) -> AsyncIterator[AsyncClient]:
    """Provide an in-process asynchronous HTTP client."""
    application = create_app(test_settings)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
