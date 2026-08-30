"""Comprehensive tests for extensibility capability.

Tests cover:
- Plugin sandboxing
- Compatibility matrix
- Contract tests and ABI/version negotiation
- Self-healing discovery errors
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Plugin Interface Contract Tests ---


class PluginInterface(ABC):
    """Base plugin interface contract."""

    @abstractmethod
    def name(self) -> str:
        """Return plugin name."""

    @abstractmethod
    def version(self) -> str:
        """Return plugin version."""

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize plugin with config."""

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute plugin logic."""

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""


class SamplePlugin(PluginInterface):
    """Sample plugin implementation for testing."""

    def __init__(self):
        self._initialized = False
        self._config: dict[str, Any] = {}

    def name(self) -> str:
        return "sample_plugin"

    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: dict[str, Any]) -> bool:
        self._config = config
        self._initialized = True
        return True

    def execute(self, input_data: Any) -> Any:
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")
        return {"processed": input_data, "config": self._config}

    def cleanup(self) -> None:
        self._initialized = False
        self._config = {}


class TestPluginContract:
    """Tests for plugin contract compliance."""

    def test_plugin_has_name(self):
        """Plugin must have a name."""
        plugin = SamplePlugin()
        assert isinstance(plugin.name(), str)
        assert len(plugin.name()) > 0, "Collection must not be empty"

    def test_plugin_has_version(self):
        """Plugin must have a version."""
        plugin = SamplePlugin()
        assert isinstance(plugin.version(), str)
        assert len(plugin.version()) > 0, "Collection must not be empty"

    def test_plugin_initialization(self):
        """Plugin must initialize correctly."""
        plugin = SamplePlugin()
        result = plugin.initialize({"setting": "value"})
        assert result is True, "Result must not be empty"

    def test_plugin_execute_after_init(self):
        """Plugin must execute after initialization."""
        plugin = SamplePlugin()
        plugin.initialize({})
        result = plugin.execute("test_input")
        assert result is not None, "result must be initialized"

    def test_plugin_execute_before_init_fails(self):
        """Plugin must fail if executed before initialization."""
        plugin = SamplePlugin()
        with pytest.raises(RuntimeError):
            plugin.execute("test_input")

    def test_plugin_cleanup(self):
        """Plugin must cleanup correctly."""
        plugin = SamplePlugin()
        plugin.initialize({})
        plugin.cleanup()
        with pytest.raises(RuntimeError):
            plugin.execute("test_input")


# --- Plugin Registry Tests ---


class PluginRegistry:
    """Registry for managing plugins."""

    def __init__(self):
        self._plugins: dict[str, type] = {}
        self._instances: dict[str, PluginInterface] = {}

    def register(self, plugin_cls: type) -> None:
        """Register a plugin class."""
        instance = plugin_cls()
        name = instance.name()
        self._plugins[name] = plugin_cls

    def get(self, name: str) -> type | None:
        """Get plugin class by name."""
        return self._plugins.get(name)

    def instantiate(
        self, name: str, config: dict[str, Any] | None = None
    ) -> PluginInterface | None:
        """Instantiate and initialize a plugin."""
        plugin_cls = self._plugins.get(name)
        if plugin_cls is None:
            return None
        instance = plugin_cls()
        instance.initialize(config or {})
        self._instances[name] = instance
        return instance

    def list_plugins(self) -> list[str]:
        """List all registered plugins."""
        return list(self._plugins.keys())

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        if name in self._plugins:
            if name in self._instances:
                self._instances[name].cleanup()
                del self._instances[name]
            del self._plugins[name]
            return True
        return False


class TestPluginRegistry:
    """Tests for plugin registry."""

    def test_register_plugin(self):
        """Register plugin in registry."""
        registry = PluginRegistry()
        registry.register(SamplePlugin)
        assert "sample_plugin" in registry.list_plugins(), "Condition must be true"

    def test_get_plugin(self):
        """Get plugin class from registry."""
        registry = PluginRegistry()
        registry.register(SamplePlugin)
        plugin_cls = registry.get("sample_plugin")
        assert plugin_cls == SamplePlugin, "plugin_cls is not valid"

    def test_instantiate_plugin(self):
        """Instantiate plugin from registry."""
        registry = PluginRegistry()
        registry.register(SamplePlugin)
        instance = registry.instantiate("sample_plugin", {"test": "config"})
        assert instance is not None, "instance must be initialized"
        assert instance.name() == "sample_plugin", "Condition must be true"

    def test_unregister_plugin(self):
        """Unregister plugin from registry."""
        registry = PluginRegistry()
        registry.register(SamplePlugin)
        result = registry.unregister("sample_plugin")
        assert result is True, "Result must not be empty"
        assert "sample_plugin" not in registry.list_plugins(), "Condition must be true"


# --- Version Compatibility Matrix Tests ---


class VersionCompatibility:
    """Manages version compatibility between plugins and host."""

    def __init__(self):
        self.matrix: dict[str, dict[str, list[str]]] = {}

    def add_compatibility(self, plugin: str, plugin_version: str, host_versions: list[str]) -> None:
        """Add compatibility entry."""
        if plugin not in self.matrix:
            self.matrix[plugin] = {}
        self.matrix[plugin][plugin_version] = host_versions

    def is_compatible(self, plugin: str, plugin_version: str, host_version: str) -> bool:
        """Check if plugin version is compatible with host version."""
        if plugin not in self.matrix:
            return False
        if plugin_version not in self.matrix[plugin]:
            return False
        return host_version in self.matrix[plugin][plugin_version]

    def get_compatible_host_versions(self, plugin: str, plugin_version: str) -> list[str]:
        """Get compatible host versions for plugin."""
        if plugin not in self.matrix:
            return []
        return self.matrix[plugin].get(plugin_version, [])


class TestVersionCompatibility:
    """Tests for version compatibility matrix."""

    def test_add_compatibility(self):
        """Add compatibility entry."""
        compat = VersionCompatibility()
        compat.add_compatibility("my_plugin", "1.0.0", ["2.0", "2.1", "2.2"])
        assert "my_plugin" in compat.matrix, "Condition must be true"

    def test_check_compatible(self):
        """Check compatible versions."""
        compat = VersionCompatibility()
        compat.add_compatibility("my_plugin", "1.0.0", ["2.0", "2.1"])
        assert compat.is_compatible("my_plugin", "1.0.0", "2.0")
        assert compat.is_compatible("my_plugin", "1.0.0", "2.1")

    def test_check_incompatible(self):
        """Check incompatible versions."""
        compat = VersionCompatibility()
        compat.add_compatibility("my_plugin", "1.0.0", ["2.0", "2.1"])
        assert not compat.is_compatible("my_plugin", "1.0.0", "3.0")

    def test_unknown_plugin(self):
        """Unknown plugin is not compatible."""
        compat = VersionCompatibility()
        assert not compat.is_compatible("unknown", "1.0.0", "2.0")


# --- Plugin Sandboxing Tests ---


class PluginSandbox:
    """Sandbox for running plugins with resource limits."""

    def __init__(self, max_memory_mb: int = 100, max_time_sec: float = 5.0):
        self.max_memory_mb = max_memory_mb
        self.max_time_sec = max_time_sec
        self.allowed_modules: set[str] = {"json", "math", "re"}
        self.denied_modules: set[str] = {"os", "subprocess", "sys", "importlib"}

    def is_module_allowed(self, module_name: str) -> bool:
        """Check if module is allowed in sandbox."""
        if module_name in self.denied_modules:
            return False
        # Allow explicit whitelist or non-system modules
        return module_name in self.allowed_modules or not module_name.startswith("_")

    def validate_plugin_code(self, code: str) -> list[str]:
        """Validate plugin code for sandbox safety."""
        violations = []
        for module in self.denied_modules:
            if f"import {module}" in code or f"from {module}" in code:
                violations.append(f"Denied module import: {module}")
        if "exec(" in code or "eval(" in code:
            violations.append("Dynamic code execution not allowed")
        if "__import__" in code:
            violations.append("Dynamic imports not allowed")
        return violations

    def run(self, plugin: PluginInterface, input_data: Any) -> dict[str, Any]:
        """Run plugin in sandbox (simplified simulation)."""
        # In real implementation, this would use resource limits
        try:
            result = plugin.execute(input_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


class TestPluginSandbox:
    """Tests for plugin sandboxing."""

    def test_allowed_module(self):
        """Allowed modules should pass."""
        sandbox = PluginSandbox()
        assert sandbox.is_module_allowed("json"), "s is not valid"
        assert sandbox.is_module_allowed("math"), "s is not valid"

    def test_denied_module(self):
        """Denied modules should fail."""
        sandbox = PluginSandbox()
        assert not sandbox.is_module_allowed("os"), "Condition must be true"
        assert not sandbox.is_module_allowed("subprocess"), "Condition must be true"

    def test_validate_safe_code(self):
        """Safe code should pass validation."""
        sandbox = PluginSandbox()
        code = "import json\ndef process(x): return json.dumps(x)"
        violations = sandbox.validate_plugin_code(code)
        assert len(violations) == 0, "Violations must not be empty"

    def test_validate_unsafe_code(self):
        """Unsafe code should fail validation."""
        sandbox = PluginSandbox()
        code = "import os\nos.system('rm -rf /')"
        violations = sandbox.validate_plugin_code(code)
        assert len(violations) > 0, "Violations must not be empty"

    def test_validate_eval_denied(self):
        """Eval should be denied."""
        sandbox = PluginSandbox()
        code = "eval('malicious')"
        violations = sandbox.validate_plugin_code(code)
        assert len(violations) > 0, "Violations must not be empty"

    def test_run_plugin_success(self):
        """Run plugin successfully in sandbox."""
        sandbox = PluginSandbox()
        plugin = SamplePlugin()
        plugin.initialize({})
        result = sandbox.run(plugin, "test")
        assert result["success"] is True, "Result must not be empty"


# --- Self-Healing Discovery Tests ---


class SelfHealingDiscovery:
    """Self-healing plugin discovery system."""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.failed_plugins: dict[str, list[dict[str, Any]]] = {}
        self.max_retries = 3
        self.retry_delays = [1, 5, 30]  # seconds

    def discover_plugin(self, name: str, loader_fn) -> PluginInterface | None:
        """Discover and load plugin with self-healing."""
        self.failed_plugins.get(name, [])

        for attempt in range(self.max_retries):
            try:
                plugin = loader_fn()
                if plugin is not None:
                    self.registry.register(type(plugin))
                    # Clear failure history on success
                    if name in self.failed_plugins:
                        del self.failed_plugins[name]
                    return plugin
            except Exception as e:
                error_record = {"attempt": attempt, "error": str(e)}
                if name not in self.failed_plugins:
                    self.failed_plugins[name] = []
                self.failed_plugins[name].append(error_record)

        return None

    def get_failure_count(self, name: str) -> int:
        """Get number of failures for a plugin."""
        return len(self.failed_plugins.get(name, []))

    def should_retry(self, name: str) -> bool:
        """Check if plugin should be retried."""
        return self.get_failure_count(name) < self.max_retries

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of discovery system."""
        return {
            "total_registered": len(self.registry.list_plugins()),
            "failed_plugins": list(self.failed_plugins.keys()),
            "failure_counts": {k: len(v) for k, v in self.failed_plugins.items()},
        }


