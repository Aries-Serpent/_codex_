"""Entry-point plugin loader utilities."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

try:
    from importlib import metadata
except Exception:  # pragma: no cover - importlib metadata not available
    metadata = None  # type: ignore[assignment]

RegisterFn = Callable[..., Any]


def _iter_entry_points(group: str) -> Iterable[Any]:
    """Return iterable of entry points for *group* or an empty tuple."""

    if metadata is None:  # pragma: no cover - fallback for very old Python
        return ()

    try:
        return metadata.entry_points(group=group)
    except TypeError:
        # Python <3.10 compatibility: entry_points() returns dict-like object
        try:
            eps = metadata.entry_points()
        except Exception:
            return ()
        if hasattr(eps, "select"):
            return eps.select(group=group)
        return [ep for ep in eps if getattr(ep, "group", None) == group]
    except Exception:
        return ()


def _call_plugin_hook(target: Any, register: Optional[RegisterFn]) -> bool:
    """Invoke plugin hook if *target* exposes a register-style API."""

    if register is None:
        return False

    hook = getattr(target, "register", None)
    if callable(hook):
        try:
            hook(register)
            return True
        except Exception:
            return False

    if callable(target):
        try:
            target(register)
            return True
        except TypeError:
            return False
        except Exception:
            return False

    return False


def _register_direct(register: Optional[RegisterFn], name: str, target: Any) -> bool:
    """Attempt direct registration via ``register`` for the given entry point."""

    if register is None:
        return False

    try:
        register(name, target)
        return True
    except TypeError:
        try:
            decorator = register(name)
            decorator(target)
            return True
        except Exception:
            return False
    except Exception:
        return False


def load_plugins(group: str, *, register: Optional[RegisterFn] = None) -> int:
    """Best-effort load of entry-point plugins for ``group``.

    The loader understands two plugin styles:

    * A callable accepting a ``register`` function to perform custom
      registrations.
    * A module (or object) exposing a ``register(register_fn)`` attribute.

    When a callable or module does not implement one of the above conventions,
    the loader falls back to direct registration via ``register(entrypoint,
    obj)`` when a ``register`` function is provided.  All exceptions are
    swallowed so plugin discovery cannot break the host application.

    Returns the number of successfully invoked plugin registrations.
    """

    loaded = 0
    for ep in _iter_entry_points(group):
        try:
            target = ep.load()
        except Exception:
            continue

        if _call_plugin_hook(target, register):
            loaded += 1
            continue

        if _register_direct(register, getattr(ep, "name", ""), target):
            loaded += 1

    return loaded


__all__ = ["load_plugins"]
