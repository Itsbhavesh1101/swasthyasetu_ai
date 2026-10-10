"""Shared PostgreSQL persistence primitives for application composition."""

from app.shared.persistence.base import NAMING_CONVENTION, Base
from app.shared.persistence.runtime import DatabaseRuntime, create_database_runtime

__all__ = ["Base", "DatabaseRuntime", "NAMING_CONVENTION", "create_database_runtime"]
