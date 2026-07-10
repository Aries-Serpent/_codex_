"""Codex logging adapter compatibility module.

This module provides backward compatibility by re-exporting from aries_serpent_core.logging.adapter.
"""

from aries_serpent_core.logging.adapter import get_default_logger

__all__ = [
    "get_default_logger",
]
