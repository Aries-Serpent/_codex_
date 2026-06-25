"""
Torch test helpers for detecting stub modules.

Provides utilities to ensure tests skip when PyTorch stub is detected instead of real PyTorch.
Also includes general utilities for handling heavy dependency imports in tests.
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
    if not hasattr(torch_module, "nn"):
        pytest.skip("PyTorch is not fully functional (missing nn module)", allow_module_level=True)

    if not hasattr(torch_module.nn, "Linear"):
        pytest.skip("PyTorch is not fully functional (missing nn.Linear)", allow_module_level=True)

    # Check if it's the stub by looking for IS_CODEX_STUB marker
    if hasattr(torch_module, "IS_CODEX_STUB") and torch_module.IS_CODEX_STUB:
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


def skip_if_missing(module_name: str, feature_name: str = None):
    """
    Skip test if a module is not available.

    Args:
        module_name: Name of the module to check
        feature_name: Optional feature name for better error message

    Raises:
        pytest.skip: If module is not available

    Example:
        >>> skip_if_missing("transformers", "HuggingFace Transformers")
        >>> skip_if_missing("mlflow")
    """
    feature = feature_name or module_name
    try:
        __import__(module_name)
    except ImportError:
        pytest.skip(f"{feature} not available", allow_module_level=True)


def require_module(module_name: str, feature_name: str = None):
    """
    Import and return a module, skip test if not available.

    Args:
        module_name: Name of the module to import
        feature_name: Optional feature name for better error message

    Returns:
        Imported module

    Raises:
        pytest.skip: If module is not available

    Example:
        >>> transformers = require_module("transformers", "HuggingFace Transformers")
        >>> model = transformers.AutoModel.from_pretrained("bert-base-uncased")
    """
    feature = feature_name or module_name
    return pytest.importorskip(module_name, reason=f"{feature} required for tests")


def skip_if_any_missing(*module_names: str):
    """
    Skip test if any of the listed modules are not available.

    Args:
        *module_names: Names of modules to check

    Raises:
        pytest.skip: If any module is not available

    Example:
        >>> skip_if_any_missing("torch", "transformers", "mlflow")
    """
    missing = []
    for module_name in module_names:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)

    if missing:
        pytest.skip(
            f"Required modules not available: {', '.join(missing)}", allow_module_level=True
        )
