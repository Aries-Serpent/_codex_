"""Compatibility shim for the legacy :mod:`codex_task_sequence` module.

This module preserves the historical import path for the task sequence CLI
after it was relocated to :mod:`cli.task_sequence`. Downstream tools and tests
that import :mod:`codex_task_sequence` continue to function without change.
"""

from __future__ import annotations

from importlib import import_module

_implementation_module = import_module("cli.task_sequence")

__doc__ = _implementation_module.__doc__

if hasattr(_implementation_module, "__all__"):
    _export_names = list(_implementation_module.__all__)  # type: ignore[attr-defined]
else:
    _export_names = [name for name in dir(_implementation_module) if not name.startswith("_")]

_globals = globals()
for name in _export_names:
    _globals[name] = getattr(_implementation_module, name)

__all__ = _export_names
implementation_module = "cli.task_sequence"

# Provide access to the underlying module for advanced callers.
module = _implementation_module
