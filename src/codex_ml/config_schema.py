"""
Minimal Pydantic-based config schema and validation helpers.
Extend/replace with rich Hydra Structured Configs as needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

import yaml
from pydantic import BaseModel, Field, PositiveInt, ValidationError, field_validator


class TrainConfig(BaseModel):
    model_name: str = Field(default="tiny", description="Model identifier or profile name.")
    learning_rate: float = Field(default=1e-3, gt=0.0)
    epochs: PositiveInt = Field(default=1)
    max_samples: PositiveInt = Field(default=32)
    data_path: Optional[str] = Field(
        default=None, description="Optional local dataset path (offline safe)."
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
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_config_file(path: str | Path) -> TrainConfig:
    data = load_yaml(path)
    return TrainConfig.model_validate(data)


def validate_config_dict(cfg: Mapping[str, Any]) -> TrainConfig:
    """Validate a config provided as a dictionary-like object."""
    return TrainConfig.model_validate(dict(cfg))


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
    "TrainConfig",
    "ValidationError",
    "load_yaml",
    "validate_config_file",
    "validate_config_dict",
    "validate_config",
]
