"""
Test Core

Test module for core.
"""

from __future__ import annotations

from codex_ml.detectors.core import DetectorResult, clamp01


def test_clamp01_bounds():
    assert clamp01(-1.0) == 0.0, "Condition must be true"
    assert clamp01(0.5) == 0.5, "Condition must be true"
    assert clamp01(2.0) == 1.0, "Condition must be true"


def test_detector_result_dataclass_fields():
    r = DetectorResult(name="x", score=0.5, details={"a": 1})
    assert r.name == "x" and r.score == 0.5 and r.details["a"] == 1
