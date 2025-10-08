from __future__ import annotations

from codex_ml.detectors import DetectorFinding, DetectorResult, run_detectors


def test_run_detectors_happy_path():
    def d1(_m):
        return DetectorResult("d1", 1.0, [DetectorFinding("ok", True)])

    def d2(_m):
        return DetectorResult("d2", 0.5, [DetectorFinding("warn", True, "partial")])

    res = run_detectors([d1, d2], manifest=None)
    assert [r.detector for r in res] == ["d1", "d2"]
    assert res[0].score == 1.0 and res[1].score == 0.5
