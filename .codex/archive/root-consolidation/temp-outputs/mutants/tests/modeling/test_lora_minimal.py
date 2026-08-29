"""LoRA minimal unit test (opt-in).

These tests validate basic LoRA configuration and availability
without requiring model downloads or network access.

Set RUN_LORA_TESTS=1 to enable these tests.
"""

from __future__ import annotations

import os

import pytest

# Skip all tests unless RUN_LORA_TESTS=1
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LORA_TESTS") != "1",
    reason="LoRA tests disabled (set RUN_LORA_TESTS=1 to enable)",
)


def test_lora_config_shapes_sanity():
    """Minimal LoRA sanity gate (opt-in).

    Validates:
    - peft can be imported
    - LoraConfig can be constructed
    - Config fields match expectations

    Does NOT require network/model downloads.
    """
    LoraConfig = pytest.importorskip("peft").LoraConfig

    # Create basic LoRA config
    config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM",
    )

    # Validate config attributes
    assert config.r == 8, "r is not valid"
    assert config.lora_alpha == 16, "lora_alpha is not valid"
    assert config.target_modules == ["q_proj", "v_proj"]
    assert config.lora_dropout == 0.1, "lora_dropout is not valid"
    assert config.bias == "none", "bias is not valid"
    assert config.task_type == "CAUSAL_LM", "task_type is not valid"

    # Validate config is serializable
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert "r" in config_dict, "Condition must be true"
    assert "lora_alpha" in config_dict, "Condition must be true"


def test_lora_available():
    """Test that LoRA/PEFT is available for use."""
    peft = pytest.importorskip("peft")

    # Verify key classes are available
    assert hasattr(peft, "LoraConfig")
    assert hasattr(peft, "get_peft_model")
    assert hasattr(peft, "PeftModel")


def test_lora_config_validation():
    """Test LoRA config parameter validation."""
    LoraConfig = pytest.importorskip("peft").LoraConfig

    # Valid config should not raise
    config = LoraConfig(r=16, lora_alpha=32)
    assert config.r == 16, "r is not valid"

    # Test different rank values
    for r in [4, 8, 16, 32, 64]:
        config = LoraConfig(r=r)
        assert config.r == r, "r is not valid"

    # Test alpha scaling
    for alpha in [8, 16, 32]:
        config = LoraConfig(r=8, lora_alpha=alpha)
        assert config.lora_alpha == alpha, "lora_alpha is not valid"


def test_lora_test_utils_available():
    """Test that LoRA test utilities are available and functional."""
    import sys
    from pathlib import Path

    # Add models directory to path
    _REPO_ROOT = Path(__file__).parent.parent.parent
    _MODELS_DIR = _REPO_ROOT / "models"
    if str(_MODELS_DIR) not in sys.path:
        sys.path.insert(0, str(_MODELS_DIR))

    try:
        from lora._test_utils import (
            create_mock_lora_config,
            create_mock_tensor,
            get_lora_param_count,
            is_peft_available,
            validate_lora_config_shape,
        )

        # Test utility functions
        assert isinstance(is_peft_available(), bool)

        # Test mock tensor creation
        tensor = create_mock_tensor((2, 3, 4))
        assert tensor.shape == (2, 3, 4)

        # Test parameter count estimation
        params = get_lora_param_count(r=8, d_model=512, n_layers=2)
        assert params > 0, "params must be greater than zero"
        assert params == (512 * 8 + 8 * 512) * 2 * 2, "params is not valid"

        # Test config creation and validation
        if is_peft_available():
            config = create_mock_lora_config(r=16)
            assert config is not None, "config must be initialized"
            assert validate_lora_config_shape(config), "validate_l is not valid"
            assert config.r == 16, "r is not valid"

    except ImportError as e:
        pytest.skip(f"Test utils not available: {e}")
