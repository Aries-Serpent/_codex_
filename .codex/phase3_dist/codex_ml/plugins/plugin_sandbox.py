"""Plugin sandboxing with contract tests and auto-disable on failure.

This module provides a sandboxed execution environment for plugins with
contract testing, health monitoring, and automatic failure handling.
"""

from __future__ import annotations

import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "Plugin",
    "PluginContract",
    "PluginHealth",
    "PluginManager",
    "PluginSandbox",
    "PluginStatus",
]


class PluginStatus(Enum):
    """Plugin status states."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    QUARANTINED = "quarantined"


@dataclass
class PluginHealth:
    """Plugin health information.

    Attributes:
        plugin_name: Name of the plugin
        status: Current status
        failure_count: Number of consecutive failures
        last_success: Timestamp of last successful execution
        last_failure: Timestamp of last failure
        last_error: Last error message
    """

    plugin_name: str
    status: PluginStatus = PluginStatus.ENABLED
    failure_count: int = 0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    last_error: Optional[str] = None
    quarantined_at: Optional[str] = None  # ISO8601 timestamp when quarantined

    def record_success(self) -> None:
        """Record successful execution."""
        self.failure_count = 0
        self.last_success = datetime.now(UTC).isoformat()
        if self.status == PluginStatus.FAILED:
            self.status = PluginStatus.ENABLED
        # Clear quarantine on success
        if self.status == PluginStatus.QUARANTINED:
            self.status = PluginStatus.ENABLED
            self.quarantined_at = None

    def record_failure(self, error: str):
        """Record failure.

        Args:
            error: Error message
        """
        self.failure_count += 1
        self.last_failure = datetime.now(UTC).isoformat()
        self.last_error = error

    def set_quarantined(self) -> None:
        """set plugin to quarantined status."""
        self.status = PluginStatus.QUARANTINED
        self.quarantined_at = datetime.now(UTC).isoformat()

    def is_quarantine_expired(self, quarantine_duration: int) -> bool:
        """Check if quarantine period has expired.

        Args:
            quarantine_duration: Quarantine duration in seconds

        Returns:
            True if quarantine has expired and plugin should be re-enabled
        """
        if self.status != PluginStatus.QUARANTINED or not self.quarantined_at:
            return False

        try:
            quarantined_time = datetime.fromisoformat(self.quarantined_at)
            elapsed = (datetime.now(UTC) - quarantined_time).total_seconds()
            return elapsed >= quarantine_duration
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning("Failed to parse quarantine timestamp: <ERROR_TYPE>")
            return False


@dataclass
class PluginContract:
    """Contract specification for a plugin.

    Attributes:
        required_methods: list of required method names
        input_schema: Expected input schema (simplified)
        output_schema: Expected output schema (simplified)
        max_execution_time: Maximum execution time in seconds
        required_config_keys: Required configuration keys
    """

    required_methods: list[str] = field(default_factory=list)
    input_schema: Optional[dict[str, type]] = None
    output_schema: Optional[dict[str, type]] = None
    max_execution_time: float = 30.0
    required_config_keys: list[str] = field(default_factory=list)


class Plugin(ABC):
    """Base class for plugins.

    All plugins must inherit from this class and implement required methods.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization successful
        """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin logic.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Plugin execution result
        """

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""

    def get_contract(self) -> PluginContract:
        """Get plugin contract specification.

        Returns:
            PluginContract object
        """
        return PluginContract(required_methods=["initialize", "execute", "cleanup"])


