"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from exec.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# Re-export all public symbols from codex_exec
# Note: codex_exec does not define __all__, so we import selectively
try:
    from .codex_exec import CodexExecutor, execute_codex  # type: ignore[attr-defined]
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)  # Module may not have these exports
