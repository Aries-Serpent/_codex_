"""
Main Module

This module provides functionality for main.

Usage:
    from hhg_logistics.main import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import hydra
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    import config_legacy as hydra  # type: ignore[no-redef]


from common.randomness import set_seed  # noqa: E402
from omegaconf import DictConfig, OmegaConf  # noqa: E402

from .pipeline import run_pipeline  # noqa: E402


@hydra.main(
    config_path="../../configs/deployment/hhg_logistics",
    config_name="config",
    version_base="1.3",
)
def main(cfg: DictConfig) -> Any:
    """Hydra entrypoint for hhg_logistics domain."""

    eff_seed = set_seed(getattr(getattr(cfg, "train", {}), "seed", None))
    logger.info("Seed set to %s", eff_seed)
    logger.info("Composed config:\n%s", OmegaConf.to_yaml(cfg))
    return run_pipeline(cfg)


if __name__ == "__main__":
    main()