class PluginSandbox:
    """Sandboxed execution environment for plugins."""

    def __init__(
        self,
        max_failures: int = 3,
        quarantine_threshold: int = 2,  # Quarantine after 2 failures
        quarantine_duration: int = 300,  # 5 minutes
        enable_auto_disable: bool = True,
        enable_quarantine: bool = True,
    ):
        """Initialize plugin sandbox.

        Args:
            max_failures: Maximum failures before auto-disable
            quarantine_threshold: Failures before quarantine (should be < max_failures)
            quarantine_duration: Quarantine duration in seconds
            enable_auto_disable: Enable automatic plugin disabling
            enable_quarantine: Enable quarantine feature
        """
        if quarantine_threshold >= max_failures:
            raise ValueError(
                f"quarantine_threshold ({quarantine_threshold}) must be less than "
                f"max_failures ({max_failures})"
            )

        self.max_failures = max_failures
        self.quarantine_threshold = quarantine_threshold
        self.quarantine_duration = quarantine_duration
        self.enable_auto_disable = enable_auto_disable
        self.enable_quarantine = enable_quarantine
        self.health: dict[str, PluginHealth] = {}

    def validate_contract(self, plugin: Plugin, contract: PluginContract) -> bool:
        """Validate plugin against contract.

        Args:
            plugin: Plugin instance
            contract: Contract specification

        Returns:
            True if plugin satisfies contract
        """
        # Check required methods
        for method_name in contract.required_methods:
            if not hasattr(plugin, method_name):
                logger.error(f"Plugin {plugin.name} missing required method: {method_name}")
                return False

            method = getattr(plugin, method_name)
            if not callable(method):
                logger.error(f"Plugin {plugin.name} method {method_name} is not callable")
                return False

        # Check required config keys
        for key in contract.required_config_keys:
            if key not in plugin.config:
                logger.error(f"Plugin {plugin.name} missing required config key: {key}")
                return False

        logger.info(f"Plugin {plugin.name} contract validation passed")
        return True

    def execute_sandboxed(
        self, plugin: Plugin, method_name: str = "execute", *args, **kwargs
    ) -> Optional[Any]:
        """Execute plugin method in sandbox.

        Args:
            plugin: Plugin instance
            method_name: Method to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Execution result or None on failure
        """
        plugin_name = plugin.name

        # Initialize health tracking
        if plugin_name not in self.health:
            self.health[plugin_name] = PluginHealth(plugin_name=plugin_name)

        health = self.health[plugin_name]

        # Check if plugin is disabled
        if health.status == PluginStatus.DISABLED:
            logger.warning(f"Plugin {plugin_name} is disabled, skipping execution")
            return None

        # Check if plugin is quarantined
        if health.status == PluginStatus.QUARANTINED:
            # Check if quarantine duration has expired
            if health.is_quarantine_expired(self.quarantine_duration):
                logger.info(f"Plugin {plugin_name} quarantine expired, re-enabling")
                health.status = PluginStatus.ENABLED
                health.quarantined_at = None
                health.failure_count = 0
            else:
                elapsed = 0
                if health.quarantined_at:
                    try:
                        quarantined_time = datetime.fromisoformat(health.quarantined_at)
                        elapsed = int((datetime.now(UTC) - quarantined_time).total_seconds())
                    except (ValueError, TypeError):
                        # If quarantine timestamp is invalid or missing, default to zero elapsed time.  # noqa: E501
                        # If quarantine timestamp is invalid or missing, default to zero elapsed time.  # noqa: E501
                        # Security note: This keeps the plugin quarantined for the full duration,
                        # which is the safe default behavior when timestamp parsing fails.
                        logger.debug("Suppressed exception in handler", exc_info=True)
                remaining = self.quarantine_duration - elapsed
                logger.warning(
                    f"Plugin {plugin_name} is quarantined, "
                    f"skipping execution ({remaining}s remaining)"
                )
                return None

        try:
            # Get method
            if not hasattr(plugin, method_name):
                raise AttributeError(f"Plugin {plugin_name} has no method {method_name}")

            method = getattr(plugin, method_name)

            # Execute in sandbox
            logger.debug(f"Executing {plugin_name}.{method_name}()")
            result = method(*args, **kwargs)

            # Record success
            health.record_success()
            logger.debug(f"Plugin {plugin_name}.{method_name}() succeeded")

            return result

        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            # Record failure
            error_msg = f"{type(e).__name__}: {e!s}"
            health.record_failure(error_msg)

            logger.error(
                f"Plugin {plugin_name}.{method_name}() failed "
                f"(failures: {health.failure_count}/{self.max_failures}): {error_msg}"
            )
            logger.debug(traceback.format_exc())

            # Quarantine if threshold reached (before auto-disable)
            if (
                self.enable_quarantine
                and health.status != PluginStatus.QUARANTINED
                and health.failure_count >= self.quarantine_threshold
                and health.failure_count < self.max_failures
            ):
                health.set_quarantined()
                logger.warning(
                    f"Plugin {plugin_name} quarantined for {self.quarantine_duration}s "
                    f"after {health.failure_count} consecutive failures"
                )

            # Auto-disable if too many failures
            elif self.enable_auto_disable and health.failure_count >= self.max_failures:
                health.status = PluginStatus.DISABLED
                logger.error(
                    f"Plugin {plugin_name} auto-disabled after "
                    f"{health.failure_count} consecutive failures"
                )

            return None

    def get_health_status(self, plugin_name: str) -> Optional[PluginHealth]:
        """Get health status for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginHealth object or None
        """
        return self.health.get(plugin_name)

    def get_all_health(self) -> dict[str, PluginHealth]:
        """Get health status for all plugins.

        Returns:
            Dictionary mapping plugin names to health objects
        """
        return self.health.copy()

    def enable_plugin(self, plugin_name: str):
        """Manually enable a plugin.

        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.health:
            self.health[plugin_name].status = PluginStatus.ENABLED
            self.health[plugin_name].failure_count = 0
            logger.info(f"Plugin {plugin_name} manually enabled")

    def disable_plugin(self, plugin_name: str):
        """Manually disable a plugin.

        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.health:
            self.health[plugin_name].status = PluginStatus.DISABLED
            logger.info(f"Plugin {plugin_name} manually disabled")


