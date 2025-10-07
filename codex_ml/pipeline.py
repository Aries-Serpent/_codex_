"""Shim to src/codex_ml/pipeline.py for editable checkouts.

This mirrors the approach used for the CLI module so that the
installed package and repository tree expose the same interfaces
without requiring `pip install -e .`.
"""

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

_src = _src_root / "codex_ml" / "pipeline.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("codex_ml._src_pipeline", _src)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load codex_ml.pipeline from {_src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_module = _load()
__all__ = getattr(_module, "__all__", [])
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
