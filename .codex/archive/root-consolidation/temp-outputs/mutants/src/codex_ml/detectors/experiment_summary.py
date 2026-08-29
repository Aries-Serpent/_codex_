"""
Experiment Summary Module

This module provides functionality for experiment summary.

Usage:
    from detectors.experiment_summary import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
from pathlib import Path  # noqa: E402

from .core import DetectorResult, clamp01  # noqa: E402


def detector_experiment_summary(
    summary_path: str | Path = "artifacts/experiment_summary.json",
) -> DetectorResult:
    path = Path(summary_path)
    if not path.exists():
        return DetectorResult(
            name="experiment_summary",
            score=0.0,
            details={"reason": "summary missing", "path": str(path)},
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return DetectorResult(
            name="experiment_summary",
            score=0.0,
            details={"reason": "failed to parse", "path": str(path)},
        )

    runs = payload.get("runs", []) if isinstance(payload, dict) else []
    aggregates = payload.get("aggregates", {}) if isinstance(payload, dict) else {}
    run_count = len(runs)
    score = clamp01(1.0 if run_count > 0 else 0.0)
    return DetectorResult(
        name="experiment_summary",
        score=score,
        details={"runs": run_count, "aggregates": aggregates, "path": str(path)},
    )
