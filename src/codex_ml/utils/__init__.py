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
import logging
logger = logging.getLogger(__name__)
"""Utility helpers and modules re-exported for convenience."""


from . import (
    checkpoint_core,  # noqa: F401
    checkpointing,  # noqa: F401
    error_log,  # noqa: F401
)

try:  # pragma: no cover - optional torch dependency
    from . import modeling  # noqa: F401
except Exception:  # pragma: no cover - allow utilities without torch
    modeling = None  # type: ignore[assignment]
from . import provenance  # noqa: F401
from .atomic_io import safe_write_bytes, safe_write_text  # noqa: F401
from .checkpointing import CheckpointManager  # noqa: F401
from .provenance import environment_summary  # noqa: F401
from .repro import (  # noqa: F401
    record_dataset_checksums,
    restore_rng_state,
    set_deterministic,
    set_seed,
    snapshot_rng_state,
)
from .seed import deterministic_shuffle  # noqa: F401
from .seeding import set_reproducible  # noqa: F401
from .storage import FSSpecStorage, StorageProvider  # noqa: F401

__all__ = [
    "CheckpointManager",
    "checkpoint_core",
    "checkpointing",
    "error_log",
    "modeling",
    "provenance",
    "environment_summary",
    "deterministic_shuffle",
    "set_reproducible",
    "set_deterministic",
    "set_seed",
    "snapshot_rng_state",
    "restore_rng_state",
    "record_dataset_checksums",
    "safe_write_bytes",
    "safe_write_text",
    "FSSpecStorage",
    "StorageProvider",
]
