"""
Base Metric Interface v1.0.0
Abstract base class for batch and streaming metrics

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMetric(ABC):
    """Abstract base for metrics (batch or streaming)."""

    @abstractmethod
    def update(self, preds: Any, labels: Any, **kwargs) -> None:
        """Accumulate a batch into internal state. Subclasses must implement."""

    @abstractmethod
    def compute(self) -> Any:
        """Compute the final metric from current internal state. Subclasses must implement."""

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state for a fresh accumulation. Subclasses must implement."""

    def meta(self) -> dict[str, Any]:
        """Optional: return metadata about the metric instance."""
        return {"name": self.__class__.__name__}
