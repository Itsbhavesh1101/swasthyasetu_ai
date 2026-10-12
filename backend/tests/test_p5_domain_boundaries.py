"""P5-A architecture and scope regression tests."""

import ast
from pathlib import Path

from app.config import Settings
from app.main import create_app
from app.shared.persistence import Base

DOMAIN_FILES = (
    Path("app/modules/patients/domain.py"),
    Path("app/modules/patients/clinical.py"),
    Path("app/modules/patients/public.py"),
    Path("app/modules/encounters/domain.py"),
    Path("app/modules/encounters/public.py"),
    Path("app/modules/provenance/domain.py"),
    Path("app/modules/provenance/public.py"),
)
FORBIDDEN_FRAMEWORKS = {"fastapi", "sqlalchemy", "psycopg", "alembic", "pydantic"}


def test_p5_domain_and_public_files_are_framework_independent() -> None:
    imported_roots: set[str] = set()
    for path in DOMAIN_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.partition(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_roots.add(node.module.partition(".")[0])

    assert imported_roots.isdisjoint(FORBIDDEN_FRAMEWORKS)


def test_p5a_does_not_register_runtime_modules_or_capabilities() -> None:
    application = create_app(Settings(_env_file=None))

    assert application.state.module_registry.module_ids == ("consent", "identity", "sessions")
    assert all(
        not name.startswith(("patients.", "encounters.", "provenance."))
        for name in application.state.capability_registry.registered_names
    )


def test_p5a_adds_no_api_routes() -> None:
    paths = create_app(Settings(_env_file=None)).openapi()["paths"]

    assert not any(
        path.startswith(("/api/v1/patients", "/api/v1/encounters", "/api/v1/clinical-facts"))
        for path in paths
    )


def test_p5a_adds_no_persistence_metadata() -> None:
    assert set(Base.metadata.tables) == {
        "actor_roles",
        "actors",
        "consent_records",
        "outbox_events",
        "sessions",
    }