class PluginManager:
    """Manager for plugin lifecycle and execution."""

    def __init__(self, sandbox: Optional[PluginSandbox] = None, validate_contracts: bool = True):
        """Initialize plugin manager.

        Args:
            sandbox: Plugin sandbox (creates default if None)
            validate_contracts: Enable contract validation
        """
        self.sandbox = sandbox or PluginSandbox()
        self.validate_contracts = validate_contracts
        self.plugins: dict[str, Plugin] = {}

    def register_plugin(self, plugin: Plugin) -> bool:
        """Register a plugin.

        Args:
            plugin: Plugin instance

        Returns:
            True if registration successful
        """
        plugin_name = plugin.name

        # Validate contract if enabled
        if self.validate_contracts:
            contract = plugin.get_contract()
            if not self.sandbox.validate_contract(plugin, contract):
                logger.error(f"Plugin {plugin_name} failed contract validation")
                return False

        # Initialize plugin
        try:
            if not plugin.initialize():
                logger.error(f"Plugin {plugin_name} initialization failed")
                return False
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error(f"Plugin {plugin_name} initialization raised exception: <ERROR_TYPE>")
            return False

        # Register
        self.plugins[plugin_name] = plugin
        logger.info(f"Plugin {plugin_name} registered successfully")
        return True

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Optional[Any]:
        """Execute a registered plugin.

        Args:
            plugin_name: Name of the plugin
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Execution result or None on failure
        """
        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} not registered")
            return None

        plugin = self.plugins[plugin_name]
        return self.sandbox.execute_sandboxed(plugin, "execute", *args, **kwargs)

    def execute_all_plugins(self, *args, **kwargs) -> dict[str, Any]:
        """Execute all registered plugins.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Dictionary mapping plugin names to results
        """
        results = {}

        for plugin_name, plugin in self.plugins.items():
            result = self.sandbox.execute_sandboxed(plugin, "execute", *args, **kwargs)
            results[plugin_name] = result

        return results

    def cleanup_all(self) -> None:
        """Clean up all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.cleanup()
                logger.info(f"Plugin {plugin_name} cleanup complete")
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.error(f"Plugin {plugin_name} cleanup failed: <ERROR_TYPE>")

    def get_plugin_health_report(self) -> dict[str, Any]:
        """Get health report for all plugins.

        Returns:
            Health report dictionary
        """
        health_data = self.sandbox.get_all_health()

        report: dict[str, Any] = {
            "total_plugins": len(self.plugins),
            "enabled": 0,
            "disabled": 0,
            "failed": 0,
            "plugins": {},
        }

        for plugin_name, health in health_data.items():
            if health.status == PluginStatus.ENABLED:
                report["enabled"] += 1
            elif health.status == PluginStatus.DISABLED:
                report["disabled"] += 1
            elif health.status == PluginStatus.FAILED:
                report["failed"] += 1

            report["plugins"][plugin_name] = {
                "status": health.status.value,
                "failure_count": health.failure_count,
                "last_success": health.last_success,
                "last_failure": health.last_failure,
                "last_error": health.last_error,
            }

        return report
