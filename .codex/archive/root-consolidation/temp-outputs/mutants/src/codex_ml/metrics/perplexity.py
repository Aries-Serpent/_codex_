"""
Perplexity Metric v1.0.0
Perplexity = exp(loss)

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import math  # noqa: E402


def perplexity_from_loss(loss: float) -> float:
    """Perplexity = exp(loss)."""
    try:
        return float(math.exp(float(loss)))
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return float("inf")
