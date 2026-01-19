"""
Batch Triage Agent - Package Initialization

This package provides intelligent batch CI failure triage with cognitive brain integration.
"""

__version__ = "1.0.0"
__author__ = "Codex Team"

from .analyzer import BatchTriageAnalyzer
from .pattern_learner import PatternLearner
from .remediation_engine import RemediationEngine
from .notifier import Notifier

__all__ = [
    "BatchTriageAnalyzer",
    "PatternLearner",
    "RemediationEngine",
    "Notifier",
]
