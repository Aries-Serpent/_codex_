from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_defaults_yaml_contains_sections() -> None:
    config_path = REPO_ROOT / "configs/defaults.yaml"
    assert config_path.exists()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert "training" in data
    assert "logging" in data
    assert "tracking" in data
