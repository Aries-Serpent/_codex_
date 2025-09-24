"""Shim to src/codex_ml tracking utilities to avoid drift."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType

_src = (
    pathlib.Path(__file__).resolve().parents[2]
    / "src"
    / "codex_ml"
    / "tracking"
    / "mlflow_utils.py"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("codex_ml._src_mlflow_utils", _src)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load codex_ml.tracking.mlflow_utils from {_src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_module = _load()
__all__ = getattr(_module, "__all__", [])
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
