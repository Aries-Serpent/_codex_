"""Compatibility shim for the legacy `codex.rag` import path.

This module re-exports the active `aries_serpent_core.rag` implementation so
legacy imports remain stable while the runtime continues using the modern
package layout.
"""

from __future__ import annotations

import importlib
import sys

_target = importlib.import_module("aries_serpent_core.rag")

# Ensure legacy imports resolve to the same module object as the active
# implementation so monkeypatching `codex.rag.*` affects the live runtime.
sys.modules[__name__] = _target
__doc__ = _target.__doc__
__package__ = getattr(_target, "__package__", __name__.split(".")[0])
__spec__ = getattr(_target, "__spec__", None)
__all__ = list(getattr(_target, "__all__", []))
__path__ = list(getattr(_target, "__path__", []))

for _name in dir(_target):
    if _name.startswith("__") and _name.endswith("__"):
        continue
    globals()[_name] = getattr(_target, _name)
