"""Compatibility layer for the legacy codex.monitoring.metrics namespace."""

from aries_serpent_core.monitoring import Counter, Histogram, metrics

__all__ = ["Counter", "Histogram", "metrics"]
