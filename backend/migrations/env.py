"""Alembic environment backed by project settings and async SQLAlchemy."""

from __future__ import annotations

import asyncio
import selectors
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import Settings
from app.events.outbox import OutboxEventRecord  # noqa: F401 - registers Alembic metadata
from app.modules.identity.infrastructure import (  # noqa: F401 - registers Alembic metadata
    ActorRecord,
    ActorRoleRecord,
)
from app.modules.sessions.infrastructure import (  # noqa: F401 - registers Alembic metadata
    SessionRecord,
)
from app.shared.persistence import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    """Load the migration URL without exposing it in configuration errors."""
    settings = Settings(_env_file=None)
    if not settings.database.enabled or settings.database.url is None:
        raise RuntimeError("database must be explicitly enabled for migrations")
    return settings.database.url.get_secret_value()


def run_migrations_offline() -> None:
    """Generate migration SQL without creating an engine."""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations on an established synchronous facade connection."""
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async migration engine and dispose it deterministically."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run the normal online migration workflow."""
    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
        ) as runner:
            runner.run(run_async_migrations())
        return
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
