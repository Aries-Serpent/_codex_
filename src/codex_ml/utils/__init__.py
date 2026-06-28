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

from . import (
    checkpoint_core,
    checkpointing,
    error_log,
)

try:  # pragma: no cover - optional torch dependency
    from . import modeling
except (ImportError, OSError, AttributeError):  # pragma: no cover - allow utilities without torch
    modeling = None  # type: ignore[assignment]
from . import provenance
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
