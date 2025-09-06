"""Lightweight Pydantic schemas for Codex configuration.

These models validate critical sections of the Hydra config at runtime to
catch misconfiguration early. Only a subset of fields are modelled to avoid
over‑constraining experimentation.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field, PositiveInt, ValidationError


class TrainingCfg(BaseModel):
    """Schema for the ``train`` section."""

    batch_size: PositiveInt = Field(..., description="Per-device batch size")
    lr: float = Field(..., gt=0, le=1.0, description="Learning rate in (0,1]")


class TokenizerCfg(BaseModel):
    """Schema for the ``tokenizer`` section."""

    vocab_size: PositiveInt = Field(32000, ge=128, description="Vocabulary size")


class ExperimentCfg(BaseModel):
    """Schema for experiment-level parameters."""

    train_ratio: float = Field(0.9, gt=0.0, lt=1.0)


def validate_config(cfg_dict: Dict[str, Any]) -> None:
    """Validate a composed Hydra config.

    Parameters
    ----------
    cfg_dict:
        The configuration as a plain dictionary.

    Raises
    ------
    ValueError
        If validation fails.
    """

    try:
        if "train" in cfg_dict:
            TrainingCfg(**cfg_dict["train"])
        if "tokenizer" in cfg_dict:
            TokenizerCfg(**cfg_dict["tokenizer"])
        if "experiment" in cfg_dict:
            ExperimentCfg(**cfg_dict["experiment"])
    except ValidationError as exc:  # pragma: no cover - exercised in tests
        raise ValueError(str(exc)) from exc
