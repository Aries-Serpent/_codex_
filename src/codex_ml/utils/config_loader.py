from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from hydra import compose, initialize_config_dir
from hydra.errors import MissingConfigException
from omegaconf import DictConfig, OmegaConf

_CFG_DIR = (
    Path(__file__).resolve().parents[3] / "configs" / "training"
)  # resolved relative to repo root
_PRIMARY = "base"


@dataclass
class TrainingDefaults:
    seed: int = 42
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 3
    logging: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "training": {
                "seed": self.seed,
                "lr": self.lr,
                "batch_size": self.batch_size,
                "epochs": self.epochs,
            },
            "logging": self.logging
            or {
                "enable_tensorboard": False,
                "enable_wandb": False,
                "mlflow_enable": False,
            },
        }


def load_training_cfg(
    *, allow_fallback: bool = True, overrides: Optional[list[str]] = None
) -> DictConfig:
    """Load Hydra config from ``configs/training/base.yaml`` with fallback.

    When the config file is missing and ``allow_fallback`` is ``True`` a
    deterministic programmatic configuration is returned.
    """

    overrides = overrides or []

    cfg_dir = _CFG_DIR
    if cfg_dir.is_dir() and (cfg_dir / f"{_PRIMARY}.yaml").is_file():
        # Hydra Compose API: https://hydra.cc/docs/advanced/compose_api/
        with initialize_config_dir(version_base=None, config_dir=str(cfg_dir)):
            return compose(config_name=_PRIMARY, overrides=overrides)

    if not allow_fallback:
        raise MissingConfigException(
            missing_cfg_file=f"{_CFG_DIR}/{_PRIMARY}.yaml",
            message="Config file missing",
        )

    base = TrainingDefaults().to_dict()
    cfg = OmegaConf.create(base)
    if overrides:
        for item in overrides:
            key, value = item.split("=", 1)
            parsed = yaml.safe_load(value)
            OmegaConf.update(cfg, key, parsed, merge=True)
    return cfg
