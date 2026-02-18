"""
Test Peft Integration

Test module for peft integration.
"""

import pytest

from codex_ml.models import MiniLM, MiniLMConfig
from codex_ml.peft.peft_adapter import apply_lora

peft = pytest.importorskip("peft")


@pytest.fixture(autouse=True)
def disable_torch_profiler(monkeypatch):
    """Disable PyTorch profiler to avoid Protocol isinstance issues."""
    try:
        import torch.profiler as profiler_module
        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(profiler_module, "_record_function_enter", lambda *args, **kwargs: None)
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(profiler_module, "_record_function_exit", lambda *args, **kwargs: None)
    except (ImportError, AttributeError):
        pass  # PyTorch profiler not available or already disabled


def test_peft_apply_lora():
    model = MiniLM(MiniLMConfig(vocab_size=10))
    adapted = apply_lora(model, {"r": 2}, lora_alpha=4)
    assert hasattr(adapted, "peft_config")
    assert adapted.peft_config["r"] == 2
    assert adapted.peft_config["lora_alpha"] == 4
