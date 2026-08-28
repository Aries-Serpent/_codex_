"""Compatibility shim for the legacy ``data.datasets`` import path."""

from __future__ import annotations

import sys
from pathlib import Path

_src_path = Path(__file__).resolve().parent.parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

import importlib

_module = importlib.import_module("src.data.datasets")
for _name in dir(_module):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_module, _name)

__all__ = list(getattr(_module, "__all__", []))
