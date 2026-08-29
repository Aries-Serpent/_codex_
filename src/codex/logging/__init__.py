"""Codex logging compatibility module.

This module provides backward compatibility by re-exporting from aries_serpent_core.logging.
"""

from aries_serpent_core.logging import *  # noqa: F401, F403
from aries_serpent_core.logging.adapter import get_default_logger

from . import session_logger as session_logger

__all__ = [
    "get_default_logger",
    "session_logger",
]
