"""Backward-compatible alias for the legacy ``training.trainer`` import path."""

from __future__ import annotations

import sys

from src.training import trainer as _canonical_trainer

for _name in dir(_canonical_trainer):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_canonical_trainer, _name)

__all__ = getattr(_canonical_trainer, "__all__", [])

# Make ``training.trainer`` and ``src.training.trainer`` the same module object so
# tests patching the legacy import path hit the canonical implementation.
sys.modules[__name__] = _canonical_trainer
