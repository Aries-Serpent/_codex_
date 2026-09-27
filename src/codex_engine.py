"""Backward-compatible import alias for the legacy ``codex_engine`` module name.

The Rust extension is built as ``codex_swarm`` for the current package, but the
historical Python import surface still uses ``codex_engine`` in tests and docs.
This shim keeps both import paths working without forcing a broad migration.
"""

from __future__ import annotations

from codex_swarm import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
