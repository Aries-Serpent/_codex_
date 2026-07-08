"""
Test Hydra Defaults

Test module for hydra defaults.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("hydra")
pytest.importorskip("omegaconf")


def test_conf_defaults_list_round_trip() -> None:
    from hydra import compose, initialize_config_dir

    # Resolve path relative to repository root (2 levels up from this test file)
    config_dir = Path(__file__).resolve().parents[2] / "configs" / "base"
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="hydra")
    # Verify that key sections from the defaults list are present
    assert cfg.model.name, "Condition must be true"
    assert cfg.training.output_dir, "Condition must be true"
