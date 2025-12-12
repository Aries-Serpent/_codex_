"""Minimal Hydra entry point exercising the structured config schema."""

from __future__ import annotations

import hydra
from hydra.core.global_hydra import GlobalHydra

from configs.schemas import AppCfg, register_schema
from omegaconf import OmegaConf
from src.training.offline_wandb import force_offline
from src.training.seed_utils import set_all_seeds

# Register the schema once at import time so ``hydra.main`` can resolve it.
register_schema(name="app_schema")


@hydra.main(version_base=None, config_name="app_schema")
def main(cfg: AppCfg) -> None:
    """Demonstrate composing the dataclass schema without external YAML files."""

    force_offline()
    set_all_seeds(cfg.train.seed, deterministic=True)

    print(OmegaConf.to_yaml(cfg, resolve=True, sort_keys=True))
    print("train_schema_demo: OK")


if __name__ == "__main__":
    global_hydra = GlobalHydra.instance()
    is_initialized = False
    checker = getattr(global_hydra, "is_initialized", None)
    if callable(checker):
        is_initialized = bool(checker())
    else:
        is_initialized = bool(getattr(global_hydra, "initialized", False))

    if is_initialized:
        global_hydra.clear()

    main()
