"""
Torch test helpers for detecting stub modules.

Provides utilities to ensure tests skip when PyTorch stub is detected instead of real PyTorch.
"""

import pytest


def skip_if_torch_stub(torch_module):
    """
    Skip test if torch is just a stub module (not fully functional).
    
    Args:
        torch_module: The torch module returned from pytest.importorskip("torch")
        
    Raises:
        pytest.skip: If torch is detected to be a stub module
        
    Example:
        >>> torch = pytest.importorskip("torch")
        >>> skip_if_torch_stub(torch)
    """
    # Check if torch has essential attributes
    if not hasattr(torch_module, 'nn'):
        pytest.skip("PyTorch is not fully functional (missing nn module)", allow_module_level=True)
    
    if not hasattr(torch_module.nn, 'Linear'):
        pytest.skip("PyTorch is not fully functional (missing nn.Linear)", allow_module_level=True)
    
    # Check if it's the stub by looking for IS_CODEX_STUB marker
    if hasattr(torch_module, 'IS_CODEX_STUB') and torch_module.IS_CODEX_STUB:
        pytest.skip("PyTorch stub module detected", allow_module_level=True)


def require_torch():
    """
    Import and validate torch, skip if not available or stub.
    
    Returns:
        torch module if available and functional
        
    Raises:
        pytest.skip: If torch not available or is stub
        
    Example:
        >>> torch = require_torch()
        >>> model = torch.nn.Linear(10, 5)
    """
    torch = pytest.importorskip("torch", reason="PyTorch required for tests")
    skip_if_torch_stub(torch)
    return torch
