"""Shim to src/codex_ml.utils.checkpointing."""

from __future__ import annotations

import importlib.util
import pathlib
import types

_src = (
    pathlib.Path(__file__).resolve().parents[2] / "src" / "codex_ml" / "utils" / "checkpointing.py"
)
_spec = importlib.util.spec_from_file_location("codex_ml._src_checkpointing", _src)
if _spec is None or _spec.loader is None:  # pragma: no cover - defensive guard
    raise ImportError(f"Unable to load codex_ml.utils.checkpointing from {_src!s}")
_module = importlib.util.module_from_spec(_spec)
assert isinstance(_module, types.ModuleType)
_spec.loader.exec_module(_module)
__all__ = getattr(_module, "__all__", [])
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
