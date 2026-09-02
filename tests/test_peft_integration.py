"""
Test Peft Integration

Test module for peft integration.
"""

import sys

import pytest

from codex_ml.models import MiniLM, MiniLMConfig
from codex_ml.peft.peft_adapter import apply_lora

peft = pytest.importorskip("peft")

try:
    import torch as _torch_peft

    _TORCH_312_BUG = sys.version_info >= (3, 12) and _torch_peft.__version__.startswith("2.")
except (ImportError, AttributeError):
    _TORCH_312_BUG = False


@pytest.fixture(autouse=True)
def disable_torch_profiler(monkeypatch):
    """Disable PyTorch profiler to avoid Protocol isinstance issues."""
    try:
        import torch
        import torch.profiler as profiler_module

        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(
                profiler_module, "_record_function_enter", lambda *args, **kwargs: None
            )
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(
                profiler_module, "_record_function_exit", lambda *args, **kwargs: None
            )

        # Force CPU device to avoid meta tensor initialization issues
        torch.set_default_device("cpu")

    except (ImportError, AttributeError):
        _ = None  # PyTorch profiler not available or already disabled


@pytest.mark.skipif(
    _TORCH_312_BUG, reason="PyTorch 2.x isinstance bug with Python 3.12 union types"
)
def test_peft_apply_lora():
    model = MiniLM(MiniLMConfig(vocab_size=10))
    adapted = apply_lora(model, {"r": 2}, lora_alpha=4)
    assert hasattr(adapted, "peft_config")
    assert adapted.peft_config["r"] == 2, "Condition must be true"
    assert adapted.peft_config["lora_alpha"] == 4, "Condition must be true"
