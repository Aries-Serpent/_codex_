from __future__ import annotations

from pathlib import Path

import tomllib


def test_packaging_entry_points_declared() -> None:
    payload = tomllib.loads(Path("pyproject.toml").read_text())
    entry_points = payload.get("project", {}).get("entry-points", {})

    for group in ("codex_ml.datasets", "codex_ml.data_loaders", "codex_ml.tokenizers", "codex_ml.reward_models"):
        assert group in entry_points, f"Missing entry point group: {group}"
        assert entry_points[group], f"Entry point group {group} should not be empty"

    assert "lines" in entry_points["codex_ml.datasets"], "lines dataset must be declared"
    assert any(name for name in entry_points["codex_ml.reward_models"].keys()), "Reward models must be discoverable"
