from __future__ import annotations

from pathlib import Path

# Prefer stdlib tomllib (3.11+); fallback to tomli if installed
try:
    import tomllib as _toml  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    try:
        import tomli as _toml  # type: ignore
    except Exception:  # pragma: no cover
        _toml = None


def test_pyproject_scripts_have_canonical_entrypoints():
    if _toml is None:
        import pytest

        pytest.skip("tomllib/tomli not available in test environment")
    root = Path(__file__).resolve().parents[1]
    data = _toml.load((root / "pyproject.toml").open("rb"))
    project = data.get("project", {})
    scripts = project.get("scripts", {})
    # Canonical scripts expected in this repo
    expected = {
        "codex-train": "codex_ml.cli.entrypoints:train_main",
        "codex-eval": "codex_ml.cli.entrypoints:eval_main",
        "codex-list-plugins": "codex_ml.cli.list_plugins:main",
    }
    # Ensure keys exist
    for k in expected:
        assert k in scripts, f"missing [project.scripts].{k}"
    # Ensure values are wired to canonical targets
    for k, v in expected.items():
        assert scripts.get(k) == v, f"script {k} must map to {v}"
