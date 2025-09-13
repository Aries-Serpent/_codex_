"""
Minimal Pydantic-based config schema and validation helpers.
Extend/replace with rich Hydra Structured Configs as needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, PositiveInt, field_validator


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
