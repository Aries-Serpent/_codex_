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
from .plugin_registry import (
    calculate_thermodynamic_load_priority as calculate_plugin_priority,
)
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
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result
