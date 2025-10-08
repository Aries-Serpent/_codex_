from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Iterable, Mapping

from .core import DetectorResult, as_dict

Weights = Mapping[str, float]


@dataclass(frozen=True)
class Scorecard:
    total_score: float
    by_detector: dict[str, float] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)


def aggregate(results: Iterable[DetectorResult], weights: Weights | None = None) -> Scorecard:
    weights = dict(weights or {})
    w_sum = 0.0
    s_sum = 0.0
    per: dict[str, float] = {}
    details: dict[str, Any] = {}
    for r in results:
        w = float(weights.get(r.detector, 1.0))
        w_sum += w
        s_sum += w * float(r.score)
        per[r.detector] = float(r.score)
        details[r.detector] = as_dict(r)
    total = (s_sum / w_sum) if w_sum > 0 else 0.0
    return Scorecard(total_score=total, by_detector=per, details=details)


def to_json_dict(card: Scorecard) -> dict[str, Any]:
    return asdict(card)
