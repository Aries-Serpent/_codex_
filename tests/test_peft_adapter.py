import torch.nn as nn
import pytest

from src.codex_ml.peft.peft_adapter import apply_lora


def test_apply_lora_noop_without_peft():
    model = nn.Linear(4, 4)
    patched = apply_lora(model)
    assert patched is model


def test_apply_lora_with_peft():
    peft = pytest.importorskip("peft")
    model = nn.Linear(4, 4)
    patched = apply_lora(model)
    assert patched is not None
    assert hasattr(patched, "peft_config")
