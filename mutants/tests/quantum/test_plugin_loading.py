"""Tests for quantum plugin loading system."""

from __future__ import annotations

import pytest

from src.quantum import PluginState, QuantumPlugin, QuantumPluginRegistry


class TestQuantumPlugin:
    """Test QuantumPlugin class."""

    def test_plugin_creation(self):
        """Test creating a quantum plugin."""
        plugin = QuantumPlugin(name="test_plugin", import_path="sys", energy_cost=1.5)
        assert plugin.name == "test_plugin", "name is not valid"
        assert plugin.state == PluginState.SUPERPOSITION, "state is not valid"
        assert plugin.energy_cost == 1.5, "energy_cost is not valid"

    def test_plugin_amplitude_superposition(self):
        """Test amplitude calculation in superposition state."""
        plugin = QuantumPlugin(name="test", import_path="sys", energy_cost=2.0)
        amplitude = plugin.get_amplitude()
        assert 0.0 < amplitude <= 1.0, "0 is not valid"
        # Lower energy = higher amplitude
        assert amplitude < 1.0, "amplitude is not valid"

    def test_plugin_amplitude_collapsed(self):
        """Test amplitude in collapsed state."""
        plugin = QuantumPlugin(name="sys", import_path="sys")
        plugin.observe()  # Collapse wave function
        assert plugin.get_amplitude() == 1.0, "Condition must be true"
        assert plugin.state == PluginState.COLLAPSED, "state is not valid"

    def test_plugin_amplitude_decoherent(self):
        """Test amplitude in decoherent state."""
        plugin = QuantumPlugin(name="invalid", import_path="nonexistent.module")
        try:
            plugin.observe()
        except ImportError:
            # Expected: plugin deliberately designed to fail import
            _ = None  # suppressed: no action needed
        assert plugin.get_amplitude() == 0.0, "Condition must be true"
        assert plugin.state == PluginState.DECOHERENT, "state is not valid"

    def test_plugin_observe_success(self):
        """Test successful plugin loading."""
        plugin = QuantumPlugin(name="sys", import_path="sys")
        module = plugin.observe()
        assert module is not None, "module must be initialized"
        assert plugin.state == PluginState.COLLAPSED, "state is not valid"
        assert plugin._module is module, "_module is not valid"

    def test_plugin_observe_idempotent(self):
        """Test that multiple observations return same module."""
        plugin = QuantumPlugin(name="os", import_path="os")
        module1 = plugin.observe()
        module2 = plugin.observe()
        assert module1 is module2, "module1 is not valid"
        assert plugin.state == PluginState.COLLAPSED, "state is not valid"

    def test_plugin_observe_failure(self):
        """Test failed plugin loading."""
        plugin = QuantumPlugin(name="invalid", import_path="nonexistent.module")
        with pytest.raises(ImportError):
            plugin.observe()
        assert plugin.state == PluginState.DECOHERENT, "state is not valid"

    def test_plugin_observe_decoherent_raises(self):
        """Test observing decoherent plugin raises error."""
        plugin = QuantumPlugin(name="invalid", import_path="nonexistent.module")
        try:
            plugin.observe()
        except ImportError:
            # Expected: first observation fails and sets plugin to decoherent state
            _ = None  # suppressed: no action needed
        # Second attempt should also raise
        with pytest.raises(ImportError):
            plugin.observe()


