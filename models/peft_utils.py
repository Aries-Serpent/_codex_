"""
Legacy compatibility layer for peft_utils module.

DEPRECATED: Use src.models.peft_utils instead.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'models.peft_utils' is deprecated. "
    "Use 'src.models.peft_utils' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.models.peft_utils import summarize_peft

__all__ = ["summarize_peft"]
