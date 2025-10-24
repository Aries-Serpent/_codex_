from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("hydra")
pytest.importorskip("omegaconf")


def test_conf_defaults_list_round_trip() -> None:
    from hydra import compose, initialize_config_dir

    config_dir = Path("configs/base").resolve()
    with initialize_config_dir(version_base="1.3", config_dir=str(config_dir)):
        cfg = compose(config_name="hydra")
    # The top-level config mirrors the defaults list declared in configs/base/hydra.yaml.
    defaults = cfg.get("defaults", [])
    assert defaults
    assert defaults[0]["_self_"]
    assert cfg.model.name
    assert cfg.training.output_dir
