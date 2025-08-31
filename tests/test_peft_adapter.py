import pytest
import torch.nn as nn

from src.codex_ml.peft.peft_adapter import apply_lora


def test_apply_lora_merges_config_without_peft(monkeypatch):
    monkeypatch.setattr("src.codex_ml.peft.peft_adapter.get_peft_model", None)
    model = nn.Linear(4, 4)
    patched = apply_lora(model, {"r": 2}, lora_alpha=32)
    assert patched is model
    assert patched.peft_config == {
        "r": 2,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "bias": "none",
    }


def test_apply_lora_with_peft():
    pytest.importorskip("peft")
    model = nn.Linear(4, 4)
    patched = apply_lora(model, lora_dropout=0.1)
    assert hasattr(patched, "peft_config")
    assert patched.peft_config["lora_dropout"] == 0.1
