"""P11-B non-activation and dependency boundary evidence."""

import ast
from pathlib import Path

from app.main import app

ROOT = Path(__file__).parents[1]


def test_no_document_runtime_route_or_registration() -> None:
    assert all("documents" not in path for path in app.openapi()["paths"])
    assert not (ROOT / "app/modules/documents/public.py").exists()
    assert not (ROOT / "app/modules/documents/application.py").exists()


def test_production_source_never_imports_test_mock() -> None:
    for path in (ROOT / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [
            node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        assert all(
            "ocr_support" not in ast.unparse(node) and "MockOCRAdapter" not in ast.unparse(node)
            for node in imports
        )


def test_no_runtime_io_or_provider_dependency_in_documents_package() -> None:
    forbidden = {
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "pathlib",
        "sqlalchemy",
        "paddleocr",
        "docling",
        "tesseract",
    }
    for path in (ROOT / "app/modules/documents").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
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


def test_no_document_schema_or_migration_added() -> None:
    assert not any("document" in path.name for path in (ROOT / "alembic/versions").glob("*.py"))
