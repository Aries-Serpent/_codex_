"""
Test Unified Training

Test module for unified training.
"""

from __future__ import annotations

from codex_ml.detectors.unified_training import detector_unified_training


def test_unified_training_detector_shape():
    r = detector_unified_training()
    assert r.name == "unified_training", "name is not valid"
    assert 0.0 <= r.score <= 1.0, "0 is not valid"
    assert isinstance(r.details, dict)
