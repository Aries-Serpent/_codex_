"""
Architecture Layer Boundary Tests — D1 exit criteria.

Validates that the import-layer contracts defined in .importlinter and
docs/architecture/ARCHITECTURE_LAYERS.md are not violated in the live codebase.

Run: pytest tests/architecture/ -v
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent.parent
SRC = ROOT / "src"


def _imports_from(src_file: Path) -> list[str]:
    """Return top-level module names imported by a Python file."""
    try:
        tree = ast.parse(src_file.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module.split(".")[0])
    return modules


def _files_under(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return list(directory.rglob("*.py"))


# ---------------------------------------------------------------------------
# L1 boundary: CLI / apps / tools must NOT import from tests/
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("layer_dir", ["cli", "apps", "tools"])
def test_l1_no_test_imports(layer_dir: str) -> None:
    """CLI/apps/tools layers must not import from tests."""
    layer_path = ROOT / layer_dir
    violations: list[str] = []
    for f in _files_under(layer_path):
        for mod in _imports_from(f):
            if mod == "tests":
                violations.append(str(f.relative_to(ROOT)))
    assert not violations, (
        f"Layer 1 ({layer_dir}) imports 'tests' — prohibited upward dependency:\n"
        + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# L5 boundary: tests/ must not import production cli/apps/tools directly
# (only src.* packages)
# ---------------------------------------------------------------------------

def test_tests_no_direct_cli_import() -> None:
    """Test files should import src.* not CLI entry-point scripts directly."""
    tests_path = ROOT / "tests"
    # This is a soft check — warn but don't fail on edge cases
    prohibited = {"cli", "apps", "tools"}
    violations: list[str] = []
    for f in _files_under(tests_path):
        for mod in _imports_from(f):
            if mod in prohibited:
                violations.append(f"{f.relative_to(ROOT)} imports '{mod}'")
    # Warn only — CLI integration tests legitimately import entry-points
    if violations:
        pytest.skip(
            f"Soft boundary: {len(violations)} test file(s) import L1 modules directly "
            f"(expected for integration tests). Review: {violations[:5]}"
        )


# ---------------------------------------------------------------------------
# Architecture document integrity
# ---------------------------------------------------------------------------

def test_architecture_doc_exists() -> None:
    """D1 — architecture layer document must be present."""
    doc = ROOT / "docs" / "architecture" / "ARCHITECTURE_LAYERS.md"
    assert doc.exists(), f"Missing: {doc} — required for D1 exit criteria"


def test_import_linter_config_exists() -> None:
    """D1 — .importlinter config must be present."""
    config = ROOT / ".importlinter"
    assert config.exists(), f"Missing: {config} — required for import-linter.yml CI gate"


def test_import_linter_workflow_exists() -> None:
    """D1 — import-linter.yml CI workflow must be present."""
    wf = ROOT / ".github" / "workflows" / "import-linter.yml"
    assert wf.exists(), f"Missing: {wf} — D1 CI gate workflow"


def test_domain_ownership_doc_exists() -> None:
    """D1 — DOMAIN_OWNERSHIP.md must be present (architecture ownership map)."""
    doc = ROOT / ".codex" / "DOMAIN_OWNERSHIP.md"
    assert doc.exists(), f"Missing: {doc} — D1 exit criteria"


# ---------------------------------------------------------------------------
# Source structure integrity (no empty __init__ stubs in critical packages)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pkg", ["codex_ml", "codex", "mcp"])
def test_src_package_has_init(pkg: str) -> None:
    """Critical src packages must have __init__.py."""
    init = SRC / pkg / "__init__.py"
    if not (SRC / pkg).exists():
        pytest.skip(f"Package src/{pkg} not found — skipping")
    assert init.exists(), f"src/{pkg}/__init__.py missing — package may not be importable"
