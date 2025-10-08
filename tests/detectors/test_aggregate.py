from __future__ import annotations

from codex_ml.detectors.aggregate import aggregate
from codex_ml.detectors.core import DetectorFinding, DetectorResult


def test_aggregate_weighted_mean():
    r1 = DetectorResult("a", 1.0, [DetectorFinding("ok", True)])
    r2 = DetectorResult("b", 0.0, [DetectorFinding("ko", False)])
    card = aggregate([r1, r2], weights={"a": 2.0, "b": 1.0})
    # (2*1 + 1*0)/3 = 0.666...
    assert 0.65 < card.total_score < 0.68
    assert card.by_detector == {"a": 1.0, "b": 0.0}
    assert "details" in card.__dict__
