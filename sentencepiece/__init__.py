"""Stub shim for optional dependency ``sentencepiece``.

The module provides a transparent pass-through to the real library when
available while keeping the offline developer flow unblocked when it is not
installed.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_real_module() -> ModuleType | None:
    current_path = Path(__file__).resolve()
    current_dir = current_path.parent
    search_paths = [p for p in sys.path if Path(p).resolve() != current_dir]
    spec = importlib.machinery.PathFinder().find_spec("sentencepiece", search_paths)
    if spec is None or spec.loader is None:
        return None
    origin = getattr(spec, "origin", None)
    if origin and Path(origin).resolve() == current_path:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[__name__] = module
    spec.loader.exec_module(module)
    return module


_real = _load_real_module()

if _real is not None:
    globals().update({k: getattr(_real, k) for k in dir(_real) if not k.startswith("__")})
    __all__ = [k for k in dir(_real) if not k.startswith("__")]
else:  # pragma: no cover - exercised in minimal test envs
    __all__ = []
    __path__ = []  # type: ignore[assignment]
