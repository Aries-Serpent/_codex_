"""Lightweight compatibility shims for legacy ``codex_ml`` imports.

This package provides minimal implementations of the modules that were
historically bundled with the training stack.  The goal is to keep the
public training entry points importable without pulling in heavyweight
runtime dependencies.  The shims favour simple, well-documented behaviour
so downstream examples continue to execute in constrained environments.
"""

from __future__ import annotations

__all__ = [
    "logging",
    "monitoring",
    "telemetry",
    "utils",
]
