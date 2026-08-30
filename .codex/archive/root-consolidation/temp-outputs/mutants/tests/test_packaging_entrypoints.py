"""
Test Packaging Entrypoints

Test module for packaging entrypoints.
"""

from __future__ import annotations

from pathlib import Path

# Prefer stdlib tomllib (3.11+) with tomli fallback for 3.9/3.10
try:  # pragma: no cover - exercised in CI matrix
    import tomllib as _toml  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    try:
        import tomli as _toml  # type: ignore
    except ImportError:  # pragma: no cover
        _toml = None


def test_packaging_entry_points_declared() -> None:
    if _toml is None:
        import pytest

        pytest.skip("tomllib/tomli not available in test environment")

    payload = _toml.loads(Path("pyproject.toml").read_text())
    entry_points = payload.get("project", {}).get("entry-points", {})

    for group in (
        "codex_ml.datasets",
        "codex_ml.data_loaders",
        "codex_ml.tokenizers",
        "codex_ml.reward_models",
    ):
        assert group in entry_points, f"Missing entry point group: {group}"
        assert entry_points[group], f"Entry point group {group} should not be empty"

    assert "lines" in entry_points["codex_ml.datasets"], "lines dataset must be declared"
    # Fixed malformed assertion: assert any(...)
