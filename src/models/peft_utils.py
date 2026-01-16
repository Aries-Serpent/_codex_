"""
Peft Utils Module

This module provides functionality for peft utils.

Usage:
    from models.peft_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
"""Helpers for interrogating optional PEFT adapters at runtime."""


from typing import Any


def summarize_peft(model: Any) -> dict[str, Any]:
    """Return a compact summary describing the adapter wiring for ``model``.

    The helper gracefully handles environments without the ``peft`` package
    installed. When ``peft`` is available but the supplied model is not wrapped
    by a PEFT adapter, a neutral summary is emitted to aid smoke tests.
    """

    try:
        from peft.utils import get_model_status  # type: ignore
    except (ImportError, ModuleNotFoundError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "unavailable"}

    try:
        status = get_model_status(model)  # type: ignore
    except (ValueError, AttributeError, TypeError):
        logger.debug("Exception caught, returning", exc_info=True)
        return {"peft": "not_wrapped"}

    return {
        "base_model_type": getattr(status, "base_model_type", "unknown"),
        "adapter_model_type": getattr(status, "adapter_model_type", "unknown"),
        "trainable_params": int(getattr(status, "trainable_params", -1)),
        "total_params": int(getattr(status, "total_params", -1)),
        "num_adapter_layers": int(getattr(status, "num_adapter_layers", -1)),
    }


__all__ = ["summarize_peft"]
