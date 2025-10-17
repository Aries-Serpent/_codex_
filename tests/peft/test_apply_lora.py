"""Tests for the graceful LoRA fallback when ``peft`` is unavailable."""

from __future__ import annotations

import pytest

from codex_ml.peft import peft_adapter

if peft_adapter.LoraConfig is not None and peft_adapter.get_peft_model is not None:
    pytest.skip("peft is installed, skip fallback test", allow_module_level=True)


class DummyModel:
    pass


def test_apply_lora_attaches_config() -> None:
    dummy = DummyModel()
    out = peft_adapter.apply_lora(dummy, {"r": 12})
    assert out is dummy
    assert hasattr(out, "peft_config"), "peft_config not attached"
    cfg = out.peft_config
    assert isinstance(cfg, dict), "peft_config is not a dict"
    assert cfg.get("r") == 12, "LoRA config override for 'r' was not applied"
    assert "lora_alpha" in cfg and "bias" in cfg, "Missing expected keys in peft_config"
