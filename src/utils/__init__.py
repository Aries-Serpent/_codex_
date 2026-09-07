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

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ROOT_UTILS = _ROOT / "utils"
if _ROOT_UTILS.exists():
    __path__ = [str(Path(__file__).resolve().parent), str(_ROOT_UTILS)]

from .checkpointing import (
    CheckpointManager,
    dump_rng_state,
    load_rng_state,
    set_seed,
)
from .training_callbacks import EarlyStopping

__all__ = [
    "CheckpointManager",
    "EarlyStopping",
    "dump_rng_state",
    "load_rng_state",
    "set_seed",
]
