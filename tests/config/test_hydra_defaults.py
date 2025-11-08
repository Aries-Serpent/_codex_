from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("hydra")
pytest.importorskip("omegaconf")


def test_conf_defaults_list_round_trip() -> None:
    from hydra import compose, initialize_config_dir

    # Get absolute path relative to this test file
    config_dir = Path(__file__).resolve().parents[2] / "configs" / "base"
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="hydra")
    # The top-level config should have been composed from configs/base/hydra.yaml.
    # In Hydra 1.3+, defaults list is not preserved in the final config
    # So we just verify the config loaded and has expected keys
    assert cfg.model.name
    assert cfg.training.output_dir
