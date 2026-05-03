"""Detectors package seed."""

from __future__ import annotations

from .aggregate import scorecard
from .core import Detector, DetectorResult
from .experiment_summary import detector_experiment_summary

__all__ = ["Detector", "DetectorResult", "detector_experiment_summary", "scorecard"]
