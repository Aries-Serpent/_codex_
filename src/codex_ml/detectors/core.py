"""
Core Module

This module provides functionality for core.

Usage:
    from detectors.core import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class DetectorResult:
    name: str
    score: float  # bounded [0,1]
    details: dict[str, Any]


Detector = Callable[[], DetectorResult]


def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x
