"""
Test Hydra Sweep

Test module for hydra sweep.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from omegaconf import OmegaConf


def test_hydra_sweep_config_loads() -> None:
    # Register 'now' resolver for OmegaConf interpolation
    if not OmegaConf.has_resolver("now"):
        OmegaConf.register_new_resolver("now", lambda fmt: datetime.now().strftime(fmt))

    cfg = OmegaConf.load(Path("configs/base/hydra_sweep.yaml"))
    assert cfg.hydra.sweep.dir.startswith("outputs/"), "Condition must be true"
    template = OmegaConf.load(Path("configs/experiments/sweep_template.yaml"))
    assert template.defaults[0] == "/base/hydra_sweep", "Condition must be true"
