from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf


def test_hydra_sweep_config_loads() -> None:
    cfg = OmegaConf.load(Path("configs/base/hydra_sweep.yaml"))
    assert cfg.hydra.sweep.dir.startswith("outputs/")
    template = OmegaConf.load(Path("configs/experiments/sweep_template.yaml"))
    assert template.defaults[0] == "/base/hydra_sweep"
