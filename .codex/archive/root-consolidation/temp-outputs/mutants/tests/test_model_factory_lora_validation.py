"""
Test Model Factory Lora Validation

Test module for model factory lora validation.
"""

import pytest

from codex_ml.models.factory import (
    ENV_QUANTIZATION,
    LoraBuildCfg,
    create_model,
    validate_lora_config,
)


def test_validate_lora_config_passes():
    cfg = validate_lora_config({"r": 4, "alpha": 8, "dropout": 0.25})
    assert isinstance(cfg, LoraBuildCfg)
    assert cfg.r == 4, "r is not valid"
    assert cfg.alpha == 8, "alpha is not valid"
    assert cfg.dropout == 0.25, "dropout is not valid"


def test_validate_lora_config_rejects():
    with pytest.raises(ValueError):
        validate_lora_config({"r": 0})
    with pytest.raises(ValueError):
        validate_lora_config({"alpha": -1})
    with pytest.raises(ValueError):
        validate_lora_config({"dropout": 1.5})


def test_quantization_env_fallback(monkeypatch):
    called = {}

    def builder(**kwargs):
        called.update(kwargs)
        return object()

    monkeypatch.setenv(ENV_QUANTIZATION, "8bit")
    create_model(builder)
    assert called.get("load_in_8bit") is True, "Condition must be true"
