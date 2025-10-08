from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Any


@dataclass
class DetectorResult:
    name: str
    score: float  # bounded [0,1]
    details: Dict[str, Any]


Detector = Callable[[], DetectorResult]


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x
