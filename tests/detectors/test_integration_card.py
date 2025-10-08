from __future__ import annotations
from codex_ml.detectors.aggregate import scorecard
from codex_ml.detectors.unified_training import detector_unified_training


def test_integration_scorecard_has_reasonable_fields():
    sc = scorecard([detector_unified_training])
    assert 0.0 <= sc["total_score"] <= 1.0
    assert "unified_training" in sc["by_detector"]
    assert isinstance(sc["details"], list) and sc["details"]
