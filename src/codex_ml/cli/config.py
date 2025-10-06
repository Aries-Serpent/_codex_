"""Structured Hydra configuration for Codex training."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class ModelCfg:
    """Model-related hyperparameters."""

    name: str = "gpt2"
    dtype: str = "float32"
    lora_enable: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05


@dataclass
class OptimCfg:
    """Optimizer parameters."""

    learning_rate: float = 3e-4
    weight_decay: float = 0.0


@dataclass
class DataCfg:
    """Dataset configuration."""

    format: str = "jsonl"
    train_path: str = "data/train.jsonl"
    eval_path: Optional[str] = "data/eval.jsonl"
    val_fraction: float = 0.0
    pad_to_max: bool = False
    truncation: bool = True


@dataclass
class TrainCfg:
    """Training loop parameters."""

    seed: int = 42
    deterministic: bool = True
    batch_size: int = 8
    max_epochs: int = 1
    gradient_accumulation: int = 1
    amp_enable: bool = False
    amp_dtype: Optional[str] = None
    eval_every_epochs: int = 1
    metrics_out: str = ".codex/metrics.ndjson"
    log_dir: str = "logs"
    log_formats: Tuple[str, ...] = ("ndjson",)
    log_system_metrics: bool = False
    keep_last_n: Optional[int] = 5


@dataclass
class LogCfg:
    """Logging integrations."""

    tensorboard: bool = False
    tensorboard_dir: str = ".codex/tb"
    wandb_enable: bool = False
    mlflow_enable: bool = False
    mlflow_tracking_uri: Optional[str] = None


@dataclass
class AppConfig:
    """Root structured config for Codex training."""

    model: ModelCfg = field(default_factory=ModelCfg)
    optim: OptimCfg = field(default_factory=OptimCfg)
    data: DataCfg = field(default_factory=DataCfg)
    training: TrainCfg = field(default_factory=TrainCfg)
    logging: LogCfg = field(default_factory=LogCfg)


def register_configs() -> None:
    """Register structured configs with Hydra's ConfigStore."""

    try:
        from hydra.core.config_store import ConfigStore
    except Exception:  # pragma: no cover - hydra optional dependency
        return

    cs = ConfigStore.instance()

    if not cs.exists(name="app"):
        cs.store(name="app", node=AppConfig)
    if not cs.exists(group="experiment", name="debug"):
        cs.store(
            group="experiment",
            name="debug",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=2)),
        )
    if not cs.exists(group="experiment", name="fast"):
        cs.store(
            group="experiment",
            name="fast",
            node=AppConfig(training=TrainCfg(max_epochs=1, batch_size=8)),
        )


__all__ = [
    "AppConfig",
    "register_configs",
    "ModelCfg",
    "OptimCfg",
    "DataCfg",
    "TrainCfg",
    "LogCfg",
]
