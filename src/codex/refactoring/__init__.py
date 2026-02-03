"""
Refactoring utilities for the Codex project.

Includes deterritorialization engine for breaking rigid patterns.
"""

from .deterritorialization_engine import (
    DeterritorializationEngine,
    RigidityDetector,
    RigidityType,
    LineOfFlight,
)

__all__ = [
    "DeterritorializationEngine",
    "RigidityDetector",
    "RigidityType",
    "LineOfFlight",
]
