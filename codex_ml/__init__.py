"""Repository shim exposing the ``src/codex_ml`` package when running from a checkout."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_DIR.parent
_SRC_ROOT = _REPO_ROOT / "src"
_IMPL_PATH = _SRC_ROOT / "codex_ml" / "__init__.py"

if _SRC_ROOT.exists():
    src_str = str(_SRC_ROOT)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

if _IMPL_PATH.exists():
    spec = importlib.util.spec_from_file_location(__name__, _IMPL_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise ImportError(f"Unable to load codex_ml implementation from {_IMPL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    sys.modules[__name__] = module
    globals().update(module.__dict__)
else:  # pragma: no cover - installed distributions provide the actual package
    __all__: list[str] = []