class TestQuantumPluginRegistry:
    """Test QuantumPluginRegistry class."""

    def test_registry_creation(self):
        """Test creating a plugin registry."""
        registry = QuantumPluginRegistry()
        assert registry.plugins == {}, "plugins is not valid"
        assert registry.dependency_graph is not None, "dependency_graph must be initialized"

    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = QuantumPluginRegistry()
        plugin = QuantumPlugin(name="test", import_path="sys")
        registry.register(plugin)
        assert "test" in registry.plugins, "Condition must be true"
        assert registry.plugins["test"] is plugin, "Condition must be true"

    def test_register_plugin_with_dependencies(self):
        """Test registering plugin with dependencies."""
        registry = QuantumPluginRegistry()
        dep_plugin = QuantumPlugin(name="dep", import_path="os")
        main_plugin = QuantumPlugin(name="main", import_path="sys", dependencies=["dep"])
        registry.register(dep_plugin)
        registry.register(main_plugin)

        assert main_plugin.state == PluginState.ENTANGLED, "state is not valid"
        entangled = registry.get_entangled_plugins("main")
        assert "dep" in entangled, "Condition must be true"

    def test_load_with_dependencies(self):
        """Test loading plugin with dependencies."""
        registry = QuantumPluginRegistry()

        # Register plugins in dependency order
        dep = QuantumPlugin(name="os_dep", import_path="os")
        main = QuantumPlugin(name="sys_main", import_path="sys", dependencies=["os_dep"])

        registry.register(dep)
        registry.register(main)

        # Load main plugin (should also load dependency)
        module = registry.load_with_dependencies("sys_main")
        assert module is not None, "module must be initialized"
        assert dep.state == PluginState.COLLAPSED, "state is not valid"
        assert main.state == PluginState.COLLAPSED, "state is not valid"

    def test_load_nonexistent_plugin(self):
        """Test loading non-registered plugin raises error."""
        registry = QuantumPluginRegistry()
        with pytest.raises(KeyError):
            registry.load_with_dependencies("nonexistent")

    def test_get_entangled_plugins_empty(self):
        """Test getting entangled plugins for plugin with no dependencies."""
        registry = QuantumPluginRegistry()
        plugin = QuantumPlugin(name="test", import_path="sys")
        registry.register(plugin)

        entangled = registry.get_entangled_plugins("test")
        assert len(entangled) == 0, "Entangled must not be empty"

    def test_thermodynamic_load_priority(self):
        """Test calculating load priority using Boltzmann distribution."""
        from src.quantum.plugin_registry import calculate_thermodynamic_load_priority

        plugins = [
            QuantumPlugin(name="high_energy", import_path="sys", energy_cost=5.0),
            QuantumPlugin(name="low_energy", import_path="os", energy_cost=0.5),
            QuantumPlugin(name="medium_energy", import_path="math", energy_cost=2.0),
        ]

        priorities = calculate_thermodynamic_load_priority(plugins, current_temperature=1.0)

        # Check that lower energy has higher priority
        names = [name for name, _ in priorities]
        assert names[0] == "low_energy", "Condition must be true"
        assert names[-1] == "high_energy", "Condition must be true"


@pytest.mark.integration
class TestPluginIntegration:
    """Integration tests for plugin system."""

    def test_real_module_loading(self):
        """Test loading real Python modules."""
        registry = QuantumPluginRegistry()

        # Register several standard library modules
        for module_name in ["sys", "os", "math", "time"]:
            plugin = QuantumPlugin(name=module_name, import_path=module_name)
            registry.register(plugin)

        # Load all plugins
        for module_name in ["sys", "os", "math", "time"]:
            module = registry.load_with_dependencies(module_name)
            assert module is not None, "module must be initialized"
            assert registry.plugins[module_name].state == PluginState.COLLAPSED, "state is not valid"

    def test_complex_dependency_chain(self):
        """Test loading plugins with complex dependency chains."""
        registry = QuantumPluginRegistry()

        # Create dependency chain: A -> B -> C
        plugin_c = QuantumPlugin(name="math_c", import_path="math")
        plugin_b = QuantumPlugin(name="os_b", import_path="os", dependencies=["math_c"])
        plugin_a = QuantumPlugin(name="sys_a", import_path="sys", dependencies=["os_b"])

        registry.register(plugin_c)
        registry.register(plugin_b)
        registry.register(plugin_a)

        # Load A (should load B and C as well)
        module = registry.load_with_dependencies("sys_a")
        assert module is not None, "module must be initialized"
        assert plugin_a.state == PluginState.COLLAPSED, "state is not valid"
        assert plugin_b.state == PluginState.COLLAPSED, "state is not valid"
        assert plugin_c.state == PluginState.COLLAPSED, "state is not valid"
