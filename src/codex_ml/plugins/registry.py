"""Plugin registry utilities.

This module exposes a lightweight `Registry` class for runtime registration
and discovery helpers that load plugins from Python entry points.

Public API:
    class Registry
    discover(group: str = "codex_ml.plugins") -> dict[str, object]
    get(name: str, group: str = "codex_ml.plugins") -> object | None
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import re  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from importlib import import_module as _import_module  # noqa: E402
from importlib import invalidate_caches as _invalidate_caches  # noqa: E402
from importlib import metadata  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

DEFAULT_GROUP = "codex_ml.plugins"

# Matches only simple `import a.b.c` — no semicolons, no commas.
# Used to safely handle .pth bootstrap lines without evaluating arbitrary code.
_SIMPLE_IMPORT_RE = re.compile(r"^import\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")


# ---------------------------------------------------------------------------
# Internal helpers


def _iter_entry_points(group: str) -> tuple[Any, ...]:
    """Return iterable of entry points for ``group`` with fallbacks."""

    _invalidate_caches()
    collected: list[Any] = []
    try:
        items = metadata.entry_points(group=group)
    except TypeError:  # pragma: no cover - older importlib
        eps = metadata.entry_points()
        items = (
            eps.select(group=group)  # type: ignore[assignment]
            if hasattr(eps, "select")
            else [ep for ep in eps if ep.group == group]
        )
    except (ValueError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        items = []  # type: ignore[assignment]
    collected.extend(items)
    try:  # pragma: no cover - best effort fallback
        for dist in metadata.distributions():
            for ep in getattr(dist, "entry_points", ()):
                if getattr(ep, "group", None) == group:
                    collected.append(ep)
    except (ValueError, TypeError, RuntimeError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
    unique: dict[tuple[str, str], Any] = {}
    for ep in collected:
        key = (getattr(ep, "name", ""), getattr(ep, "value", ""))
        if key not in unique:
            unique[key] = ep
    return tuple(unique.values())


def _activate_editable_distribution(ep: Any) -> None:
    """Ensure editable distribution paths are on ``sys.path`` before loading."""

    dist = getattr(ep, "dist", None)
    if dist is None:
        return
    try:
        files = dist.files or ()
    except (IOError, OSError):  # pragma: no cover - defensive
        return
    for file in files:
        if not str(file).endswith(".pth") or "__editable__" not in str(file):
            continue
        try:
            pth_path = Path(dist.locate_file(file))
            lines = pth_path.read_text(encoding="utf-8").splitlines()
        except (IOError, OSError):  # pragma: no cover - best effort  # nosec B112
            continue
        for line in lines:
            entry = line.strip()
            if not entry or entry.startswith("#"):
                continue
            if entry.startswith("import "):
                match = _SIMPLE_IMPORT_RE.match(entry)
                if match:
                    try:
                        _import_module(match.group(1))  # pragma: no cover - .pth bootstrap
                    except (IOError, OSError) as e:  # pragma: no cover
                        logger.debug("import_module(%r) failed: %s", match.group(1), e)
                else:
                    # Complex .pth lines (e.g. chained statements) are skipped to
                    # avoid dynamic code evaluation. In practice editable-install
                    # .pth files only emit simple `import <name>` lines.
                    logger.debug("Skipping complex .pth import line: %r", entry)
                continue
            if entry not in sys.path:
                sys.path.insert(0, entry)


# ---------------------------------------------------------------------------
# Runtime registration registry


@dataclass
class _Item:
    name: str
    obj: Any
    meta: dict[str, Any]


class Registry:
    """Simple case-insensitive registry with optional entry-point loading."""

    def __init__(self, kind: str = "plugins") -> None:
        self.kind = kind
        self._items: dict[str, _Item] = {}

    def register(self, name: str, **meta: Any) -> Any:
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
    ) -> tuple[int, dict[str, str]]:
        """Load entry points into the registry.

        Returns a tuple of (loaded_count, errors).
        Each entry point object may define ``__codex_api__`` (or legacy
        ``__codex_ext_api__``); if provided and it does not match
        ``require_api`` the plugin is skipped.
        """

        count = 0
        errors: dict[str, str] = {}
        items = _iter_entry_points(group)
        if not items:
            return count, errors
        for ep in items:
            try:
                _activate_editable_distribution(ep)
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
        return count, errors


# ---------------------------------------------------------------------------
# Entry point helpers (stateless)


def discover(group: str = DEFAULT_GROUP) -> dict[str, object]:
    """Return mapping of {name: object} for the entry point group."""

    results: dict[str, object] = {}
    items = _iter_entry_points(group)
    if not items:
        return {}
    for ep in items:
        try:
            _activate_editable_distribution(ep)
            results[ep.name] = ep.load()
        except (ValueError, TypeError):  # pragma: no cover - skip broken entry points  # nosec B112
            continue
    return results


def get(name: str, group: str = DEFAULT_GROUP) -> object | None:
    """Return a single entry point object by name, or None if missing."""

    return discover(group).get(name)


__all__ = ["Registry", "discover", "get"]
