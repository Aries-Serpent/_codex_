"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from eval.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import logging

logger = logging.getLogger(__name__)

from . import metrics
from .fallback import synthetic_alignment

try:  # pragma: no cover - optional heavy dependencies
    from . import eval_runner
except (ImportError, AttributeError):  # pragma: no cover - torch/datasets may be missing
    eval_runner = None  # type: ignore[assignment]

try:  # pragma: no cover - new structured runner
    from . import runner
except (ImportError, AttributeError):  # pragma: no cover
    runner = None  # type: ignore[assignment]

__all__ = ["metrics", "synthetic_alignment"]
if eval_runner is not None:
    __all__.append("eval_runner")
if runner is not None:
    __all__.append("runner")
