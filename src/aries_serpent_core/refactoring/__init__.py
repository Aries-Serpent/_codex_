"""
Refactoring utilities for the Codex project.

Includes deterritorialization engine for breaking rigid patterns.
"""

from .deterritorialization_engine import (
    DeterritorializationEngine,
    LineOfFlight,
    RigidityDetector,
    RigidityType,
)

__all__ = [
    "DeterritorializationEngine",
    "LineOfFlight",
    "RigidityDetector",
    "RigidityType",
]
