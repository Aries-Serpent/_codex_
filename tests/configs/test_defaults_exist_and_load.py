"""
Test Defaults Exist And Load

Test module for defaults exist and load.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_defaults_yaml_contains_sections() -> None:
    config_path = REPO_ROOT / "configs/base/defaults.yaml"
    assert config_path.exists(), "Condition must be true"

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert "training" in data, "Data must not be empty"
    assert "logging" in data, "Data must not be empty"
    assert "tracking" in data, "Data must not be empty"
