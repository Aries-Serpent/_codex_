"""
Quantum-inspired lazy plugin loading with superposition states.

Cross-references:
    - src/codex_ml/plugins/loader.py
    - agents/advanced_physics_calculators.py
    - src/codex/ast/graph.py:DependencyGraph
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Quantum-inspired plugin states."""

    SUPERPOSITION = "superposition"  # Lazy - not yet loaded
    COLLAPSED = "collapsed"  # Eager - fully loaded
    ENTANGLED = "entangled"  # Dependent on other plugins
    DECOHERENT = "decoherent"  # Load failed, unusable


@dataclass
class QuantumPlugin:
    """
    Plugin with quantum-inspired loading behavior.

    Principles Applied:
        - Superposition: Plugin exists in unloaded/loaded states simultaneously
        - Wave Function Collapse: Loading triggers state collapse
        - Entanglement: Dependencies create quantum correlations
        - Energy Minimization: Load only when energy cost is justified

    Attributes:
        name: Plugin identifier
        import_path: Python import path (e.g., "src.agent.core")
        state: Current quantum state
        dependencies: List of plugin names this depends on
        energy_cost: Computational cost to load (affects priority)
        coherence_time: Time before auto-unload (seconds)

    Example:
        >>> plugin = QuantumPlugin(
        ...     name="core",
        ...     import_path="src.agent.core",
        ...     energy_cost=0.5
        ... )
        >>> module = plugin.observe()  # Collapse wave function
    """

    name: str
    import_path: str
    state: PluginState = PluginState.SUPERPOSITION
    _module: Optional[Any] = field(default=None, repr=False)
    dependencies: list[str] = field(default_factory=list)
    energy_cost: float = 1.0
    coherence_time: float = 3600.0

    def observe(self) -> Any:
        """
        Collapse wave function by loading the plugin.

        Physics: Wave function collapse upon measurement.

        Returns:
            Loaded module

        Raises:
            ImportError: If plugin cannot be loaded
        """
        if self.state == PluginState.COLLAPSED and self._module is not None:
            return self._module

        if self.state == PluginState.DECOHERENT:
            raise ImportError(f"Plugin {self.name} is decoherent (failed)")

        try:
            # Use existing safe_call from codebase
            from src.common.error_handling import safe_call

            spec = importlib.util.find_spec(self.import_path)
            if spec is None:
                self.state = PluginState.DECOHERENT
                raise ImportError(f"Cannot find spec for {self.import_path}")

            module = safe_call(
                importlib.util.module_from_spec,
                spec,
                operation_name=f"Load plugin {self.name}",
                default_return=None,
            )

            if module is None:
                self.state = PluginState.DECOHERENT
                raise ImportError(f"Failed to create module for {self.name}")

            safe_call(
                spec.loader.exec_module,
                module,
                operation_name=f"Execute plugin {self.name}",
                default_return=None,
            )

            self._module = module
            self.state = PluginState.COLLAPSED
            logger.info(f"✓ Plugin '{self.name}' wave function collapsed successfully")

            return self._module

        except Exception as exc:
            self.state = PluginState.DECOHERENT
            logger.error(f"Plugin '{self.name}' decoherence: {exc}")
            raise

    def get_amplitude(self) -> float:
        """
        Calculate quantum amplitude (probability of successful load).

        Physics: |ψ|² gives probability.

        Returns:
            Probability between 0.0 and 1.0
        """
        if self.state == PluginState.COLLAPSED:
            return 1.0
        elif self.state == PluginState.DECOHERENT:
            return 0.0
        else:
            # Base probability modified by energy cost
            # Lower energy cost = higher probability
            return max(0.1, 1.0 / (1.0 + self.energy_cost))


@dataclass
class QuantumPluginRegistry:
    """
    Plugin registry with entanglement and coherence management.

    Cross-references:
        - src/codex_ml/plugins/programmatic.py:PluginRegistry
        - src/codex/ast/graph.py:DependencyGraph

    Example:
        >>> registry = QuantumPluginRegistry()
        >>> plugin = QuantumPlugin(name="core", import_path="src.agent.core")
        >>> registry.register(plugin)
        >>> module = registry.load_with_dependencies("core")
    """

    plugins: dict[str, QuantumPlugin] = field(default_factory=dict)
    dependency_graph: Optional[Any] = None

    def __post_init__(self):
        """Initialize dependency graph for entanglement tracking."""
        from src.codex.ast.graph import DependencyGraph

        self.dependency_graph = DependencyGraph()

    def register(self, plugin: QuantumPlugin) -> None:
        """
        Register plugin and build entanglement graph.

        Args:
            plugin: Plugin to register
        """
        self.plugins[plugin.name] = plugin
        self.dependency_graph.add_node(plugin.name, {"plugin": plugin})

        for dep in plugin.dependencies:
            self.dependency_graph.add_edge(plugin.name, dep)
            # Mark as entangled
            if plugin.name in self.plugins:
                self.plugins[plugin.name].state = PluginState.ENTANGLED

    def get_entangled_plugins(self, plugin_name: str) -> set[str]:
        """
        Get all plugins entangled with the given plugin.

        Physics: Quantum entanglement - measuring one affects others.

        Args:
            plugin_name: Name of plugin to check

        Returns:
            Set of entangled plugin names
        """
        return self.dependency_graph.get_transitive_deps(plugin_name)

    def load_with_dependencies(self, plugin_name: str) -> Any:
        """
        Load plugin and all entangled dependencies.

        Respects topological order to prevent circular loading.

        Args:
            plugin_name: Name of plugin to load

        Returns:
            Loaded plugin module

        Raises:
            KeyError: If plugin not registered
        """
        if plugin_name not in self.plugins:
            raise KeyError(f"Plugin '{plugin_name}' not registered")

        # Get load order using topological sort
        try:
            load_order = self.dependency_graph.topological_sort()
        except Exception:
            # Fallback: just load the plugin
            load_order = [plugin_name]

        # Filter to only required plugins
        required_plugins = {plugin_name} | self.get_entangled_plugins(plugin_name)
        ordered_required = [p for p in load_order if p in required_plugins]

        loaded_modules = {}
        for p_name in ordered_required:
            if p_name in self.plugins:
                plugin = self.plugins[p_name]
                try:
                    loaded_modules[p_name] = plugin.observe()
                except Exception as exc:
                    logger.warning(f"Failed to load dependency '{p_name}': {exc}")

        return loaded_modules.get(plugin_name)


def calculate_thermodynamic_load_priority(
    plugins: list[QuantumPlugin], current_temperature: float = 1.0
) -> list[tuple[str, float]]:
    """
    Calculate plugin load priority using thermodynamic principles.

    Physics: Boltzmann distribution for energy states.
    Cross-reference: agents/advanced_physics_calculators.py

    Priority = exp(-Energy / kT) where:
        - Energy = plugin load cost
        - k = Boltzmann constant (normalized)
        - T = system temperature (load pressure)

    Args:
        plugins: List of plugins to prioritize
        current_temperature: System temperature (load pressure)

    Returns:
        List of (plugin_name, priority) tuples sorted by priority
    """
    import math

    k_boltzmann = 1.0  # Normalized
    priorities = []

    for plugin in plugins:
        # Boltzmann probability
        priority = math.exp(-plugin.energy_cost / (k_boltzmann * current_temperature))
        priorities.append((plugin.name, priority))

    # Sort by priority (highest first)
    priorities.sort(key=lambda x: x[1], reverse=True)
    return priorities
