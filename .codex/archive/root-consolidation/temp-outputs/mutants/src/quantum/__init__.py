"""
Quantum-inspired plugin orchestration system for _codex_.

This package provides lazy loading, thermodynamic scheduling, and wave function
testing capabilities using principles from quantum mechanics and thermodynamics.

Key Components:
    - QuantumPluginRegistry: Lazy plugin loading with dependency management
    - QuantumTestSuite: Wave function-based test execution
    - ThermodynamicOrchestrator: Energy-based task scheduling

Example:
    >>> from src.quantum import QuantumPluginRegistry, QuantumPlugin
    >>> registry = QuantumPluginRegistry()
    >>> plugin = QuantumPlugin(name="core", import_path="src.agent.core")
    >>> registry.register(plugin)
    >>> module = registry.load_with_dependencies("core")
"""

from __future__ import annotations

from .orchestrator import (
    TaskPriority,
    ThermodynamicOrchestrator,
    ThermodynamicTask,
    calculate_thermodynamic_load_priority,
)
from .plugin_registry import (
    PluginState,
    QuantumPlugin,
    QuantumPluginRegistry,
)
from .plugin_registry import calculate_thermodynamic_load_priority as calculate_plugin_priority
from .testing import (
    QuantumTest,
    QuantumTestSuite,
    TestState,
)

__all__ = [
    # Plugin Registry
    "QuantumPlugin",
    "QuantumPluginRegistry",
    "PluginState",
    "calculate_plugin_priority",
    # Testing
    "QuantumTest",
    "QuantumTestSuite",
    "TestState",
    # Orchestration
    "ThermodynamicTask",
    "ThermodynamicOrchestrator",
    "TaskPriority",
    "calculate_thermodynamic_load_priority",
]

__version__ = "1.0.0"
