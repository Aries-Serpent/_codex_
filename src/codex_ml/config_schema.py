"""
Minimal Pydantic-based config schema and validation helpers.
Extend/replace with rich Hydra Structured Configs as needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    ValidationError,
    field_validator,
)

from codex_ml.utils.yaml_support import MissingPyYAMLError, safe_load


class LoraConfig(BaseModel):
    """Subset of LoRA hyper-parameters accepted by the training stack."""

    model_config = ConfigDict(extra="forbid")

    enable: bool = False
    r: PositiveInt = Field(default=8, description="LoRA rank")
    lora_alpha: PositiveInt = Field(default=16, description="LoRA alpha scaling")
    lora_dropout: float = Field(default=0.05, ge=0.0, le=1.0)
    task_type: str = Field(default="CAUSAL_LM")


class TrainConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    config_version: int = Field(default=1, ge=1)
    model_name: str = Field(default="tiny", description="Model identifier or profile name.")
    learning_rate: float = Field(default=1e-3, gt=0.0)
    epochs: PositiveInt = Field(default=1)
    max_samples: PositiveInt = Field(default=32)
    data_path: Optional[str] = Field(
        default=None, description="Optional local dataset path (offline safe)."
    )
    seed: int = Field(default=42, description="Random seed for reproducible runs")
    device: str = Field(default="cpu", description="Preferred training device")
    dtype: str = Field(default="float32", description="Torch dtype for model weights")
    grad_accum: PositiveInt = Field(default=1, description="Gradient accumulation steps")
    lora: Optional[LoraConfig] = Field(default=None, description="Optional LoRA overrides")
    eval_split: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of data reserved for evaluation",
    )
    checkpoint_keep: PositiveInt = Field(default=1, description="Number of checkpoints to keep")
    bf16_require_capability: bool = Field(
        default=False,
        description="When true and dtype requests bf16, assert bf16 capability and fail fast.",
    )
    dataset_cast_policy: Optional[str] = Field(
        default=None,
        description="Optional dataset casting policy: 'to_model_dtype', 'to_fp32', or None",
    )

    @field_validator("data_path")
    @classmethod
    def _path_exists_if_provided(cls, v):
        if v:
            p = Path(v)
            if not p.exists():
                raise ValueError(f"data_path does not exist: {p}")
        return v


def load_yaml(path: str | Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return safe_load(f) or {}
    except MissingPyYAMLError as exc:
        raise RuntimeError(
            'PyYAML is required to validate configuration files. Install it via ``pip install "PyYAML>=6.0"`` '
            f"before loading {path}."
        ) from exc


def _as_train_config_payload(cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Return a mapping compatible with :class:`TrainConfig`.

    Historical configs often nest training options under a top-level ``training``
    key.  This helper preserves backward compatibility by extracting that block
    when present while still permitting flattened dictionaries.
    """

    if "training" in cfg and isinstance(cfg["training"], Mapping):
        return dict(cfg["training"])
    return dict(cfg)


def validate_config_file(path: str | Path) -> TrainConfig:
    data = load_yaml(path)
    return TrainConfig.model_validate(_as_train_config_payload(data))


def validate_config_dict(cfg: Mapping[str, Any]) -> TrainConfig:
    """Validate a config provided as a dictionary-like object."""

    return TrainConfig.model_validate(_as_train_config_payload(cfg))


# --- Back-compat shim -------------------------------------------------------
# Existing callers import `validate_config` and may pass either a mapping or a path.


def validate_config(
    cfg: Union[str, Path, Mapping[str, Any]], *args: Any, **kwargs: Any
) -> TrainConfig:
    """Backward-compatible wrapper around the new validators."""
    if isinstance(cfg, Mapping):
        return validate_config_dict(cfg)
    # treat as path-like
    return validate_config_file(Path(cfg))


__all__ = [
    "LoraConfig",
    "TrainConfig",
    "ValidationError",
    "load_yaml",
    "validate_config_file",
    "validate_config_dict",
    "validate_config",
]
