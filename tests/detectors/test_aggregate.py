from __future__ import annotations
from codex_ml.detectors.aggregate import scorecard
from codex_ml.detectors.core import DetectorResult


def _mk(name, s):
    def run():
        return DetectorResult(name=name, score=s, details={})

    return run


def test_scorecard_unweighted_mean():
    sc = scorecard([_mk("a", 1.0), _mk("b", 0.0)])
    assert 0.0 <= sc["total_score"] <= 1.0
    assert sc["by_detector"]["a"] == 1.0
    assert sc["by_detector"]["b"] == 0.0
    assert abs(sc["total_score"] - 0.5) < 1e-9


def test_scorecard_weighted_mean():
    sc = scorecard([_mk("a", 1.0), _mk("b", 0.0)], weights={"a": 3.0, "b": 1.0})
    # (3*1 + 1*0)/4 = 0.75
    assert abs(sc["total_score"] - 0.75) < 1e-9
