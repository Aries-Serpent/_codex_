"""
Checkpoint Module

This module provides functionality for checkpoint.

Usage:
    from workers.checkpoint import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# Simple file-based checkpoint helper. Stores processed ids/checksums per input file.
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_checkpoint(path: str) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text()))
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return set()


def save_checkpoint(path: str, seen: set[str]):
    p = Path(path)
    p.write_text(json.dumps(list(seen)))
