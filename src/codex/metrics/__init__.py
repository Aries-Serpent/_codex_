"""
Codex Metrics Module

Provides code quality metrics including duplication detection and ratio calculation.
"""

from .duplication import (
    DuplicateBlock,
    DuplicationDetector,
    DuplicationRatio,
    calculate_duplication_ratio,
    detect_duplicates,
)
from .storage import MetricStorage

__all__ = [
    "DuplicationDetector",
    "DuplicationRatio",
    "DuplicateBlock",
    "detect_duplicates",
    "calculate_duplication_ratio",
    "MetricStorage",
]
