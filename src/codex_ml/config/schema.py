"""Configuration schema for `_codex_`.

This module defines *minimal* dataclasses for core configuration blocks:

- ModelConfig
- TrainingConfig
- DataConfig
- EvalConfig
- CodexConfig (top-level)

The goal is not to freeze the entire config surface, but to provide:

- A typed "spine" for key fields referenced by training / eval loops.
- A validation hook that can be run locally before longer runs.
- A pattern that can coexist with Hydra or other config systems later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ModelConfig:
    """Minimal model configuration.

    Fields are consciously generic; they can be extended as needed.
    """

    model_name: str = "codex-minimal"
    hidden_size: int = 256
    num_layers: int = 4
    dropout: float = 0.1
    dtype: str = "float32"  # e.g. "float16", "bfloat16"


@dataclass
class TrainingConfig:
    """Minimal training configuration."""

    learning_rate: float = 1e-3
    batch_size: int = 8
    max_steps: int = 100
    gradient_accumulation_steps: int = 1
    log_every_n_steps: int = 10
    seed: int = 123


@dataclass
class DataConfig:
    """Minimal data configuration."""

    dataset_name: str = "dummy"
    train_split: str = "train"
    eval_split: str = "validation"
    shuffle: bool = True
    num_workers: int = 0


@dataclass
class EvalConfig:
    """Minimal evaluation configuration."""

    batch_size: int = 8
    split: str = "validation"
    max_batches: Optional[int] = None


@dataclass
class CodexConfig:
    """Top-level configuration container for `_codex_` runs.

    This is intended as a "spine" around which more detailed configs
    can be layered. Unknown keys in the raw dict are preserved in
    `raw` for forward compatibility.
    """

    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    raw: dict[str, Any] = field(default_factory=dict)


def _coerce_model(data: dict[str, Any]) -> ModelConfig:
    return ModelConfig(
        model_name=str(data.get("model_name", "codex-minimal")),
        hidden_size=int(data.get("hidden_size", 256)),
        num_layers=int(data.get("num_layers", 4)),
        dropout=float(data.get("dropout", 0.1)),
        dtype=str(data.get("dtype", "float32")),
    )


def _coerce_training(data: dict[str, Any]) -> TrainingConfig:
    return TrainingConfig(
        learning_rate=float(data.get("learning_rate", 1e-3)),
        batch_size=int(data.get("batch_size", 8)),
        max_steps=int(data.get("max_steps", 100)),
        gradient_accumulation_steps=int(data.get("gradient_accumulation_steps", 1)),
        log_every_n_steps=int(data.get("log_every_n_steps", 10)),
        seed=int(data.get("seed", 123)),
    )


def _coerce_data(data: dict[str, Any]) -> DataConfig:
    return DataConfig(
        dataset_name=str(data.get("dataset_name", "dummy")),
        train_split=str(data.get("train_split", "train")),
        eval_split=str(data.get("eval_split", "validation")),
        shuffle=bool(data.get("shuffle", True)),
        num_workers=int(data.get("num_workers", 0)),
    )


def _coerce_eval(data: dict[str, Any]) -> EvalConfig:
    return EvalConfig(
        batch_size=int(data.get("batch_size", 8)),
        split=str(data.get("split", "validation")),
        max_batches=(None if data.get("max_batches") is None else int(data["max_batches"])),
    )


class ConfigValidationError(ValueError):
    """Raised when config validation fails."""


def from_dict(raw: dict[str, Any]) -> CodexConfig:
    """Construct CodexConfig from a raw dict (e.g. parsed YAML).

    Unknown keys are preserved in the `raw` field.
    """

    if not isinstance(raw, dict):
        raise ConfigValidationError("Top-level config must be a mapping")

    model_data = raw.get("model") or {}
    training_data = raw.get("training") or {}
    data_data = raw.get("data") or {}
    eval_data = raw.get("eval") or {}

    if not isinstance(model_data, dict):
        raise ConfigValidationError("`model` section must be a mapping")
    if not isinstance(training_data, dict):
        raise ConfigValidationError("`training` section must be a mapping")
    if not isinstance(data_data, dict):
        raise ConfigValidationError("`data` section must be a mapping")
    if not isinstance(eval_data, dict):
        raise ConfigValidationError("`eval` section must be a mapping")

    model = _coerce_model(model_data)
    training = _coerce_training(training_data)
    data_cfg = _coerce_data(data_data)
    eval_cfg = _coerce_eval(eval_data)

    return CodexConfig(
        model=model,
        training=training,
        data=data_cfg,
        eval=eval_cfg,
        raw=raw,
    )
