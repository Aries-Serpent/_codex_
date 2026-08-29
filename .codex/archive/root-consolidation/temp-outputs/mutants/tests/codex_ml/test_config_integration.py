"""
Test Config Integration

Test module for config integration.
"""

from pathlib import Path

import yaml


def test_basic_config_loads():
    root = Path(__file__).resolve().parents[2]
    cfg = root / "conf" / "config.yaml"
    assert cfg.exists(), "Condition must be true"
    data = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    assert "experiment" in data, "Data must not be empty"
