"""Focused test runner simulation for the ITA."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import List

from .models import TestFailure, TestsRunRequest, TestsRunResponse, TestsRunSummary


@dataclass(frozen=True)
class SyntheticTestResult:
    target: str
    passed: bool
    message: str = ""


_FAILURE_HINTS = {
    "lint": "Lint failures detected for {target}.",
    "mypy": "Type errors detected for {target}.",
    "integration": "Integration test {target} failed to reach healthy state.",
}


def _determine_failure_message(target: str) -> str:
    for keyword, template in _FAILURE_HINTS.items():
        if keyword in target:
            return template.format(target=target)
    return f"Test target {target} failed with an unspecified error."


def simulate_test_execution(request: TestsRunRequest) -> TestsRunResponse:
    """Simulate focused test execution.

    The heuristic treats targets containing the word "fail" as failures and randomly introduces
    non-deterministic behaviour for advanced keywords (e.g. integration tests).
    """

    results: List[SyntheticTestResult] = []
    start = time.perf_counter()
    rng = random.Random()

    for target in request.targets:
        lowered = target.lower()
        if "fail" in lowered:
            results.append(
                SyntheticTestResult(
                    target=target, passed=False, message=_determine_failure_message(lowered)
                )
            )
            continue
        if "integration" in lowered and rng.random() < 0.2:
            results.append(
                SyntheticTestResult(
                    target=target, passed=False, message=_determine_failure_message(lowered)
                )
            )
            continue
        results.append(SyntheticTestResult(target=target, passed=True))

    duration = round(time.perf_counter() - start, 4)
    failures = [
        TestFailure(name=result.target, message=result.message)
        for result in results
        if not result.passed
    ]
    passed = sum(1 for result in results if result.passed)
    summary = TestsRunSummary(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        duration_s=duration,
    )
    return TestsRunResponse(summary=summary, failures=failures)


__all__ = ["simulate_test_execution"]
