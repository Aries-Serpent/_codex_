"""Detectors package seed."""

from __future__ import annotations
from .core import DetectorResult, Detector
from .aggregate import scorecard

__all__ = ["DetectorResult", "Detector", "scorecard"]
