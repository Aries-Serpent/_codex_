"""Plugin registry utilities.

This module exposes a lightweight `Registry` class for runtime registration
and discovery helpers that load plugins from Python entry points.

Public API:
    class Registry
    discover(group: str = "codex_ml.plugins") -> dict[str, object]
    get(name: str, group: str = "codex_ml.plugins") -> object | None
"""

from __future__ import annotations

import importlib
import sys
import warnings
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_GROUP = "codex_ml.plugins"


# ---------------------------------------------------------------------------
# Runtime registration registry


@dataclass
class _Item:
    name: str
    obj: Any
    meta: Dict[str, Any]


class DuplicatePluginWarning(RuntimeWarning):
    """Warning emitted when entry point discovery finds a duplicate."""


def _ensure_editable_paths(ep: metadata.EntryPoint) -> None:
    dist = getattr(ep, "dist", None)
    files = getattr(dist, "files", None)
    if not dist or not files:
        return
    for file in files:
        if not str(file).endswith(".pth"):
            continue
        try:
            target = Path(dist.locate_file(file))
        except Exception:
            continue
        if not target.exists():
            continue
        try:
            content = target.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in content.splitlines():
            candidate = line.strip()
            if not candidate:
                continue
            if candidate.startswith("import "):
                try:
                    exec(candidate, {})
                except Exception:
                    continue
                continue
            if candidate not in sys.path:
                sys.path.append(candidate)


class Registry:
    """Simple case-insensitive registry with optional entry-point loading."""

    def __init__(self, kind: str = "plugins") -> None:
        self.kind = kind
        self._items: Dict[str, _Item] = {}

    def register(self, name: str, **meta: Any):
        """Register `obj` under `name`. Usable as a decorator."""

        def decorator(obj: Any) -> Any:
            key = name.lower()
            self._items[key] = _Item(name=key, obj=obj, meta=dict(meta))
            return obj

        return decorator

    def get(self, name: str) -> Optional[_Item]:
        """Return the registered item for `name` if present."""

        return self._items.get(name.lower())

    def names(self) -> list[str]:
        """List registered names."""

        return list(self._items.keys())

    def resolve_and_instantiate(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Instantiate the registered object by name.

        Supports both class and factory function registrations. Raises
        ``KeyError`` if the name is not registered.
        """

        item = self.get(name)
        if item is None:
            raise KeyError(name)
        obj = item.obj
        if callable(obj):
            return obj(*args, **kwargs)
        return obj

    # Entry point discovery -------------------------------------------------
    def load_from_entry_points(
        self, group: str, require_api: str = "v1"
    ) -> Tuple[int, Dict[str, str]]:
        """Load entry points into the registry.

        Returns a tuple of (loaded_count, errors).
        Each entry point object may define ``__codex_api__`` (or legacy
        ``__codex_ext_api__``); if provided and it does not match
        ``require_api`` the plugin is skipped.
        """

        count = 0
        errors: Dict[str, str] = {}
        try:
            try:
                importlib.invalidate_caches()
            except Exception:
                pass
            try:
                metadata.DistributionFinder.invalidate_caches()  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                items = metadata.entry_points(group=group)
            except TypeError:  # pragma: no cover - older Python fallback
                eps = metadata.entry_points()
                items = (
                    eps.select(group=group)
                    if hasattr(eps, "select")
                    else [ep for ep in eps if ep.group == group]
                )
            for ep in items:
                try:
                    _ensure_editable_paths(ep)
                    obj = ep.load()
                    api = getattr(
                        obj,
                        "__codex_api__",
                        getattr(obj, "__codex_ext_api__", None),
                    )
                    if require_api and api is not None and api != require_api:
                        continue
                    key = ep.name.lower()
                    if key in self._items:
                        warnings.warn(
                            f"duplicate {self.kind} registration: {ep.name}",
                            category=DuplicatePluginWarning,
                            stacklevel=2,
                        )
                        continue
                    self._items[key] = _Item(
                        name=key,
                        obj=obj,
                        meta={"entry_point": ep.name},
                    )
                    count += 1
                except Exception as e:  # pragma: no cover - best effort
                    errors[ep.name] = str(e)
        except Exception:  # pragma: no cover - no entry points
            pass
        return count, errors


# ---------------------------------------------------------------------------
# Entry point helpers (stateless)


def discover(group: str = DEFAULT_GROUP) -> Dict[str, object]:
    """Return mapping of {name: object} for the entry point group."""

    results: Dict[str, object] = {}
    try:
        try:
            importlib.invalidate_caches()
        except Exception:
            pass
        try:
            metadata.DistributionFinder.invalidate_caches()  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            items = metadata.entry_points(group=group)
        except TypeError:  # pragma: no cover - compatibility path
            eps = metadata.entry_points()
            items = (
                eps.select(group=group)
                if hasattr(eps, "select")
                else [ep for ep in eps if ep.group == group]
            )
        for ep in items:
            try:
                _ensure_editable_paths(ep)
                results[ep.name] = ep.load()
            except Exception:  # pragma: no cover - skip broken entry points
                continue
    except Exception:  # pragma: no cover - discovery failure
        return {}
    return results


def get(name: str, group: str = DEFAULT_GROUP) -> object | None:
    """Return a single entry point object by name, or None if missing."""

    return discover(group).get(name)


__all__ = ["Registry", "discover", "get"]
