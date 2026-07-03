"""Plugin ecosystem foundation and registry.

Provides infrastructure for extending the system with custom plugins:
- Plugin discovery and registration
- Versioning and dependency management
- Plugin lifecycle management
- Hot-reloading support
"""

from __future__ import annotations

import importlib
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

logger = logging.getLogger(__name__)

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "load_plugins",
    "plugin_registry",
    "register_plugin",
]


@dataclass
class PluginMetadata:
    """Metadata for a plugin.

    Attributes:
        name: Plugin name
        version: Plugin version
        author: Plugin author
        description: Plugin description
        dependencies: Required dependencies
        min_codex_version: Minimum codex version required
    """

    name: str
    version: str
    author: str = "Unknown"
    description: str = ""
    dependencies: list[str] | None = None
    min_codex_version: str = "0.1.0"

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


class Plugin(ABC):
    """Base class for all plugins.

    Subclass this to create custom plugins.

    Example:
        >>> class MyPlugin(Plugin):
        ...     def initialize(self):
        ...         logger.info("Plugin initialized")
        ...
        ...     def execute(self, *args, **kwargs):
        ...         return "result"
        ...
        ...     @classmethod
        ...     def get_metadata(cls):
        ...         return PluginMetadata(
        ...             name="my_plugin",
        ...             version="1.0.0",
        ...             author="Me",
        ...         )
    """

    def initialize(self) -> None:
        """Initialize plugin. Override in subclass."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin logic. Override in subclass."""
        raise NotImplementedError()

    def cleanup(self) -> None:
        """Cleanup plugin resources. Override in subclass."""

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata. Override in subclass."""
        return PluginMetadata(
            name=cls.__name__,
            version="0.1.0",
        )


class PluginRegistry:
    """Registry for managing plugins.

    Singleton registry for plugin discovery, registration, and execution.

    Example:
        >>> registry = PluginRegistry()
        >>> registry.register(MyPlugin)
        >>> plugin = registry.get("my_plugin")
        >>> result = plugin.execute()
    """

    _instance = None

    def __new__(cls) -> "PluginRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._plugins: dict[str, type[Plugin]] = {}
        self._instances: dict[str, Plugin] = {}
        self._initialized = True

    def register(self, plugin_class: type[Plugin], override: bool = False) -> None:
        """Register a plugin class.

        Args:
            plugin_class: Plugin class to register
            override: Whether to override existing plugin
        """
        metadata = plugin_class.get_metadata()

        if metadata.name in self._plugins and not override:
            logger.warning(f"Plugin '{metadata.name}' already registered")
            return

        self._plugins[metadata.name] = plugin_class
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")

    def unregister(self, name: str):
        """Unregister a plugin.

        Args:
            name: Plugin name
        """
        if name in self._plugins:
            del self._plugins[name]

            if name in self._instances:
                self._instances[name].cleanup()
                del self._instances[name]

            logger.info(f"Unregistered plugin: {name}")

    def get(self, name: str, create_instance: bool = True) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name
            create_instance: Whether to create instance if not exists

        Returns:
            Plugin instance or None
        """
        if name not in self._plugins:
            logger.warning(f"Plugin not found: {name}")
            return None

        if create_instance and name not in self._instances:
            plugin_class = self._plugins[name]
            instance = plugin_class()
            instance.initialize()
            self._instances[name] = instance

        return self._instances.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """list all registered plugins.

        Returns:
            list of plugin metadata
        """
        return [plugin_class.get_metadata() for plugin_class in self._plugins.values()]

    def discover_plugins(self, directory: str):
        """Discover and load plugins from directory.

        Args:
            directory: Directory containing plugin modules
        """
        plugin_dir = Path(directory)

        if not plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {directory}")
            return

        # Add to Python path
        if str(plugin_dir.parent) not in sys.path:
            sys.path.insert(0, str(plugin_dir.parent))

        # Import all Python files
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.stem.startswith("_"):
                continue

            try:
                module_name = f"{plugin_dir.name}.{plugin_file.stem}"
                importlib.import_module(module_name)
                logger.info(f"Loaded plugin module: {module_name}")
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error(f"Failed to load plugin {plugin_file}: <ERROR_TYPE>")

    def reload_plugin(self, name: str):
        """Reload a plugin (for hot-reloading).

        Args:
            name: Plugin name
        """
        if name not in self._plugins:
            logger.warning(f"Plugin not found: {name}")
            return

        # Cleanup old instance
        if name in self._instances:
            self._instances[name].cleanup()
            del self._instances[name]

        # Re-import module
        plugin_class = self._plugins[name]
        module = sys.modules[plugin_class.__module__]
        importlib.reload(module)

        logger.info(f"Reloaded plugin: {name}")


# Global plugin registry instance
plugin_registry = PluginRegistry()


def register_plugin(plugin_class: type[Plugin]) -> type[Plugin]:
    """Decorator to register a plugin.

    Example:
        >>> @register_plugin
        ... class MyPlugin(Plugin):
        ...     pass
    """
    plugin_registry.register(plugin_class)
    return plugin_class


def load_plugins(directory: str = "plugins") -> None:
    """Load all plugins from directory.

    Args:
        directory: Directory containing plugins
    """
    plugin_registry.discover_plugins(directory)


# Example plugin implementations


@register_plugin
class DataAugmentationPlugin(Plugin):
    """Example: Data augmentation plugin."""

    def initialize(self) -> None:
        """Initialize augmentation pipeline."""
        logger.info("DataAugmentationPlugin initialized")

    def execute(self, data: Any, _augmentation_type: str = "default") -> Any:
        """Apply data augmentation.

        Args:
            data: Input data
            _augmentation_type: Type of augmentation (unused)

        Returns:
            Augmented data
        """
        # Example implementation
        return data

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            name="data_augmentation",
            version="1.0.0",
            author="Codex Team",
            description="Data augmentation pipeline",
        )


@register_plugin
class CustomMetricsPlugin(Plugin):
    """Example: Custom metrics computation plugin."""

    def initialize(self) -> None:
        """Initialize metrics."""
        self.metrics: dict[str, float] = {}
        logger.info("CustomMetricsPlugin initialized")

    def execute(self, predictions: Any, labels: Any) -> dict[str, float]:
        """Compute custom metrics.

        Args:
            predictions: Model predictions
            labels: Ground truth labels

        Returns:
            Dictionary of metric name -> value
        """
        # Example implementation
        return {"custom_score": 0.95}

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            name="custom_metrics",
            version="1.0.0",
            author="Codex Team",
            description="Custom metrics computation",
        )


@register_plugin
class ModelPostProcessingPlugin(Plugin):
    """Example: Model output post-processing plugin."""

    def initialize(self) -> None:
        """Initialize post-processor."""
        logger.info("ModelPostProcessingPlugin initialized")

    def execute(self, model_output: Any) -> Any:
        """Post-process model output.

        Args:
            model_output: Raw model output

        Returns:
            Post-processed output
        """
        # Example implementation
        return model_output

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            name="model_postprocessing",
            version="1.0.0",
            author="Codex Team",
            description="Model output post-processing",
        )
