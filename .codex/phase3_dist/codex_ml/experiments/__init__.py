"""A/B testing and experiment management for Codex ML.

Public API
----------
ABTest
    Dataclass holding raw metric observations and configuration for a
    single A/B test.

ABTestResult
    Structured result returned by :func:`run_ab_test`.

run_ab_test
    Execute a Welch's t-test between two groups and return an
    :class:`ABTestResult`.

ABTestSuite
    Manage and run multiple :class:`ABTest` instances; produce a
    structured report.
"""

from __future__ import annotations

from codex_ml.experiments.ab_testing import (
    ABTest,
    ABTestResult,
    ABTestSuite,
    run_ab_test,
)

__all__ = [
    "ABTest",
    "ABTestResult",
    "ABTestSuite",
    "run_ab_test",
]
