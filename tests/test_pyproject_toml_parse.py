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


def test_pyproject_toml_parses_strictly():
    if _toml is None:
        # Environment doesn't provide a TOML parser; skip.
        import pytest

        pytest.skip("tomllib/tomli not available in test environment")
    root = Path(__file__).resolve().parents[1]
    data = _toml.load((root / "pyproject.toml").open("rb"))
    assert "project" in data, "pyproject missing [project] table"
    # Basic sanity on critical fields (non-exhaustive)
    project = data["project"]
    assert isinstance(project.get("name", ""), str) and project["name"], "project.name must be set"
    assert isinstance(project.get("requires-python", ""), str) and project[
        "requires-python"
    ].startswith(">="), "project.requires-python must be a PEP 440 spec"
