"""
Optional Module

This module provides functionality for optional.

Usage:
    from utils.optional import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import importlib
import logging
import types

logger = logging.getLogger(__name__)

_OPTIONAL_INSTALL_HINT = "pip install -r requirements/dev.txt"


def optional_import(name: str) -> tuple[types.ModuleType | None, bool]:
    """Best-effort dynamic import.

    Returns a tuple of (module, available) where ``module`` is the imported
    module object or ``None`` if the import failed for any reason.
    """
    try:
        return importlib.import_module(name), True
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return None, False


def optional_dependency_error(
    package: str,
    *,
    purpose: str,
    install_hint: str | None = None,
) -> ImportError:
    """Return a descriptive ImportError for missing optional dependencies."""

    hint = install_hint or package
    message = (
        f"{package} is required for {purpose}. "
        f"Install with: pip install {hint}\n"
        f"Or install all optional dependencies: {_OPTIONAL_INSTALL_HINT}"
    )
    return ImportError(message)


__all__ = ["optional_dependency_error", "optional_import"]
