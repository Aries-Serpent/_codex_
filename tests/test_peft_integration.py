import pytest

from codex_ml.models import MiniLM, MiniLMConfig
from codex_ml.peft.peft_adapter import apply_lora

peft = pytest.importorskip("peft")


def test_peft_apply_lora():
    model = MiniLM(MiniLMConfig(vocab_size=10))
    adapted = apply_lora(model, {"r": 2})
    assert hasattr(adapted, "peft_config")
