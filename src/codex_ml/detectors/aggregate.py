from __future__ import annotations
from .core import Detector, DetectorResult, clamp01
from typing import Iterable, Dict, Any


def scorecard(
    detectors: Iterable[Detector], weights: Dict[str, float] | None = None
) -> Dict[str, Any]:
    results: list[DetectorResult] = []
    weights = dict(weights or {})
    total_w = 0.0
    acc = 0.0
    for det in detectors:
        r = det()
        w = float(weights.get(r.name, 1.0))
        s = clamp01(float(r.score))
        total_w += w
        acc += w * s
        results.append(r)
    total = (acc / total_w) if total_w > 0 else 0.0
    return {
        "total_score": round(total, 6),
        "by_detector": {r.name: r.score for r in results},
        "details": [{**r.__dict__} for r in results],
    }