class TestSelfHealingDiscovery:
    """Tests for self-healing discovery."""

    def test_successful_discovery(self):
        """Successful discovery should register plugin."""
        registry = PluginRegistry()
        discovery = SelfHealingDiscovery(registry)
        plugin = discovery.discover_plugin("sample", SamplePlugin)
        assert plugin is not None, "plugin must be initialized"
        assert "sample_plugin" in registry.list_plugins(), "Condition must be true"

    def test_failed_discovery_tracked(self):
        """Failed discovery should track failures."""
        registry = PluginRegistry()
        discovery = SelfHealingDiscovery(registry)

        def failing_loader():
            raise RuntimeError("Load failed")

        plugin = discovery.discover_plugin("bad_plugin", failing_loader)
        assert plugin is None, "plugin is not valid"
        assert discovery.get_failure_count("bad_plugin") == 3, "Count must be greater than zero"

    def test_should_retry(self):
        """Should retry up to max retries."""
        registry = PluginRegistry()
        discovery = SelfHealingDiscovery(registry)
        assert discovery.should_retry("new_plugin"), "Condition must be true"

    def test_health_status(self):
        """Health status should be accurate."""
        registry = PluginRegistry()
        registry.register(SamplePlugin)
        discovery = SelfHealingDiscovery(registry)
        status = discovery.get_health_status()
        assert status["total_registered"] == 1, "Condition must be true"


