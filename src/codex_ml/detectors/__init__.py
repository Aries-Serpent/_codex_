"""Detectors package seed."""

from __future__ import annotations

from .aggregate import scorecard
from .core import Detector, DetectorResult

__all__ = ["DetectorResult", "Detector", "scorecard"]
