from __future__ import annotations
from .core import DetectorResult


def detector_unified_training() -> DetectorResult:
    """Minimal placeholder detector.
    Returns a neutral/high score until deeper checks are wired.
    """
    return DetectorResult(
        name="unified_training",
        score=0.9,
        details={"status": "ok"},
    )
