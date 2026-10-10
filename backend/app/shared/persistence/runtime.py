"""Per-application asynchronous PostgreSQL engine and transaction runtime."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DatabaseSettings


def _configure_windows_asyncio_policy() -> None:
    """Select the event-loop policy required by async Psycopg on Windows."""
    if sys.platform != "win32":
        return
    policy_factory = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if policy_factory is not None and not isinstance(
        asyncio.get_event_loop_policy(), policy_factory
    ):
        asyncio.set_event_loop_policy(policy_factory())


class DatabaseRuntime:
    """Own one application's engine, session factory, and transaction boundary."""

    def __init__(self, settings: DatabaseSettings) -> None:
        if not settings.enabled or settings.url is None:
            raise ValueError("database runtime requires enabled database settings")

        _configure_windows_asyncio_policy()
        self.enabled = True
        self.engine: AsyncEngine = create_async_engine(
            settings.url.get_secret_value(),
            echo=False,
            pool_pre_ping=True,
            pool_timeout=settings.pool_timeout_seconds,
            connect_args={"connect_timeout": settings.connect_timeout_seconds},
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        """Commit on success, roll back on error, and always close the session."""
        async with self.session_factory() as session, session.begin():
            yield session

    async def ping(self) -> None:
        """Run one minimal bounded connectivity query."""
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def dispose(self) -> None:
        """Release this application's engine pool."""
        await self.engine.dispose()


def create_database_runtime(settings: DatabaseSettings) -> DatabaseRuntime | None:
    """Create a runtime only when PostgreSQL is explicitly enabled."""
    if not settings.enabled:
        return None
    return DatabaseRuntime(settings)
