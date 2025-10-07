"""Shim to src/codex_ml/cli/main.py.

This keeps local imports in sync with the packaged module when the repository
root shadows the installed package on ``sys.path``.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType

_root = pathlib.Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_src = _root / "src" / "codex_ml" / "cli" / "main.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("codex_ml._src_cli_main", _src)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load codex_ml.cli.main from {_src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_module = _load()
__all__ = getattr(_module, "__all__", [])
globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})
