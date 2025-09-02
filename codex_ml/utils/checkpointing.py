"""Shim to src/codex_ml.utils.checkpointing."""

from __future__ import annotations

import importlib.util
import pathlib

_src = (
    pathlib.Path(__file__).resolve().parents[2] / "src" / "codex_ml" / "utils" / "checkpointing.py"
)
_spec = importlib.util.spec_from_file_location("codex_ml._src_checkpointing", _src)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
