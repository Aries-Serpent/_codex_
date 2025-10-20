"""Structured Hydra configuration schema for lightweight training demos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING


@dataclass
class TrainCfg:
    lr: float = 3e-4
    batch_size: int = 8
    max_steps: int = 1000
    seed: int = 1337


@dataclass
class DataCfg:
    dataset_name: str = MISSING
    split_seed: int = 42
    num_workers: int = 4
    cache_dir: Optional[str] = None


@dataclass
class AppCfg:
    train: TrainCfg = field(default_factory=TrainCfg)
    data: DataCfg = field(default_factory=DataCfg)


def register_schema(name: str = "app_schema") -> None:
    """Register the structured config with Hydra's :class:`ConfigStore`."""

    cs = ConfigStore.instance()
    try:
        cs.store(name=name, node=AppCfg)
    except ValueError as exc:  # Hydra raises ValueError when re-registering the same name
        if "exists" not in str(exc):
            raise


__all__ = ["AppCfg", "DataCfg", "TrainCfg", "register_schema"]
