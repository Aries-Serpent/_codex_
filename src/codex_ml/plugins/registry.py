"""Lightweight plugin registry with optional entry-point discovery."""

from __future__ import annotations

# ``entry_points`` is accessed dynamically so tests can monkeypatch
import importlib.metadata as _importlib_metadata
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple


def _norm(name: str) -> str:
    """Normalize plugin names (case-insensitive, hyphen tolerant)."""
    return name.lower().replace("-", "_")


@dataclass
class _Item:
    obj: Any
    meta: Dict[str, Any]


class Registry:
    """In-process registry supporting entry-point loading."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._items: Dict[str, _Item] = {}
        self._ep_loaded: Dict[str, bool] = {}

    # ------------------------------------------------------------------
    def register(self, name: str, **meta: Any) -> Callable[[Any], Any]:
        key = _norm(name)

        def deco(obj: Any) -> Any:
            # Local registrations take precedence over entry points
            self._items[key] = _Item(obj=obj, meta={"name": key, **meta})
            return obj

        return deco

    # ------------------------------------------------------------------
    def get(self, name: str) -> _Item | None:
        return self._items.get(_norm(name))

    def names(self) -> list[str]:
        return sorted(self._items.keys())

    def clear(self) -> None:
        self._items.clear()
        self._ep_loaded.clear()

    # ------------------------------------------------------------------
    def load_from_entry_points(
        self, group: str, require_api: str | None = None
    ) -> Tuple[int, Dict[str, str]]:
        """Load plugins from entry points.

        Returns a tuple of (count, errors) where errors maps entry point names to
        failure reasons. Local registrations always take precedence.
        """

        errors: Dict[str, str] = {}
        try:
            eps = _importlib_metadata.entry_points().select(group=group)
        except Exception as exc:  # pragma: no cover - platform variation
            return 0, {"<entry_points>": str(exc)}
        count = 0
        for ep in eps:
            if ep.name in self._ep_loaded:
                continue
            key = _norm(ep.name)
            if key in self._items:
                # Local registration overrides entry point
                self._ep_loaded[ep.name] = True
                continue
            try:
                obj = ep.load()
                api = getattr(obj, "__codex_ext_api__", None)
                if require_api and api != require_api:
                    errors[ep.name] = f"incompatible api: {api} != {require_api}"
                    continue
                self._items[key] = _Item(
                    obj=obj,
                    meta={"entry_point": group, "module": ep.value, "name": key},
                )
                self._ep_loaded[ep.name] = True
                count += 1
            except Exception as exc:  # pragma: no cover - plugin failure
                errors[ep.name] = str(exc)
        return count, errors

    # ------------------------------------------------------------------
    def resolve_and_instantiate(self, name: str, *args: Any, **kwargs: Any) -> Any:
        item = self.get(name)
        if not item:
            raise KeyError(f"{self.name}: plugin '{name}' not found; available: {self.names()}")
        obj = item.obj
        if not callable(obj):
            raise TypeError(f"{self.name}: registered object for '{name}' is not callable")
        return obj(*args, **kwargs)
