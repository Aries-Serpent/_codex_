"""
Test Validate Config

Test module for validate config.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
from pydantic import ValidationError

from codex_ml.config_schema import (
    LoraConfig,
    TrainConfig,
    validate_config,
)


def test_validate_config_invalid() -> None:
    bad_cfg = {"train": {"batch_size": 1, "lr": 0.1}, "tokenizer": {"vocab_size": 64}}
    with pytest.raises(ValueError):
        validate_config(bad_cfg)


def test_train_config_defaults() -> None:
    cfg = validate_config({})
    assert isinstance(cfg, TrainConfig)
    assert cfg.seed == 42, "seed is not valid"
    assert cfg.device == "cpu", "device is not valid"
    assert cfg.grad_accum == 1, "grad_accum is not valid"


def test_train_config_nested_training_block() -> None:
    payload = {
        "training": {
            "model_name": "custom",
            "epochs": 3,
            "checkpoint_keep": 2,
        }
    }
    cfg = validate_config(payload)
    assert cfg.model_name == "custom", "model_name is not valid"
    assert cfg.epochs == 3, "epochs is not valid"
    assert cfg.checkpoint_keep == 2, "checkpoint_keep is not valid"


def test_train_config_lora_parsing() -> None:
    cfg = validate_config({"lora": {"enable": True, "r": 12}})
    assert cfg.lora is not None, "lora must be initialized"
    assert isinstance(cfg.lora, LoraConfig)
    assert cfg.lora.enable is True, "enable is not valid"
    assert cfg.lora.r == 12, "r is not valid"


def test_train_config_eval_split_bounds() -> None:
    with pytest.raises(ValidationError):
        validate_config({"eval_split": 1.5})
