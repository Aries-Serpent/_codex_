"""Core registry infrastructure with entry-point based extension discovery.

The registry system underpins Codex' pluggable components.  Each registry is
responsible for a specific component type (models, tokenizers, metrics, data
loaders, trainers) and provides a uniform interface for registering and
retrieving implementations.  Key features:

* **Explicit registration** via decorator or direct function call.
* **Collision detection** with detailed diagnostics and optional overrides.
* **Entry point discovery** leveraging :mod:`importlib.metadata` so third party
  packages can contribute components without modifying core code.
* **Lazy loading** of entry points only when a component is requested.

This module is intentionally self-contained to avoid circular dependencies in
component packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import Any, Dict, Iterator, Mapping, Optional


class RegistryError(RuntimeError):
    """Base exception for registry operations."""


class RegistryNotFoundError(RegistryError):
    """Raised when a requested key does not exist in the registry."""


class RegistryConflictError(RegistryError):
    """Raised when attempting to register a duplicate key without override."""


class RegistryLoadError(RegistryError):
    """Raised when loading a component from an entry point fails."""


@dataclass(frozen=True)
class _RegistryEntry:
    """Internal structure capturing a registry entry and its provenance."""

    name: str
    value: Any
    source: str


class Registry:
    """Registry mapping names to callables/classes with plugin discovery."""

    def __init__(
        self,
        component: str,
        *,
        entry_point_group: str | None = None,
        allow_entrypoint_overrides: bool = False,
    ) -> None:
        self._component = component
        self._entry_point_group = entry_point_group
        self._allow_entrypoint_overrides = allow_entrypoint_overrides
        self._items: Dict[str, _RegistryEntry] = {}
        self._entry_points_loaded = False
        self._failed_entry_points: Dict[str, Exception] = {}

    # ------------------------------------------------------------------
    # Registration API
    # ------------------------------------------------------------------
    def register(
        self,
        name: str,
        obj: Optional[Any] = None,
        *,
        override: bool = False,
        source: str | None = None,
    ) -> Any:
        """Register ``obj`` under ``name``.

        Can be used as a decorator::

            @registry.register("toy")
            class Toy: ...

        Or as a function call::

            registry.register("toy", Toy)

        Parameters
        ----------
        name:
            Registry key for the object.
        obj:
            Object to register.  When omitted, a decorator is returned.
        override:
            Allow replacing an existing registration.  Useful for tests and
            deliberate overrides.  Defaults to ``False`` which raises
            :class:`RegistryConflictError` on duplicates.
        source:
            Optional provenance marker stored alongside the object.  Defaults to
            ``"local"`` for explicit registrations.
        """

        def decorator(target: Any) -> Any:
            key = self._normalise(name)
            self._register(key, target, override=override, source=source or "local")
            return target

        if obj is not None:
            return decorator(obj)
        return decorator

    def _register(self, name: str, obj: Any, *, override: bool, source: str) -> None:
        existing = self._items.get(name)
        if existing and not override:
            raise RegistryConflictError(
                f"Duplicate registration for {self._component!r} '{name}'. "
                f"Existing source: {existing.source}, new source: {source}."
            )
        self._items[name] = _RegistryEntry(name=name, value=obj, source=source)

    # ------------------------------------------------------------------
    # Lookup API
    # ------------------------------------------------------------------
    def get(self, name: str) -> Any:
        """Retrieve an object by name, performing entry point discovery."""

        key = self._normalise(name)
        if key in self._items:
            return self._items[key].value

        self._ensure_entry_points_loaded()

        if key in self._items:
            return self._items[key].value

        if key in self._failed_entry_points:
            exc = self._failed_entry_points[key]
            raise RegistryLoadError(
                f"Failed to load {self._component!r} '{name}' from entry point: {exc}"
            ) from exc

        suggestions = ", ".join(sorted(self._items)) or "<empty>"
        raise RegistryNotFoundError(
            f"Unknown {self._component!r} '{name}'. Available: {suggestions}"
        )

    def list(self) -> list[str]:
        """Return the sorted list of registered names (post discovery)."""

        self._ensure_entry_points_loaded()
        return sorted(self._items.keys())

    # ------------------------------------------------------------------
    # Entry point handling
    # ------------------------------------------------------------------
    def _ensure_entry_points_loaded(self) -> None:
        if self._entry_points_loaded or not self._entry_point_group:
            return

        try:
            eps = metadata.entry_points(group=self._entry_point_group)
        except Exception:  # pragma: no cover - metadata backend failure
            eps = ()

        for ep in eps:
            key = self._normalise(ep.name)
            if key in self._items and not self._allow_entrypoint_overrides:
                continue
            try:
                value = ep.load()
            except Exception as exc:  # pragma: no cover - plugin failure
                self._failed_entry_points[key] = exc
                continue
            try:
                self._register(
                    key,
                    value,
                    override=self._allow_entrypoint_overrides,
                    source=f"entry_point:{ep.value}",
                )
            except RegistryConflictError as conflict:
                # Preserve the conflict details but continue scanning.
                self._failed_entry_points[key] = conflict
        self._entry_points_loaded = True

    # ------------------------------------------------------------------
    # Context manager / helper utilities
    # ------------------------------------------------------------------
    def temporarily_registered(self, items: Mapping[str, Any]) -> Iterator[None]:
        """Context manager to temporarily register items (mainly for tests)."""

        from contextlib import contextmanager

        @contextmanager
        def manager() -> Iterator[None]:
            original = {}
            try:
                for key, value in items.items():
                    norm = self._normalise(key)
                    original[norm] = self._items.get(norm)
                    self._register(norm, value, override=True, source="temporary")
                yield
            finally:
                for key in items:
                    norm = self._normalise(key)
                    if original[norm] is None:
                        self._items.pop(norm, None)
                    else:
                        self._items[norm] = original[norm]

        return manager()

    def _normalise(self, name: str) -> str:
        return name.lower()


__all__ = [
    "Registry",
    "RegistryError",
    "RegistryConflictError",
    "RegistryNotFoundError",
    "RegistryLoadError",
]
