"""Shim to src/codex_ml/config.py for editable checkouts."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType

_repo_root = pathlib.Path(__file__).resolve().parents[1]
_src_root = _repo_root / "src"
if _src_root.exists():
    src_str = str(_src_root)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

_SRC = _src_root / "codex_ml" / "config.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("codex_ml._src_config", _SRC)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load codex_ml.config from {_SRC}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_module = _load()
__all__ = getattr(_module, "__all__", [])
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