# --- Entry Point Discovery Tests ---


class EntryPointLoader:
    """Loads plugins from entry points."""

    def __init__(self):
        self.entry_points: dict[str, dict[str, str]] = {}

    def register_entry_point(self, group: str, name: str, module_path: str) -> None:
        """Register an entry point."""
        if group not in self.entry_points:
            self.entry_points[group] = {}
        self.entry_points[group][name] = module_path

    def list_entry_points(self, group: str) -> list[str]:
        """List entry points in a group."""
        return list(self.entry_points.get(group, {}).keys())

    def get_entry_point(self, group: str, name: str) -> str | None:
        """Get entry point module path."""
        return self.entry_points.get(group, {}).get(name)


class TestEntryPointLoader:
    """Tests for entry point loading."""

    def test_register_entry_point(self):
        """Register entry point."""
        loader = EntryPointLoader()
        loader.register_entry_point("codex.plugins", "my_plugin", "my_package.plugins:MyPlugin")
        assert "my_plugin" in loader.list_entry_points("codex.plugins"), "Condition must be true"

    def test_list_entry_points(self):
        """List entry points in group."""
        loader = EntryPointLoader()
        loader.register_entry_point("codex.plugins", "plugin1", "path1")
        loader.register_entry_point("codex.plugins", "plugin2", "path2")
        assert len(loader.list_entry_points("codex.plugins")) == 2, "Collection must not be empty"

    def test_get_entry_point(self):
        """Get entry point path."""
        loader = EntryPointLoader()
        loader.register_entry_point("codex.plugins", "my_plugin", "my_package:MyPlugin")
        path = loader.get_entry_point("codex.plugins", "my_plugin")
        assert path == "my_package:MyPlugin", "path is not valid"


