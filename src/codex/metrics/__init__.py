"""
Codex Metrics Module

Provides code quality metrics including duplication detection and ratio calculation.
"""

from .duplication import (
    DuplicationDetector,
    DuplicationRatio,
    detect_duplicates,
    calculate_duplication_ratio,
)

__all__ = [
    "DuplicationDetector",
    "DuplicationRatio",
    "detect_duplicates",
    "calculate_duplication_ratio",
]
