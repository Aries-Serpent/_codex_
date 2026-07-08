"""
Test helpers for quantum plugin testing.

Provides utilities for mocking quantum plugins and handling import failures gracefully.
"""

from __future__ import annotations

import importlib.util
import sys
from types import ModuleType
from typing import Any, Optional

import pytest


def create_mock_module(module_name: str, **attributes: Any) -> ModuleType:
    """
    Create a mock module that can be imported.

    Args:
        module_name: Full module path (e.g., 'src.rag.pipelines.chunking')
        **attributes: Attributes to set on the module

    Returns:
        Mock module that behaves like a real module

    Example:
        >>> mock_mod = create_mock_module('src.rag.chunking', process=lambda x: x)
        >>> install_mock_module(mock_mod)
        >>> from rag import chunking
        >>> chunking.process("test")
    """
    # Create a real module object
    module = ModuleType(module_name)
    module.__name__ = module_name
    module.__file__ = f"<mock {module_name}>"
    module.__package__ = ".".join(module_name.split(".")[:-1]) or None

    # Add attributes
    for key, value in attributes.items():
        setattr(module, key, value)

    return module


def install_mock_module(module: ModuleType) -> None:
    """
    Install a mock module into sys.modules.

    Args:
        module: Module object to install

    Example:
        >>> mock_mod = create_mock_module('src.test.module')
        >>> install_mock_module(mock_mod)
        >>> import src.test.module
    """
    # Install module and all parent packages
    parts = module.__name__.split(".")
    for i in range(len(parts)):
        partial_name = ".".join(parts[: i + 1])
        if partial_name not in sys.modules:
            if i < len(parts) - 1:
                # Create parent package
                parent = ModuleType(partial_name)
                parent.__name__ = partial_name
                parent.__file__ = f"<mock {partial_name}>"
                parent.__package__ = ".".join(parts[:i]) or None
                parent.__path__ = []
                sys.modules[partial_name] = parent
            else:
                # Install the actual module
                sys.modules[partial_name] = module


def uninstall_mock_module(module_name: str) -> None:
    """
    Remove a mock module from sys.modules.

    Args:
        module_name: Full module path to remove
    """
    if module_name in sys.modules:
        del sys.modules[module_name]


def skip_if_module_missing(module_path: str, reason: Optional[str] = None) -> None:
    """
    Skip test if module cannot be imported.

    Args:
        module_path: Python import path to check
        reason: Optional reason for skipping

    Raises:
        pytest.skip: If module is not available

    Example:
        >>> skip_if_module_missing('src.rag.pipelines.chunking')
    """
    try:
        spec = importlib.util.find_spec(module_path)
        if spec is None:
            reason = reason or f"Module {module_path} not found"
            pytest.skip(reason)
    except (ImportError, ModuleNotFoundError, ValueError):
        reason = reason or f"Module {module_path} cannot be imported"
        pytest.skip(reason)


def mock_quantum_plugin_imports(plugin_paths: list[str]) -> None:
    """
    Create and install mock modules for quantum plugin paths.

    This is useful for testing quantum plugin behavior without requiring
    actual module implementations.

    Args:
        plugin_paths: List of import paths to mock

    Example:
        >>> mock_quantum_plugin_imports([
        ...     'src.rag.pipelines.chunking',
        ...     'src.rag.pipelines.embedding'
        ... ])
    """
    for path in plugin_paths:
        module = create_mock_module(path)
        install_mock_module(module)


class QuantumPluginTestFixture:
    """
    Test fixture for quantum plugin testing with automatic cleanup.

    Example:
        >>> fixture = QuantumPluginTestFixture()
        >>> fixture.mock_module('src.rag.chunking', process=lambda x: x)
        >>> # Use mocked module in tests
        >>> fixture.cleanup()  # Remove all mocks
    """

    def __init__(self):
        self.mocked_modules: list[str] = []

    def mock_module(self, module_path: str, **attributes: Any) -> ModuleType:
        """Create and install a mock module."""
        module = create_mock_module(module_path, **attributes)
        install_mock_module(module)
        self.mocked_modules.append(module_path)
        return module

    def cleanup(self) -> None:
        """Remove all mocked modules."""
        for module_name in self.mocked_modules:
            uninstall_mock_module(module_name)
        self.mocked_modules.clear()


@pytest.fixture
def quantum_plugin_fixture():
    """Pytest fixture for quantum plugin testing."""
    fixture = QuantumPluginTestFixture()
    yield fixture
    fixture.cleanup()