# --- ABI Version Negotiation Tests ---


class ABIVersion:
    """Represents an ABI version."""

    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, other: "ABIVersion") -> bool:
        """Check if this version is compatible with another."""
        # Major version must match, minor can be greater or equal
        return self.major == other.major and self.minor >= other.minor


class ABINegotiator:
    """Negotiates ABI versions between plugin and host."""

    def __init__(self, host_version: ABIVersion):
        self.host_version = host_version

    def negotiate(self, plugin_required: ABIVersion) -> dict[str, Any]:
        """Negotiate ABI version."""
        compatible = self.host_version.is_compatible_with(plugin_required)
        return {
            "compatible": compatible,
            "host_version": str(self.host_version),
            "required_version": str(plugin_required),
        }


class TestABINegotiation:
    """Tests for ABI version negotiation."""

    def test_compatible_versions(self):
        """Compatible versions should negotiate successfully."""
        host = ABIVersion(2, 1, 0)
        negotiator = ABINegotiator(host)
        result = negotiator.negotiate(ABIVersion(2, 0, 0))
        assert result["compatible"] is True, "Result must not be empty"

    def test_incompatible_major(self):
        """Incompatible major versions should fail."""
        host = ABIVersion(2, 0, 0)
        negotiator = ABINegotiator(host)
        result = negotiator.negotiate(ABIVersion(3, 0, 0))
        assert result["compatible"] is False, "Result must not be empty"

    def test_incompatible_minor(self):
        """Host minor less than required should fail."""
        host = ABIVersion(2, 0, 0)
        negotiator = ABINegotiator(host)
        result = negotiator.negotiate(ABIVersion(2, 1, 0))
        assert result["compatible"] is False, "Result must not be empty"

    @given(
        st.integers(min_value=1, max_value=10),
        st.integers(min_value=0, max_value=10),
        st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=30)
    def test_same_version_always_compatible(self, major: int, minor: int, patch: int):
        """Property: same version is always compatible with itself."""
        version = ABIVersion(major, minor, patch)
        negotiator = ABINegotiator(version)
        result = negotiator.negotiate(version)
        assert result["compatible"] is True, "Result must not be empty"
