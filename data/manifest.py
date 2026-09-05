"""Compatibility shim for the legacy ``data.manifest`` import path."""

from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import importlib

_module = importlib.import_module("src.data.manifest")
for _name in dir(_module):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_module, _name)

__all__ = list(getattr(_module, "__all__", []))
