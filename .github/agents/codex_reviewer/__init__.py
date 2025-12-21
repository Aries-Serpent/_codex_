"""
Codex Quantum Reviewer Agent Package

This package contains the implementation of the Codex Quantum Reviewer,
a GitHub Copilot agent that provides intelligent PR reviews with quantum-pattern
analysis, security validation, and self-evolution capabilities.
"""

__version__ = "1.0.0"
__author__ = "mbaetiong"

from .main import (
    CodexQuantumReviewer,
    ReviewContext,
    ReviewResult,
)

__all__ = [
    "CodexQuantumReviewer",
    "ReviewContext",
    "ReviewResult",
]
