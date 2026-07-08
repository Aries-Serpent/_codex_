"""
Test Training Config Module

Test module for training config module.
"""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="numpy required")

from pathlib import Path

from training.config import TrainingConfig


def test_training_config_defaults_validate() -> None:
    cfg = TrainingConfig()
    cfg.validate()
    assert cfg.precision == "fp32", "precision is not valid"


def test_training_config_as_dict_contains_fields() -> None:
    cfg = TrainingConfig(batch_size=16)
    data = cfg.as_dict()
    assert data["batch_size"] == 16, "Data must not be empty"
    assert isinstance(data["dataset_path"], Path)


def test_training_config_from_mapping_coerces_types() -> None:
    cfg = TrainingConfig.from_mapping({"batch_size": "4", "precision": "bf16"})
    assert cfg.batch_size == 4, "batch_size is not valid"
    assert cfg.precision == "bf16", "precision is not valid"


@pytest.mark.parametrize(
    "env_key, env_value, expected",
    [
        ("TRAIN_BATCH_SIZE", "12", 12),
        ("TRAIN_PRECISION", "fp16", "fp16"),
        ("TRAIN_USE_LORA", "true", True),
    ],
)
def test_training_config_from_env(
    monkeypatch, env_key: str, env_value: str, expected: object
) -> None:
    monkeypatch.setenv(env_key, env_value)
    cfg = TrainingConfig.from_env()
    field_name = env_key.removeprefix("TRAIN_").lower()
    assert getattr(cfg, field_name) == expected


def test_training_config_invalid_precision() -> None:
    cfg = TrainingConfig(precision="int8")
    with pytest.raises(ValueError):
        cfg.validate()


def test_training_config_invalid_lora_rank() -> None:
    cfg = TrainingConfig(use_lora=True, lora_r=0)
    with pytest.raises(ValueError):
        cfg.validate()


def test_training_config_replace_validation() -> None:
    cfg = TrainingConfig().replace(batch_size=32)
    assert cfg.batch_size == 32, "batch_size is not valid"


def test_training_config_from_env_unknown_bool(monkeypatch) -> None:
    monkeypatch.setenv("TRAIN_DETERMINISTIC", "maybe")
    with pytest.raises(ValueError):
        TrainingConfig.from_env()
