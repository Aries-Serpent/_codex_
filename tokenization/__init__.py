"""Tokenization API re-exported from :mod:`codex_ml.tokenization`."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

_pkg_dir = Path(__file__).resolve().parent
_root_src = _pkg_dir.parent / "src"
if _root_src.exists():
    root_src_str = str(_root_src)
    if root_src_str not in sys.path:
        sys.path.insert(0, root_src_str)

_pkg_src = _root_src / "tokenization"
if _pkg_src.exists():
    pkg_src_str = str(_pkg_src)
    pkg_path = globals().get("__path__")
    if pkg_path is not None and pkg_src_str not in pkg_path:
        pkg_path.append(pkg_src_str)

try:
    from codex_ml.tokenization import TokenizerAdapter, load_tokenizer, register_tokenizer
except Exception as exc:  # pragma: no cover - only when codex_ml is unavailable
    raise ImportError(
        "codex_ml.tokenization is unavailable; install the codex-ml package or "
        "run from the repository root so 'src' is on sys.path."
    ) from exc

__all__ = ["TokenizerAdapter", "load_tokenizer", "register_tokenizer"]

_OPTIONAL_SUBMODULES = ("sentencepiece_adapter", "train_tokenizer", "cli", "api")


def __getattr__(name: str) -> Any:  # pragma: no cover - shim for optional imports
    if name in _OPTIONAL_SUBMODULES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        if name not in __all__:
            __all__.append(name)
        return module
    raise AttributeError(name)
