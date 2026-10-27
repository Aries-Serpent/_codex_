"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from utils.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import checkpoint_core, checkpointing, error_log, modeling, provenance
    from .atomic_io import safe_write_bytes, safe_write_text
    from .checkpointing import CheckpointManager
    from .provenance import environment_summary
    from .repro import (
        record_dataset_checksums,
        restore_rng_state,
        set_deterministic,
        set_seed,
        snapshot_rng_state,
    )
    from .seed import deterministic_shuffle
    from .seeding import set_reproducible
    from .storage import FSSpecStorage, StorageProvider

_EXPORTS = {
    "CheckpointManager": ("checkpointing", "CheckpointManager"),
    "FSSpecStorage": ("storage", "FSSpecStorage"),
    "StorageProvider": ("storage", "StorageProvider"),
    "checkpoint_core": ("checkpoint_core", None),
    "checkpointing": ("checkpointing", None),
    "deterministic_shuffle": ("seed", "deterministic_shuffle"),
    "environment_summary": ("provenance", "environment_summary"),
    "error_log": ("error_log", None),
    "modeling": ("modeling", None),
    "provenance": ("provenance", None),
    "record_dataset_checksums": ("repro", "record_dataset_checksums"),
    "restore_rng_state": ("repro", "restore_rng_state"),
    "safe_write_bytes": ("atomic_io", "safe_write_bytes"),
    "safe_write_text": ("atomic_io", "safe_write_text"),
    "set_deterministic": ("repro", "set_deterministic"),
    "set_reproducible": ("seeding", "set_reproducible"),
    "set_seed": ("repro", "set_seed"),
    "snapshot_rng_state": ("repro", "snapshot_rng_state"),
}


def __getattr__(name: str) -> Any:
    """Resolve utility exports without loading ML backends for unrelated helpers."""
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _EXPORTS[name]
    module = import_module(f".{module_name}", __name__)
    value = getattr(module, attribute) if attribute is not None else module
    globals()[name] = value
    return value


__all__ = [
    "CheckpointManager",
    "FSSpecStorage",
    "StorageProvider",
    "checkpoint_core",
    "checkpointing",
    "deterministic_shuffle",
    "environment_summary",
    "error_log",
    "modeling",
    "provenance",
    "record_dataset_checksums",
    "restore_rng_state",
    "safe_write_bytes",
    "safe_write_text",
    "set_deterministic",
    "set_reproducible",
    "set_seed",
    "snapshot_rng_state",
]
