from __future__ import annotations

import logging
from typing import Any

import hydra
from common.randomness import set_seed
from omegaconf import DictConfig, OmegaConf

from .pipeline import run_pipeline

logger = logging.getLogger(__name__)


@hydra.main(config_path="conf", config_name="config", version_base="1.3")
def main(cfg: DictConfig) -> Any:
    """Hydra entrypoint for hhg_logistics domain."""

    eff_seed = set_seed(getattr(getattr(cfg, "train", {}), "seed", None))
    logger.info("Seed set to %s", eff_seed)
    logger.info("Composed config:\n%s", OmegaConf.to_yaml(cfg))
    result = run_pipeline(cfg)
    return result


if __name__ == "__main__":
    main()
