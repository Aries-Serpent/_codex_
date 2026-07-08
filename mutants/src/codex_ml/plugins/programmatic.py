"""
Programmatic Module

This module provides functionality for programmatic.

Usage:
    from plugins.programmatic import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from contextlib import suppress  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from functools import lru_cache  # noqa: E402

from .base import BasePlugin  # noqa: E402
from .registry import (  # noqa: E402
    DEFAULT_GROUP,
    _activate_editable_distribution,
    _iter_entry_points,
)


@dataclass
class PluginRegistry:
    """Minimal instance-based registry for plugin objects."""

    _by_name: dict[str, BasePlugin] = field(default_factory=dict)

    def register(self, plugin: BasePlugin, *, override: bool = False) -> None:
        key = plugin.name().lower()
        if not override and key in self._by_name:
            # Log debug message for duplicate registration but don't raise
            logger.debug(f"Plugin '{key}' already registered, skipping duplicate")
            return
        self._by_name[key] = plugin

    def get(self, name: str) -> BasePlugin | None:
        return self._by_name.get(name.lower())

    def all(self) -> list[BasePlugin]:
        return list(self._by_name.values())

    def discover(self, group: str = DEFAULT_GROUP) -> int:
        """Discover entry-point plugins and register them."""

        count = 0
        for ep in _iter_entry_points(group):
            plugin: BasePlugin | None = None
            with suppress(Exception):  # pragma: no cover - best effort
                _activate_editable_distribution(ep)
                candidate = ep.load()
                resolved = candidate() if isinstance(candidate, type) else candidate
                if isinstance(resolved, BasePlugin):
                    plugin = resolved
            if plugin is None:
                continue
            # register() now handles deduplication internally
            self.register(plugin)
            # Only count if actually added (not a duplicate)
            if plugin.name().lower() in self._by_name:
                count += 1
        return count


_REGISTRY = PluginRegistry()


def _register_example(plugin_cls: type[BasePlugin] | None) -> None:
    if plugin_cls is None:
        return
    with suppress(Exception):
        _REGISTRY.register(plugin_cls())


@lru_cache(maxsize=1)
def _bootstrap_examples() -> None:
    try:
        from examples.plugins.hello_plugin import HelloPlugin
    except (ImportError, AttributeError):  # pragma: no cover - optional example absent

        class HelloPlugin(BasePlugin):  # type: ignore[no-redef]
            def version(self) -> str:
                return "0.0.0"

            def activate(self, app_ctx=None) -> None:
                _ = app_ctx
                return

    try:
        from examples.plugins.metrics_token_accuracy_plugin import (
            TokenAccuracyPlugin,
        )
    except (ImportError, AttributeError):  # pragma: no cover - optional example absent

        class TokenAccuracyPlugin(BasePlugin):  # type: ignore[no-redef]
            def version(self) -> str:
                return "0.0.0"

            def activate(self, app_ctx=None) -> None:
                _ = app_ctx
                return

    _register_example(HelloPlugin)
    _register_example(TokenAccuracyPlugin)


def registry() -> PluginRegistry:
    _bootstrap_examples()
    return _REGISTRY


__all__ = ["PluginRegistry", "registry"]
