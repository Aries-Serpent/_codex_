"""
Test Peft Adapter

Test module for peft adapter.
"""

from typing import Any

import pytest

from codex_ml.peft.peft_adapter import apply_lora
from tests.helpers.optional_dependencies import import_optional_dependency

torch = import_optional_dependency("torch", allow_stub=False)
nn = torch.nn


class DummyModel:
    def parameters(self):
        return []


def test_apply_lora_merges_config_without_peft(monkeypatch):
    monkeypatch.setattr("codex_ml.peft.peft_adapter.get_peft_model", None)
    model = nn.Linear(4, 4)
    patched = apply_lora(model, {"r": 2, "bias": "all"}, lora_alpha=32)
    assert patched is model, "patched is not valid"
    monkeypatch.setattr("codex_ml.peft.peft_adapter.get_peft_model", None)
    model = nn.Linear(4, 4)
    patched = apply_lora(model, {"r": 2}, r=4)
    assert patched.peft_config["r"] == 4, "Condition must be true"
    assert patched.peft_config["task_type"] == "CAUSAL_LM", "Condition must be true"


def test_apply_lora_task_type_and_control_keys(monkeypatch):
    captured: list[tuple[str, dict[str, Any]]] = []

    class DummyConfig:
        def __init__(self, *, task_type: str, **kwargs: Any) -> None:
            captured.append((task_type, dict(kwargs)))

    def fake_get_peft_model(model: nn.Module, cfg: DummyConfig) -> nn.Module:
        return model

    monkeypatch.setattr("codex_ml.peft.peft_adapter.LoraConfig", DummyConfig)
    monkeypatch.setattr("codex_ml.peft.peft_adapter.get_peft_model", fake_get_peft_model)

    base = nn.Linear(2, 2)
    adapted = apply_lora(base, {"enabled": True, "r": 4})
    assert captured[0][0] == "CAUSAL_LM", "Condition must be true"
    assert "enabled" not in captured[0][1], "Condition must be true"
    assert adapted.peft_config["task_type"] == "CAUSAL_LM", "Condition must be true"

    fresh = nn.Linear(2, 2)
    override = apply_lora(fresh, {"enabled": True}, task_type="SEQ2SEQ_LM", lora_alpha=48)
    assert captured[1][0] == "SEQ2SEQ_LM", "Condition must be true"
    assert override.peft_config["task_type"] == "SEQ2SEQ_LM", "Condition must be true"
    assert captured[1][1]["lora_alpha"] == 48, "Condition must be true"


def test_apply_lora_with_peft():
    pytest.importorskip("peft")
    model = nn.Linear(4, 4)
    patched = apply_lora(model, lora_dropout=0.1)
    assert hasattr(patched, "peft_config")
    assert patched.peft_config["lora_dropout"] == 0.1, "Condition must be true"
