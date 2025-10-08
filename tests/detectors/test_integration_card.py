from __future__ import annotations

from codex_ml.detectors.core import run_detectors
from codex_ml.detectors.unified_training import detect as unified
from codex_ml.detectors.aggregate import aggregate


def test_integration_detectors_to_scorecard():
    results = run_detectors([unified], manifest=None)
    card = aggregate(results, weights={"unified_training": 1.0})
    assert 0.0 <= card.total_score <= 1.0
    assert "unified_training" in card.by_detector
