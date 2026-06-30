"""Test Coverage Enforcer Agent - Enforces test coverage thresholds and generates missing tests"""

__version__ = "1.0.0"
__agent_name__ = "test-coverage-enforcer"

from .agent import TestCoverageEnforcer

__all__ = ["TestCoverageEnforcer"]
