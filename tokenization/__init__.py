"""Shims to make the tokenization package importable without installation."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
_root_src = _pkg_dir.parent / "src"
if _root_src.exists():
    root_src_str = str(_root_src)
    if root_src_str not in sys.path:
        sys.path.insert(0, root_src_str)

_pkg_src = _root_src / "tokenization"
if _pkg_src.exists():
    pkg_src_str = str(_pkg_src)
    if pkg_src_str not in __path__:
        __path__.append(pkg_src_str)

__all__: list[str] = []
_OPTIONAL_SUBMODULES = ("sentencepiece_adapter", "train_tokenizer")


def __getattr__(name: str):  # pragma: no cover - shim for optional imports
    if name in _OPTIONAL_SUBMODULES:
        try:
            module = importlib.import_module(f"{__name__}.{name}")
        except ModuleNotFoundError:
            globals()[name] = None
            return None
        else:
            globals()[name] = module
            if name not in __all__:
                __all__.append(name)
            return module
    raise AttributeError(name)
