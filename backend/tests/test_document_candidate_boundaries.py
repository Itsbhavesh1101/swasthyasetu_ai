"""P11-D zero-activation and import-boundary tests."""

import ast
from pathlib import Path

from app.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_new_modules_have_only_pure_document_contract_dependencies() -> None:
    allowed = {
        "app.modules.documents.candidates",
        "app.modules.documents.classification",
        "app.modules.documents.contracts",
        "app.modules.documents.registry",
        "app.shared.types",
    }
    forbidden = (
        "sqlalchemy",
        "httpx",
        "requests",
        "socket",
        "pathlib",
        "app.modules.patients",
        "app.modules.ai",
        "app.modules.safety",
        "app.jobs",
        "app.storage",
    )
    for name in ("candidates.py", "evidence.py"):
        tree = ast.parse((ROOT / "app/modules/documents" / name).read_text(encoding="utf-8"))
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(module.startswith(forbidden) for module in imported)
        assert all(not module.startswith("app.") or module in allowed for module in imported)


def test_no_runtime_document_api_or_public_activation() -> None:
    assert not (ROOT / "app/modules/documents/public.py").exists()
    assert not (ROOT / "app/modules/documents/application.py").exists()
    paths = app.openapi()["paths"]
    assert not any("document" in path.lower() for path in paths)
    source = (ROOT / "app/main.py").read_text(encoding="utf-8")
    assert "documents.candidates" not in source
    assert "documents.evidence" not in source


def test_no_executable_or_value_extraction_surface() -> None:
    for name in ("candidates.py", "evidence.py"):
        source = (ROOT / "app/modules/documents" / name).read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert not functions.intersection(
            {"extract", "parse", "promote", "confirm", "open_source", "execute"}
        )
        assert "TextBlock.text" not in source
        assert ".text" not in source


def test_no_schema_or_dependency_change() -> None:
    versions = tuple((ROOT / "migrations/versions").glob("*.py"))
    assert len(versions) == 7
    assert "p7a_0007" in (ROOT / "alembic.ini").read_text(encoding="utf-8") or any(
        "p7a_0007" in item.read_text(encoding="utf-8") for item in versions
    )
