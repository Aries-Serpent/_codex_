"""Test utilities for LoRA/PEFT testing without network access.

Provides helper functions for creating mock tensors and configurations
for local-only LoRA testing.
"""
from __future__ import annotations

import os
from typing import Any


def is_lora_testing_enabled() -> bool:
    """Check if LoRA testing is enabled via environment variable.
    
    Returns:
        True if RUN_LORA_TESTS=1, False otherwise
    """
    return os.getenv("RUN_LORA_TESTS") == "1"


def is_peft_available() -> bool:
    """Check if peft library is importable.
    
    Returns:
        True if peft can be imported, False otherwise
    """
    try:
        import peft  # noqa: F401
        return True
    except ImportError:
        return False


def create_mock_lora_config(**kwargs) -> Any:
    """Create a mock LoRA configuration for testing.
    
    Args:
        **kwargs: Override default config parameters
        
    Returns:
        LoraConfig instance if peft available, None otherwise
        
    Example:
        >>> config = create_mock_lora_config(r=16, lora_alpha=32)
        >>> assert config.r == 16
    """
    if not is_peft_available():
        return None
    
    from peft import LoraConfig
    
    # Default minimal config
    defaults = {
        "r": 8,
        "lora_alpha": 16,
        "target_modules": ["q_proj", "v_proj"],
        "lora_dropout": 0.0,  # No dropout for deterministic tests
        "bias": "none",
        "task_type": "CAUSAL_LM",
    }
    
    # Override with provided kwargs
    defaults.update(kwargs)
    
    return LoraConfig(**defaults)


def create_mock_tensor(shape: tuple[int, ...], fill_value: float = 0.0) -> Any:
    """Create a mock tensor for shape testing (no PyTorch required).
    
    Args:
        shape: Tensor shape
        fill_value: Value to fill tensor with
        
    Returns:
        Simple object with shape attribute for testing
        
    Example:
        >>> tensor = create_mock_tensor((2, 3, 4))
        >>> assert tensor.shape == (2, 3, 4)
    """
    class MockTensor:
        def __init__(self, shape: tuple[int, ...], fill_value: float = 0.0):
            self.shape = shape
            self.fill_value = fill_value
            
        def __repr__(self) -> str:
            return f"MockTensor(shape={self.shape}, fill={self.fill_value})"
    
    return MockTensor(shape, fill_value)


def validate_lora_config_shape(config: Any) -> bool:
    """Validate that LoRA config has expected shape parameters.
    
    Args:
        config: LoraConfig instance
        
    Returns:
        True if config has valid shape parameters
        
    Example:
        >>> config = create_mock_lora_config(r=8)
        >>> assert validate_lora_config_shape(config)
    """
    if config is None:
        return False
    
    # Check required attributes
    required_attrs = ["r", "lora_alpha", "lora_dropout"]
    for attr in required_attrs:
        if not hasattr(config, attr):
            return False
    
    # Validate r (rank) is positive
    if config.r <= 0:
        return False
    
    # Validate lora_alpha is positive
    if config.lora_alpha <= 0:
        return False
    
    # Validate dropout is in [0, 1]
    if not (0.0 <= config.lora_dropout <= 1.0):
        return False
    
    return True


def get_lora_param_count(r: int, d_model: int, n_layers: int = 1) -> int:
    """Estimate parameter count for LoRA adapter.
    
    Args:
        r: LoRA rank
        d_model: Model dimension
        n_layers: Number of layers (default: 1)
        
    Returns:
        Estimated parameter count
        
    Example:
        >>> params = get_lora_param_count(r=8, d_model=512, n_layers=12)
        >>> assert params > 0
    """
    # LoRA adds two matrices: A (d_model x r) and B (r x d_model) per module
    # Typical setup has 2 modules (q_proj, v_proj) per layer
    params_per_module = (d_model * r) + (r * d_model)
    modules_per_layer = 2  # q_proj, v_proj
    return params_per_module * modules_per_layer * n_layers
