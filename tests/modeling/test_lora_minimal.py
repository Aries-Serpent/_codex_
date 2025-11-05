"""LoRA minimal unit test (opt-in).

These tests validate basic LoRA configuration and availability
without requiring model downloads or network access.
"""

from __future__ import annotations

import os

import pytest


# Skip all tests unless CODEX_ENABLE_LORA_TEST=1
pytestmark = pytest.mark.skipif(
    os.getenv("CODEX_ENABLE_LORA_TEST") != "1",
    reason="LoRA tests disabled (set CODEX_ENABLE_LORA_TEST=1 to enable)"
)


def test_lora_config_shapes_sanity():
    """Minimal LoRA sanity gate (opt-in).
    
    Validates:
    - peft can be imported
    - LoraConfig can be constructed
    - Config fields match expectations
    
    Does NOT require network/model downloads.
    """
    # Try to import peft
    try:
        from peft import LoraConfig
    except ImportError:
        pytest.skip("peft not installed")
    
    # Create basic LoRA config
    config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Validate config attributes
    assert config.r == 8
    assert config.lora_alpha == 16
    assert config.target_modules == ["q_proj", "v_proj"]
    assert config.lora_dropout == 0.1
    assert config.bias == "none"
    assert config.task_type == "CAUSAL_LM"
    
    # Validate config is serializable
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert "r" in config_dict
    assert "lora_alpha" in config_dict


def test_lora_available():
    """Test that LoRA/PEFT is available for use."""
    try:
        import peft
        
        # Verify key classes are available
        assert hasattr(peft, "LoraConfig")
        assert hasattr(peft, "get_peft_model")
        assert hasattr(peft, "PeftModel")
        
    except ImportError:
        pytest.skip("peft not installed")


def test_lora_config_validation():
    """Test LoRA config parameter validation."""
    try:
        from peft import LoraConfig
    except ImportError:
        pytest.skip("peft not installed")
    
    # Valid config should not raise
    config = LoraConfig(r=16, lora_alpha=32)
    assert config.r == 16
    
    # Test different rank values
    for r in [4, 8, 16, 32, 64]:
        config = LoraConfig(r=r)
        assert config.r == r
    
    # Test alpha scaling
    for alpha in [8, 16, 32]:
        config = LoraConfig(r=8, lora_alpha=alpha)
        assert config.lora_alpha == alpha
