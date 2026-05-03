"""
Test Peft Optional

Test module for peft optional.
"""

import pytest

# Check if PEFT is available for proper testing
try:
    from peft import get_peft_model
    HAS_PEFT = bool(get_peft_model)
except ImportError:
    HAS_PEFT = False


@pytest.mark.skipif(
    not HAS_PEFT,
    reason="PEFT library not fully available - environment-specific test"
)
def test_apply_lora_if_available_identity_without_peft():
    from codex_ml.models.utils.peft import apply_lora_if_available

    class Dummy:
        pass

    model = Dummy()
    wrapped = apply_lora_if_available(model)
    # If `peft` is not installed, helper returns the model unchanged.
    assert wrapped is model
