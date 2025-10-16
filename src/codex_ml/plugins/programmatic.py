from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field

from .base import BasePlugin
from .registry import DEFAULT_GROUP, _activate_editable_distribution, _iter_entry_points


@dataclass
class PluginRegistry:
    """Minimal instance-based registry for plugin objects."""

    _by_name: dict[str, BasePlugin] = field(default_factory=dict)

    def register(self, plugin: BasePlugin, *, override: bool = False) -> None:
        key = plugin.name().lower()
        if not override and key in self._by_name:
            raise ValueError(f"plugin already registered: {key}")
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
            try:
                self.register(plugin)
            except ValueError:
                continue
            count += 1
        return count


_REGISTRY = PluginRegistry()
_BOOTSTRAPPED = False


def _register_example(plugin_cls: type[BasePlugin] | None) -> None:
    if plugin_cls is None:
        return
    with suppress(Exception):
        _REGISTRY.register(plugin_cls())


def _bootstrap_examples() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    try:
        from examples.plugins.hello_plugin import HelloPlugin  # type: ignore
    except Exception:  # pragma: no cover - optional example absent

        class HelloPlugin(BasePlugin):
            def name(self) -> str:
                return "hello"

            def version(self) -> str:
                return "0.0.0"

            def activate(self, app_ctx=None) -> None:
                return

    try:
        from examples.plugins.metrics_token_accuracy_plugin import (
            TokenAccuracyPlugin,  # type: ignore
        )
    except Exception:  # pragma: no cover - optional example absent

        class TokenAccuracyPlugin(BasePlugin):
            def name(self) -> str:
                return "token-accuracy-plugin"

            def version(self) -> str:
                return "0.0.0"

            def activate(self, app_ctx=None) -> None:
                return

    _register_example(HelloPlugin)  # type: ignore[arg-type]
    _register_example(TokenAccuracyPlugin)  # type: ignore[arg-type]

    _BOOTSTRAPPED = True


def registry() -> PluginRegistry:
    _bootstrap_examples()
    return _REGISTRY


__all__ = ["PluginRegistry", "registry"]
