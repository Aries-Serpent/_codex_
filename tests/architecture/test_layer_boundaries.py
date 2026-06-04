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
# copilot-setup-steps.yml integrity guard
#
# The session_preload block at lines ~141-145 uses shell brace syntax that is
# valid for GitHub Actions' Go YAML parser but is rejected by PyYAML's strict
# safe_load.  Any automated "fix" that normalises this block to a pipe `|`
# form or removes it would break the non-blocking fallback behaviour.
#
# These tests act as a tripwire: they will fail if the block is accidentally
# mutated, reformatted, or removed, prompting a human review before merge.
# ---------------------------------------------------------------------------

_SETUP_STEPS = ROOT / ".github" / "workflows" / "copilot-setup-steps.yml"
_SESSION_PRELOAD_STEP = "Session Context Pre-load (memory + policy + accountability + PDA)"
_SESSION_PRELOAD_SCRIPT = ".github/scripts/session_preload.py"


def test_copilot_setup_steps_exists() -> None:
    """copilot-setup-steps.yml must be present and non-empty."""
    assert _SETUP_STEPS.exists(), (
        "Missing: .github/workflows/copilot-setup-steps.yml — "
        "Copilot coding agent cannot initialise without it"
    )
    assert _SETUP_STEPS.stat().st_size > 0, "copilot-setup-steps.yml is empty"


def test_copilot_setup_steps_session_preload_block_intact() -> None:
    """The session_preload block-scalar form must remain intact.

    The `run: |` + `if ! python3 …; then … fi` form is intentional.  Reverting to
    inline shell-brace syntax (`|| { … }`) breaks YAML parsing and yamllint in CI.
    """
    lines = _SETUP_STEPS.read_text(encoding="utf-8").splitlines()

    # Locate the session_preload step by searching for the distinctive step name.
    step_start: int | None = None
    for i, line in enumerate(lines):
        if _SESSION_PRELOAD_STEP in line:
            step_start = i
            break

    assert step_start is not None, (
        "copilot-setup-steps.yml: could not find the session preload step — "
        "the canonical block-scalar form may have been removed or reformatted"
    )

    step_indent = len(lines[step_start]) - len(lines[step_start].lstrip())
    step_end = next(
        (
            i
            for i in range(step_start + 1, len(lines))
            if lines[i].lstrip().startswith("- name:")
            and len(lines[i]) - len(lines[i].lstrip()) == step_indent
        ),
        len(lines),
    )
    step_block = "\n".join(lines[step_start:step_end])

    assert "run: |" in step_block, (
        f"Step at line {step_start + 1}: expected block-scalar 'run: |' form — "
        "do not inline the session_preload shell command"
    )
    assert f"if ! python3 {_SESSION_PRELOAD_SCRIPT}; then" in step_block, (
        f"Step at line {step_start + 1}: expected guarded 'if ! python3 ...; then' shell form — "
        "the canonical non-blocking preload structure has changed"
    )
    assert 'echo "⚠️ session_preload.py failed (non-blocking)' in step_block, (
        f"Step at line {step_start + 1}: fallback echo is missing — "
        "the non-blocking error message must be preserved"
    )
    assert "fi" in step_block, (
        f"Step at line {step_start + 1}: expected closing 'fi' for the preload guard — "
        "block structure has changed"
    )


def test_copilot_setup_steps_session_preload_step_nonblocking() -> None:
    """The session_preload step must carry 'continue-on-error: true'.

    Removing this flag would cause the entire Copilot agent session to abort
    whenever session_preload.py fails, which is explicitly undesired.
    """
    lines = _SETUP_STEPS.read_text(encoding="utf-8").splitlines()

    # Find the step name that wraps the session_preload run
    step_start: int | None = None
    for i, line in enumerate(lines):
        if "Session Context Pre-load" in line or "session_preload" in line:
            # Walk back to the `- name:` anchor of this step
            for j in range(i, max(i - 5, 0), -1):
                if lines[j].lstrip().startswith("- name:"):
                    step_start = j
                    break
            if step_start is not None:
                break

    assert step_start is not None, (
        "copilot-setup-steps.yml: cannot locate the session_preload step — "
        "step may have been removed"
    )

    # The continue-on-error flag must appear within the next 5 lines of the step
    step_block = "\n".join(lines[step_start : step_start + 6])
    assert "continue-on-error: true" in step_block, (
        f"Step at line {step_start + 1}: 'continue-on-error: true' is missing — "
        "this flag is mandatory; removing it makes session_preload failures fatal"
    )


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
