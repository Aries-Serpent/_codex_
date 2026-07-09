"""
Quantum-inspired lazy plugin loading with superposition states.

Cross-references:
    - src/codex_ml/plugins/loader.py
    - agents/advanced_physics_calculators.py
    - src/codex/ast/graph.py:DependencyGraph
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
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
            # If the module is already in sys.modules (e.g. mocked by tests),
            # use it directly — avoids Python 3.12 ValueError from find_spec
            # when __spec__ is None on a sys.modules entry.
            existing = sys.modules.get(self.import_path)
            if existing is not None:
                self._module = existing
                self.state = PluginState.COLLAPSED
                logger.info(f"✓ Plugin '{self.name}' resolved from sys.modules")
                return self._module

            # Direct import without safe_call to properly propagate exceptions
            # This ensures tests can properly mock imports and CI failures are visible
            try:
                spec = importlib.util.find_spec(self.import_path)
            except ValueError:
                # Python 3.12: find_spec raises ValueError when the module is in
                # sys.modules but __spec__ is None (created via types.ModuleType).
                # Fall back to importlib.import_module.
                try:
                    self._module = importlib.import_module(self.import_path)
                    self.state = PluginState.COLLAPSED
                    return self._module
                except ImportError:
                    spec = None

            if spec is None:
                self.state = PluginState.DECOHERENT
                raise ImportError(f"Cannot find spec for {self.import_path}")

            if spec.loader is None:
                self.state = PluginState.DECOHERENT
                raise ImportError(f"No loader available for {self.import_path}")

            module = importlib.util.module_from_spec(spec)
            if module is None:
                self.state = PluginState.DECOHERENT
                raise ImportError(f"Failed to create module for {self.name}")

            spec.loader.exec_module(module)

            self._module = module
            self.state = PluginState.COLLAPSED
            logger.info(f"✓ Plugin '{self.name}' wave function collapsed successfully")

            return self._module

        except (ImportError, AttributeError):
            self.state = PluginState.DECOHERENT
            logger.error(f"Plugin '{self.name}' decoherence: <ERROR_TYPE>")
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
        if self.state == PluginState.DECOHERENT:
            return 0.0
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
        from codex.ast.graph import DependencyGraph

        self.dependency_graph = DependencyGraph()

    def register(self, plugin: QuantumPlugin) -> None:
        """
        Register plugin and build entanglement graph.

        Args:
            plugin: Plugin to register
        """
        self.plugins[plugin.name] = plugin
        # add_node now creates edges: dependency → plugin (correct direction)
        self.dependency_graph.add_node(  # type: ignore[union-attr]
            plugin.name, dependencies=plugin.dependencies, data={"plugin": plugin}
        )

        # Mark plugins with dependencies as entangled
        if plugin.dependencies and plugin.name in self.plugins:
            self.plugins[plugin.name].state = PluginState.ENTANGLED

    def get_entangled_plugins(self, plugin_name: str) -> set[str]:
        """
        Get all plugins entangled with the given plugin (its dependencies).

        Physics: Quantum entanglement - measuring one affects others.

        Args:
            plugin_name: Name of plugin to check

        Returns:
            Set of plugin names that this plugin depends on (transitively)
        """
        # The dependency graph stores edges as: dependency -> dependent
        # So to find what plugin_name depends on, we need to traverse backwards
        # We collect all nodes that have a path TO plugin_name
        visited = set()

        def find_dependencies(node_id: str):
            """Recursively find all dependencies of node_id."""
            if node_id not in self.plugins:
                return

            plugin = self.plugins[node_id]
            for dep_name in plugin.dependencies:
                if dep_name not in visited and dep_name in self.plugins:
                    visited.add(dep_name)
                    find_dependencies(dep_name)

        find_dependencies(plugin_name)
        return visited

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
            load_order = self.dependency_graph.topological_sort()  # type: ignore[union-attr]
        except (ValueError, TypeError):
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
                except (ImportError, AttributeError) as exc:
                    type(exc).__name__
                    logger.warning(f"Failed to load dependency '{p_name}': <ERROR_TYPE>")

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
