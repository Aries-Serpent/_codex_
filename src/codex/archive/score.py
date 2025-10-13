from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScoreInput:
    age_days: int
    ref_count: int
    coverage: float
    has_deprecation_tag: bool


def archive_score(
    inp: ScoreInput,
    *,
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.2,
    w4: float = 0.1,
    tau: int = 180,
) -> float:
    s = 0.0
    s += w1 * (1.0 if inp.age_days > tau else 0.0)
    s += w2 * (1.0 if inp.ref_count == 0 else 0.0)
    s += w3 * (1.0 if inp.coverage <= 0.0 else 0.0)
    s += w4 * (1.0 if inp.has_deprecation_tag else 0.0)
    return round(min(max(s, 0.0), 1.0), 3)
