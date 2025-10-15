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


def registry() -> PluginRegistry:
    return _REGISTRY


__all__ = ["PluginRegistry", "registry"]
