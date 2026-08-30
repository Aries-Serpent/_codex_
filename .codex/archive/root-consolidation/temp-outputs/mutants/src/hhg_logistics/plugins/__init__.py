"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from plugins.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Sequence

logger = logging.getLogger(__name__)


__all__ = ["load_plugins"]


def load_plugins(modules: Sequence[str]) -> None:
    """Import plugin modules for side-effect registrations."""

    for module in modules:
        try:
            importlib.import_module(module)
            logger.info("Plugin loaded: %s", module)
        except (
            ImportError,
            AttributeError,
        ) as exc:  # pragma: no cover - plugin failures are non-fatal
            logger.warning("Failed to load plugin %s: %s", module, exc)
