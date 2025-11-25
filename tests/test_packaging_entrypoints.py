from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec
from pathlib import Path

import pytest

tomllib_spec = find_spec("tomllib")
if tomllib_spec is not None:
    tomllib = import_module("tomllib")
else:
    tomli_spec = find_spec("tomli")
    if tomli_spec is not None:
        tomllib = import_module("tomli")  # type: ignore[assignment]
    else:
        tomllib = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(tomllib is None, reason="tomllib/tomli not available")


def test_packaging_entry_points_declared() -> None:
    payload = tomllib.loads(Path("pyproject.toml").read_text())
    entry_points = payload.get("project", {}).get("entry-points", {})

    for group in ("codex_ml.datasets", "codex_ml.data_loaders", "codex_ml.tokenizers", "codex_ml.reward_models"):
        assert group in entry_points, f"Missing entry point group: {group}"
        assert entry_points[group], f"Entry point group {group} should not be empty"

    assert "lines" in entry_points["codex_ml.datasets"], "lines dataset must be declared"
    assert any(name for name in entry_points["codex_ml.reward_models"].keys()), "Reward models must be discoverable"
