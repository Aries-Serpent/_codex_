from __future__ import annotations

import importlib
import types


def optional_import(name: str) -> tuple[types.ModuleType | None, bool]:
    """Best-effort dynamic import.

    Returns a tuple of (module, available) where ``module`` is the imported
    module object or ``None`` if the import failed for any reason.
    """
    try:
        return importlib.import_module(name), True
    except Exception:
        return None, False


__all__ = ["optional_import"]
