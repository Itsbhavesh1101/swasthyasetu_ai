"""Architecture tests for isolation of research code from patient runtime."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = ROOT / "backend" / "app"


def _research_imports(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(
                alias.name
                for alias in node.names
                if alias.name == "ml" or alias.name.startswith("ml.")
            )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "ml" or module.startswith("ml."):
                found.append(module)
    return tuple(found)


class ResearchIsolationTests(unittest.TestCase):
    def test_backend_application_does_not_import_research_package(self) -> None:
        violations = {
            path.relative_to(ROOT).as_posix(): imports
            for path in BACKEND_APP.rglob("*.py")
            if (imports := _research_imports(path))
        }

        self.assertEqual(violations, {})


if __name__ == "__main__":
    unittest.main()
