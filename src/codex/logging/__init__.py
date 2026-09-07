"""Codex logging compatibility module.

This module provides backward compatibility by re-exporting from
``aries_serpent_core.logging`` while preserving the legacy ``codex.logging``
import namespace used by the test suite.
"""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "logging"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.logging import *  # noqa: F401, F403
from aries_serpent_core.logging.adapter import (
    LoggerAdapter,
    NullLogger,
    get_default_logger,
    set_default_logger,
)

from . import session_logger as session_logger
from . import structured_logger as structured_logger

__all__ = [
    "LoggerAdapter",
    "NullLogger",
    "get_default_logger",
    "set_default_logger",
    "session_logger",
    "structured_logger",
]
