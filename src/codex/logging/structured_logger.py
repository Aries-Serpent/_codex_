"""Backward-compatible legacy import bridge for codex logging.

The repository historically exposed the structured logger under the
``codex.logging.structured_logger`` namespace. The canonical implementation now
lives under ``aries_serpent_core.logging.structured_logger`` and is re-exported
from here so legacy imports continue to work while the package layout is being
migrated.
"""

from aries_serpent_core.logging.structured_logger import (  # noqa: F401
    LogContext,
    StandardLogger,
    get_logger,
    log_debug,
    log_error,
    log_info,
    log_warning,
    logger,
)

__all__ = [
    "LogContext",
    "StandardLogger",
    "logger",
    "get_logger",
    "log_info",
    "log_error",
    "log_warning",
    "log_debug",
]
