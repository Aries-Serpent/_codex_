from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("hydra")
pytest.importorskip("omegaconf")

from hydra import compose, initialize_config_dir


def test_conf_defaults_list_round_trip() -> None:
    config_dir = Path("conf").resolve()
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="config")
    # The top-level config mirrors the defaults list declared in conf/config.yaml.
    defaults = cfg.get("defaults", [])
    assert defaults
    assert defaults[0]["_self_"]
    assert cfg.model.name
    assert cfg.training.output_dir
