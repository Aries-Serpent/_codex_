"""Compatibility shim for the legacy :mod:`codex_task_sequence` module.

This module preserves the historical import path for the task sequence CLI
after it was relocated to :mod:`cli.task_sequence`. Downstream tools and tests
that import :mod:`codex_task_sequence` continue to function without change.
"""

from __future__ import annotations

from importlib import import_module

_implementation_module = import_module("cli.task_sequence")

__doc__ = _implementation_module.__doc__

_globals = globals()
_implementation_attrs = vars(_implementation_module)

for _name, _value in _implementation_attrs.items():
    if _name.startswith("__") and _name.endswith("__"):
        continue
    _globals[_name] = _value

if "__all__" in _implementation_attrs:
    __all__ = list(_implementation_attrs["__all__"])
else:
    __all__ = [name for name in _implementation_attrs if not name.startswith("_")]
implementation_module = "cli.task_sequence"

# Provide access to the underlying module for advanced callers.
module = _implementation_module
