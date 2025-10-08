from __future__ import annotations
from codex_ml.detectors.unified_training import detector_unified_training


def test_unified_training_detector_shape():
    r = detector_unified_training()
    assert r.name == "unified_training"
    assert 0.0 <= r.score <= 1.0
    assert isinstance(r.details, dict)
