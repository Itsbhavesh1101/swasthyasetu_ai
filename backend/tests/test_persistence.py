"""Network-free tests for the shared persistence foundation."""

from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config import DatabaseSettings
from app.events.outbox import OutboxEventRecord
from app.shared.persistence import NAMING_CONVENTION, Base, DatabaseRuntime
from app.shared.persistence.runtime import create_database_runtime


def enabled_settings() -> DatabaseSettings:
    """Return valid settings without opening a database connection."""
    return DatabaseSettings(
        enabled=True,
        url="postgresql+psycopg://synthetic:secret@localhost/synthetic",
    )


def test_disabled_database_creates_no_runtime() -> None:
    assert create_database_runtime(DatabaseSettings()) is None


async def test_runtime_constructs_lazily_with_async_engine_and_session_factory() -> None:
    runtime = DatabaseRuntime(enabled_settings())
    try:
        assert runtime.enabled is True
        assert isinstance(runtime.engine, AsyncEngine)
        assert isinstance(runtime.session_factory, async_sessionmaker)
        assert runtime.session_factory.class_ is AsyncSession
        assert runtime.engine.echo is False
    finally:
        await runtime.dispose()


def test_metadata_contains_only_the_platform_outbox_table() -> None:
    assert tuple(Base.metadata.tables) == (OutboxEventRecord.__tablename__,)
    assert Base.metadata.naming_convention == NAMING_CONVENTION


def test_metadata_naming_convention_is_deterministic() -> None:
    parent = Table("synthetic_parent", Base.metadata, Column("id", Integer, primary_key=True))
    child = Table(
        "synthetic_child",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("parent_id", ForeignKey("synthetic_parent.id"), index=True),
        Column("code", Integer),
        UniqueConstraint("code"),
    )
    try:
        names = {constraint.name for constraint in child.constraints}
        index_names = {index.name for index in child.indexes}
        assert "pk_synthetic_child" in names
        assert "fk_synthetic_child_parent_id_synthetic_parent" in names
        assert "uq_synthetic_child_code" in names
        assert "ix_synthetic_child_parent_id" in index_names
    finally:
        Base.metadata.remove(child)
        Base.metadata.remove(parent)
