"""Architecture/privacy boundaries for the detached P8-B package."""

from __future__ import annotations

import ast
from pathlib import Path

EXTRACTION_ROOT = Path("app/modules/clinical_intake/extraction")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)
    return imports


def test_extraction_package_imports_no_adapters_persistence_api_or_later_phase_authority() -> None:
    forbidden_fragments = (
        "app.adapters",
        "sqlalchemy",
        "persistence",
        ".api",
        "safety",
        "triage",
        "diagnosis",
        "self_care",
        "mental_health",
    )
    imports = set().union(*(_imports(path) for path in EXTRACTION_ROOT.glob("*.py")))

    assert not {
        imported
        for imported in imports
        if any(fragment in imported for fragment in forbidden_fragments)
    }


def test_default_clinical_intake_registration_has_no_extraction_dependency() -> None:
    public_imports = _imports(Path("app/modules/clinical_intake/public.py"))
    main_imports = _imports(Path("app/main.py"))

    assert not any("clinical_intake.extraction" in value for value in public_imports | main_imports)


def test_extraction_package_has_no_logging_or_telemetry_content_sink() -> None:
    forbidden_imports = {"logging", "app.shared.observability", "opentelemetry"}
    imports = set().union(*(_imports(path) for path in EXTRACTION_ROOT.glob("*.py")))

    assert imports.isdisjoint(forbidden_imports)
