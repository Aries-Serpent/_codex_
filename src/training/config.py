"""Dataclass-driven configuration for ``training.engine_hf_trainer``.

This module provides a lightweight configuration object with validation and
helper constructors. It avoids depending on Hydra/YAML so that simple scripts
can configure ``run_hf_trainer`` using environment variables or small JSON
files.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, fields
from pathlib import Path
from types import UnionType
from typing import (
    Any,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

_VALID_PRECISIONS = {"fp32", "fp16", "bf16"}


def _to_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on", "enable", "enabled"}:
        return True
    if lowered in {"0", "false", "no", "off", "disable", "disabled"}:
        return False
    raise ValueError(f"Cannot coerce boolean from '{value}'")


def _resolve_target_type(annotation: Any, current: Any) -> type[Any] | None:
    origin = get_origin(annotation)
    if origin is None:
        if isinstance(annotation, str):
            lookup = {
                "int": int,
                "float": float,
                "bool": bool,
                "Path": Path,
                "Optional[int]": int,
                "Optional[float]": float,
                "Optional[bool]": bool,
                "Optional[Path]": Path,
            }
            resolved = lookup.get(annotation)
            if resolved is not None:
                return resolved
            if "|" in annotation:
                parts = [part.strip() for part in annotation.split("|")]
                non_none = [part for part in parts if part not in {"None", "NoneType"}]
                if len(non_none) == 1:
                    return lookup.get(non_none[0])
        if annotation is Any:
            return type(current) if current is not None else str
        if annotation is None:
            return None
        return annotation
    if origin in {list, tuple, set, frozenset}:  # pragma: no cover - not used today
        return origin
    if origin in {Union, UnionType}:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if not args:
            return None
        return _resolve_target_type(args[0], current)
    return type(current) if current is not None else str


def _coerce_value(value: Any, annotation: Any, current: Any) -> Any:
    if isinstance(value, str):
        if isinstance(current, bool):
            return _to_bool(value)
        if isinstance(current, int):
            return int(value)
        if isinstance(current, float):
            return float(value)
        if isinstance(current, Path):
            return Path(value)
    if isinstance(value, (int, float)) and annotation in {int, float}:
        return annotation(value)
    if isinstance(value, bool) and annotation is bool:
        return value
    if isinstance(value, Path) and annotation in {Path, str | Path}:
        return value
    if isinstance(value, str):
        target = _resolve_target_type(annotation, current)
        if target in {str, None}:
            return value
        if target is Path:
            return Path(value)
        if target in {int, "int"}:
            return int(value)
        if target in {float, "float"}:
            return float(value)
        if target in {bool, "bool"}:
            return _to_bool(value)
    return value


@dataclass
class TrainingConfig:
    """Configuration for ``run_hf_trainer``.

    Fields intentionally mirror a subset of the HF trainer arguments along with
    Codex-specific toggles.
    """

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: str | None = None
    dataset_path: Path = Path("data/train.jsonl")
    eval_dataset_path: Path | None = None
    output_dir: Path = Path("artifacts/hf_trainer")
    batch_size: int = 8
    eval_batch_size: int = 8
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    max_seq_length: int = 256
    gradient_accumulation_steps: int = 1
    precision: str = "fp32"
    seed: int = 42
    deterministic: bool = True
    val_split: float = 0.0
    mlflow_tracking_uri: str | None = None
    dataset_version: str | None = None
    dataset_hash: str | None = None
    use_lora: bool = False
    lora_r: int | None = None
    lora_alpha: float | None = None
    lora_dropout: float | None = None
    lora_task_type: str | None = None

    def validate(self) -> None:
        """Validate numeric and categorical constraints."""

        errors: list[str] = []
        if self.batch_size < 1:
            errors.append("batch_size must be >= 1")
        if self.eval_batch_size < 1:
            errors.append("eval_batch_size must be >= 1")
        if self.learning_rate <= 0:
            errors.append("learning_rate must be > 0")
        if self.num_train_epochs < 0:
            errors.append("num_train_epochs must be >= 0")
        if self.gradient_accumulation_steps < 1:
            errors.append("gradient_accumulation_steps must be >= 1")
        if self.precision not in _VALID_PRECISIONS:
            errors.append(f"precision must be one of {sorted(_VALID_PRECISIONS)}")
        if not (0 <= self.val_split < 1 or self.val_split == 0):
            errors.append("val_split must be in the range [0, 1)")
        if not (0 <= self.seed < 2**32):
            errors.append("seed must be in [0, 2**32)")
        if self.use_lora and self.lora_r is not None and self.lora_r <= 0:
            errors.append("lora_r must be positive when use_lora is enabled")
        if errors:
            raise ValueError("; ".join(errors))

    def as_dict(self) -> dict[str, Any]:
        """Return a ``dict`` copy of the configuration."""

        return {field.name: getattr(self, field.name) for field in fields(self)}

    def replace(self, **updates: Any) -> TrainingConfig:
        """Return a new config with ``updates`` applied."""

        data = self.as_dict()
        data.update(updates)
        cfg = TrainingConfig(**data)
        cfg.validate()
        return cfg

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> TrainingConfig:
        """Build a config from a mapping, coercing values when possible."""

        base = cls()
        type_hints = get_type_hints(cls)
        data: MutableMapping[str, Any] = {
            field.name: getattr(base, field.name) for field in fields(cls)
        }
        for field in fields(cls):
            if field.name not in mapping:
                continue
            raw = mapping[field.name]
            annotation = type_hints.get(field.name, field.type)
            data[field.name] = _coerce_value(raw, annotation, data[field.name])
        cfg = cls(**data)
        cfg.validate()
        return cfg

    @classmethod
    def from_env(cls, prefix: str = "TRAIN_") -> TrainingConfig:
        """Construct a config from environment variables."""

        base = cls()
        type_hints = get_type_hints(cls)
        data: MutableMapping[str, Any] = base.as_dict()
        for field in fields(cls):
            env_name = f"{prefix}{field.name}".upper()
            if env_name not in os.environ:
                continue
            raw = os.environ[env_name]
            annotation = type_hints.get(field.name, field.type)
            data[field.name] = _coerce_value(raw, annotation, data[field.name])
        cfg = cls(**data)
        cfg.validate()
        return cfg


__all__ = ["TrainingConfig"]
