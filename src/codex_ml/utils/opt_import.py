"""Helper for optional imports with explicit logging."""

from __future__ import annotations

import logging
from importlib import import_module
from types import ModuleType

LOGGER = logging.getLogger(__name__)


def try_import(name: str) -> ModuleType | None:
    """Attempt to import ``name`` and return ``None`` when unavailable."""

    try:
        return import_module(name)
    except (ImportError, AttributeError) as exc:  # pragma: no cover - optional dependency
        LOGGER.debug("Optional dependency %s could not be imported: %s", name, exc)
        return None


__all__ = ["try_import"]
