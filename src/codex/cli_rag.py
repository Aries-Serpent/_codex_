"""Compatibility wrapper for the legacy `codex.cli_rag` entry point."""

from __future__ import annotations

import importlib
import sys

_target = importlib.import_module("aries_serpent_core.cli_rag")

# Alias the active implementation in place so patch targets like
# `codex.cli_rag.RAGRetriever` and `codex.rag.build_index_from_files` refer to
# the same objects the runtime uses.
sys.modules[__name__] = _target
__all__ = list(getattr(_target, "__all__", []))

for _name in dir(_target):
    if _name.startswith("__") and _name.endswith("__"):
        continue
    globals()[_name] = getattr(_target, _name)
