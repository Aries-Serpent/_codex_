"""
Perplexity Metric v1.0.0
Perplexity = exp(loss)

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""

from __future__ import annotations

import math


def perplexity_from_loss(loss: float) -> float:
    """Perplexity = exp(loss)."""
    try:
        return float(math.exp(float(loss)))
    except Exception:
        return float("inf")
