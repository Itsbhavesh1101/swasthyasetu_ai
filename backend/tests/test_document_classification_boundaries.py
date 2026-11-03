"""P11-C compile-time isolation and zero-runtime-activation evidence."""

import ast
from pathlib import Path

from app.main import app
from app.modules.documents.registry import build_synthetic_processor_registry

ROOT = Path(__file__).parents[1]


def test_synthetic_document_classification_remains_absent_from_runtime() -> None:
    document_paths = [path for path in app.openapi()["paths"] if "document" in path.casefold()]
    assert document_paths
    assert all(
        path.startswith("/api/v1/patients/{patient_id}/documents") for path in document_paths
    )
    assert "documents" not in app.state.module_registry.module_ids
    assert not (ROOT / "app/modules/documents/public.py").exists()
    assert not (ROOT / "app/modules/documents/application.py").exists()


def test_new_production_modules_have_no_io_dynamic_loading_or_provider_imports() -> None:
    forbidden = {
        "asyncio",
        "httpx",
        "importlib",
        "os",
        "pathlib",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "urllib",
    }
    for name in ("classification.py", "registry.py"):
        tree = ast.parse((ROOT / "app/modules/documents" / name).read_text(encoding="utf-8"))
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported |= {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert imported.isdisjoint(forbidden)


def test_registry_factory_is_side_effect_free_and_not_globally_cached() -> None:
    first = build_synthetic_processor_registry()
    second = build_synthetic_processor_registry()
    assert first == second
    assert first is not second


def test_no_document_orm_migration_worker_or_frontend_surface_exists() -> None:
    assert not any("document" in path.name for path in (ROOT / "migrations/versions").glob("*.py"))
    assert not any("document" in path.name for path in (ROOT.parent / "workers").rglob("*.py"))
    assert not any("document" in path.name for path in (ROOT.parent / "apps").rglob("route.ts"))


def test_document_module_does_not_import_clinical_fact_safety_summary_or_ai_domains() -> None:
    forbidden = ("patients", "safety", "summaries", "ai_orchestration")
    for path in (ROOT / "app/modules/documents").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [
            ast.unparse(node)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        assert all(all(item not in value for item in forbidden) for value in imports)
