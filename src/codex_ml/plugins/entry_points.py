"""
Enhanced Entry-Point Plugin System (D2)

Provides comprehensive plugin discovery, validation, and management:
- Automatic discovery via Python entry points
- Plugin validation and dependency checking
- Version compatibility verification
- Plugin lifecycle management
- Error handling and graceful degradation
"""

from __future__ import annotations

import importlib
import importlib.metadata
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from packaging import version as pkg_version

logger = logging.getLogger(__name__)

__all__ = [
    "EntryPointPluginRegistry",
    "PluginInfo",
    "PluginValidator",
    "discover_plugins",
    "validate_plugin",
]


@dataclass
class PluginInfo:
    """Information about a discovered plugin."""

    name: str
    entry_point_group: str
    entry_point_name: str
    module_name: str
    version: Optional[str] = None
    description: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    required_codex_version: Optional[str] = None
    plugin_class: Optional[type] = None
    loaded: bool = False
    error: Optional[str] = None


class PluginValidator:
    """Validator for plugin compatibility and dependencies."""

    def __init__(self, codex_version: Optional[str] = None):
        self.codex_version = codex_version or self._get_codex_version()

    def _get_codex_version(self) -> str:
        """Get the current codex_ml version."""
        try:
            return importlib.metadata.version("codex_ml")
        except importlib.metadata.PackageNotFoundError:
            logger.debug("Exception caught, returning", exc_info=True)
            return "0.0.0"

    def validate_plugin(self, plugin_info: PluginInfo) -> tuple[bool, Optional[str]]:
        """Validate a plugin.

        Args:
            plugin_info: Plugin information

        Returns:
            tuple of (is_valid, error_message)
        """
        # Check version compatibility
        if plugin_info.required_codex_version:
            try:
                required = pkg_version.parse(plugin_info.required_codex_version)
                current = pkg_version.parse(self.codex_version)
                if current < required:
                    return False, (
                        f"Plugin {plugin_info.name} requires codex_ml >= "
                        f"{plugin_info.required_codex_version}, "
                        f"but {self.codex_version} is installed"
                    )
            except (ValueError, TypeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning(f"Failed to parse version for {plugin_info.name}: <ERROR_TYPE>")

        # Check dependencies
        for dep in plugin_info.dependencies:
            if not self._check_dependency(dep):
                return False, f"Missing dependency: {dep}"

        return True, None

    def _check_dependency(self, dep: str) -> bool:
        """Check if a dependency is installed."""
        try:
            # Parse dependency (e.g., "numpy>=1.20.0" -> "numpy")
            pkg_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()
            importlib.metadata.version(pkg_name)
            return True
        except importlib.metadata.PackageNotFoundError:
            logger.debug("Exception caught, returning", exc_info=True)
            return False


class EntryPointPluginRegistry:
    """Registry for entry-point based plugins."""

    # Default entry point groups
    DEFAULT_GROUPS = {
        "codex_ml.plugins": "Generic plugins",
        "codex_ml.tokenizers": "Tokenizer plugins",
        "codex_ml.models": "Model plugins",
        "codex_ml.datasets": "Dataset plugins",
        "codex_ml.metrics": "Metrics plugins",
        "codex_ml.trainers": "Trainer plugins",
        "codex_ml.reward_models": "Reward model plugins",
        "codex_ml.rl_agents": "RL agent plugins",
    }

    def __init__(self, validator: Optional[PluginValidator] = None):
        self.validator = validator or PluginValidator()
        self._plugins: dict[str, dict[str, PluginInfo]] = {}
        self._loaded_instances: dict[str, Any] = {}

    def discover_plugins(
        self,
        groups: Optional[list[str]] = None,
        auto_load: bool = False,
    ) -> dict[str, list[PluginInfo]]:
        """Discover plugins from entry points.

        Args:
            groups: Entry point groups to search. If None, uses DEFAULT_GROUPS
            auto_load: Whether to automatically load discovered plugins

        Returns:
            Dictionary mapping group names to lists of plugin info
        """
        if groups is None:
            groups = list(self.DEFAULT_GROUPS.keys())

        discovered: dict[str, Any] = {}

        for group in groups:
            discovered[group] = []

            try:
                entry_points = importlib.metadata.entry_points()
                # Handle both new (3.10+) and old API
                if hasattr(entry_points, "select"):
                    eps = entry_points.select(group=group)
                else:
                    eps = entry_points.get(group, [])  # type: ignore[attr-defined]

                for ep in eps:
                    plugin_info = self._create_plugin_info(ep, group)

                    # Validate plugin
                    is_valid, error = self.validator.validate_plugin(plugin_info)
                    if not is_valid:
                        plugin_info.error = error
                        logger.warning(f"Plugin {ep.name} validation failed: {error}")

                    discovered[group].append(plugin_info)

                    # Store in registry
                    if group not in self._plugins:
                        self._plugins[group] = {}
                    self._plugins[group][ep.name] = plugin_info

                    # Auto-load if requested and valid
                    if auto_load and is_valid:
                        self.load_plugin(group, ep.name)

            except (ConnectionError, TimeoutError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error(f"Failed to discover plugins in group {group}: <ERROR_TYPE>")

        return discovered

    def _create_plugin_info(
        self,
        entry_point,
        group: str,
    ) -> PluginInfo:
        """Create PluginInfo from entry point."""
        try:
            # Try to load the plugin class
            plugin_class = entry_point.load()

            # Extract metadata if available
            metadata = {}
            if hasattr(plugin_class, "get_metadata"):
                meta = plugin_class.get_metadata()
                metadata = {
                    "version": getattr(meta, "version", None),
                    "description": getattr(meta, "description", None),
                    "dependencies": getattr(meta, "dependencies", []),
                    "required_codex_version": getattr(meta, "min_codex_version", None),
                }

            return PluginInfo(
                name=entry_point.name,
                entry_point_group=group,
                entry_point_name=entry_point.name,
                module_name=entry_point.value,
                plugin_class=plugin_class,
                **metadata,  # type: ignore[arg-type]
            )
        except (ImportError, AttributeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Failed to load entry point {entry_point.name}: <ERROR_TYPE>")
            return PluginInfo(
                name=entry_point.name,
                entry_point_group=group,
                entry_point_name=entry_point.name,
                module_name=entry_point.value,
                error=str(e),
            )

    def load_plugin(
        self,
        group: str,
        name: str,
        *args,
        **kwargs,
    ) -> Optional[Any]:
        """Load and instantiate a plugin.

        Args:
            group: Entry point group
            name: Plugin name
            *args, **kwargs: Arguments for plugin instantiation

        Returns:
            Plugin instance or None if loading failed
        """
        key = f"{group}/{name}"

        # Return cached instance if already loaded
        if key in self._loaded_instances:
            return self._loaded_instances[key]

        if group not in self._plugins or name not in self._plugins[group]:
            logger.error(f"Plugin {name} not found in group {group}")
            return None

        plugin_info = self._plugins[group][name]

        # Check for previous errors
        if plugin_info.error:
            logger.error(f"Cannot load plugin {name}: {plugin_info.error}")
            return None

        # Check if plugin class is available
        if not plugin_info.plugin_class:
            logger.error(f"Plugin class not available for {name}")
            return None

        try:
            # Instantiate plugin
            instance = plugin_info.plugin_class(*args, **kwargs)

            # Initialize if method exists
            if hasattr(instance, "initialize"):
                instance.initialize()

            plugin_info.loaded = True
            self._loaded_instances[key] = instance

            logger.info(f"Successfully loaded plugin: {name} from {group}")
            return instance

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            error_msg = f"Failed to load plugin {name}: {e}"
            plugin_info.error = error_msg
            logger.error(error_msg)
            return None

    def get_plugin(
        self,
        group: str,
        name: str,
    ) -> Optional[Any]:
        """Get a loaded plugin instance.

        Args:
            group: Entry point group
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        key = f"{group}/{name}"
        return self._loaded_instances.get(key)

    def list_plugins(
        self,
        group: Optional[str] = None,
    ) -> dict[str, list[str]]:
        """list all discovered plugins.

        Args:
            group: Optional group filter

        Returns:
            Dictionary mapping groups to plugin names
        """
        if group:
            if group in self._plugins:
                return {group: list(self._plugins[group].keys())}
            return {group: []}

        return {g: list(plugins.keys()) for g, plugins in self._plugins.items()}

    def get_plugin_info(
        self,
        group: str,
        name: str,
    ) -> Optional[PluginInfo]:
        """Get plugin information.

        Args:
            group: Entry point group
            name: Plugin name

        Returns:
            PluginInfo or None
        """
        if group in self._plugins and name in self._plugins[group]:
            return self._plugins[group][name]
        return None


# Global registry instance
_global_registry = EntryPointPluginRegistry()


def discover_plugins(
    groups: Optional[list[str]] = None,
    auto_load: bool = False,
) -> dict[str, list[PluginInfo]]:
    """Discover plugins from entry points (convenience function).

    Args:
        groups: Entry point groups to search
        auto_load: Whether to automatically load plugins

    Returns:
        Dictionary of discovered plugins
    """
    return _global_registry.discover_plugins(groups=groups, auto_load=auto_load)


def validate_plugin(plugin_info: PluginInfo) -> tuple[bool, Optional[str]]:
    """Validate a plugin (convenience function).

    Args:
        plugin_info: Plugin information

    Returns:
        tuple of (is_valid, error_message)
    """
    validator = PluginValidator()
    return validator.validate_plugin(plugin_info)
