"""Dependency-direction checks for independently published packages."""

from __future__ import annotations

import ast
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
STANDALONE_SOURCES = REPOSITORY_ROOT / "packages"
MONOLITH_PACKAGES = {"aries_serpent_core", "codex", "codex_ml", "cognitive_brain"}


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.partition(".")[0])
    return imported


def test_standalone_packages_do_not_import_monolith_packages() -> None:
    violations: list[str] = []
    for path in sorted(STANDALONE_SOURCES.glob("*/src/**/*.py")):
        forbidden = sorted(_top_level_imports(path) & MONOLITH_PACKAGES)
        if forbidden:
            relative = path.relative_to(REPOSITORY_ROOT)
            violations.append(f"{relative}: {', '.join(forbidden)}")

    assert not violations, "standalone package boundary violations:\n" + "\n".join(violations)
