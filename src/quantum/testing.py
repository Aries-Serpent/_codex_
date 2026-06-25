"""
Quantum-inspired testing with superposition and collapse.

Cross-references:
    - src/rag/pipelines/quantum_retrieval.py
    - agents/quantum_game_theory.py
    - src/mcp/metrics/mcp_metrics.py
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TestState(Enum):
    """Test execution states inspired by quantum mechanics."""

    SUPERPOSITION = "superposition"  # Test outcome unknown
    PASSED = "passed"  # Wave function collapsed to success
    FAILED = "failed"  # Wave function collapsed to failure
    SKIPPED = "skipped"  # Decoherence - test not applicable


@dataclass
class QuantumTest:
    """
    Test case with quantum-inspired execution behavior.

    Physics Principles:
        - Superposition: Test result unknown until execution
        - Uncertainty Principle: Cannot know both execution time and result with certainty
        - Interference: Multiple test paths can interfere constructively/destructively

    Attributes:
        name: Test identifier
        test_func: Callable that returns bool (True=pass, False=fail)
        amplitude: Probability amplitude (affects execution probability)
        phase: Quantum phase (for interference calculations)
        state: Current test state
        execution_time: Time taken to execute (seconds)
        error: Exception if test failed

    Example:
        >>> test = QuantumTest(
        ...     name="test_import",
        ...     test_func=lambda: True,
        ...     amplitude=0.9
        ... )
        >>> state = test.execute()
    """

    name: str
    test_func: Callable[[], bool]
    amplitude: float = 1.0
    phase: float = 0.0
    state: TestState = TestState.SUPERPOSITION
    execution_time: Optional[float] = None
    error: Optional[Exception] = None

    def get_probability(self) -> float:
        """
        Calculate execution probability using Born rule: P = |ψ|².

        Returns:
            Probability between 0.0 and 1.0
        """
        return self.amplitude**2

    def execute(self) -> TestState:
        """
        Execute test and collapse wave function.

        Physics: Measurement causes wave function collapse.

        Returns:
            Final test state (PASSED, FAILED, or SKIPPED)
        """
        start_time = time.time()

        try:
            result = self.test_func()
            self.state = TestState.PASSED if result else TestState.FAILED
        except (ValueError, TypeError, RuntimeError) as exc:
            self.state = TestState.FAILED
            self.error = exc
            logger.error(f"Test '{self.name}' exception: <ERROR_TYPE>")
        finally:
            self.execution_time = time.time() - start_time

        logger.info(
            f"Test '{self.name}' collapsed to {self.state.value} "
            f"(t={self.execution_time:.3f}s, P={self.get_probability():.3f})"
        )

        return self.state

    def calculate_energy(self) -> float:
        """
        Calculate test energy using E = ℏω where ω = 1/execution_time.

        Physics: Planck-Einstein relation.

        Returns:
            Energy value (inf if not executed)
        """
        if self.execution_time is None or self.execution_time == 0:
            return float("inf")

        hbar = 1.0  # Reduced Planck constant (normalized)
        omega = 1.0 / self.execution_time  # Angular frequency
        return hbar * omega


@dataclass
class QuantumTestSuite:
    """
    Test suite with interference and entanglement.

    Cross-references:
        - src/mcp/metrics/mcp_metrics.py:MCPMetrics
        - agents/advanced_physics_calculators.py

    Example:
        >>> suite = QuantumTestSuite()
        >>> test = QuantumTest(name="test1", test_func=lambda: True)
        >>> suite.add_test(test)
        >>> results = suite.execute_with_thermodynamic_scheduling()
    """

    tests: list[QuantumTest] = field(default_factory=list)
    temperature: float = 1.0

    def add_test(self, test: QuantumTest) -> None:
        """
        Register test in superposition.

        Args:
            test: Test to add
        """
        self.tests.append(test)

    def execute_with_thermodynamic_scheduling(self) -> dict[str, Any]:
        """
        Execute tests using thermodynamic principles.

        Physics: Entropy minimization and free energy.

        Returns:
            Dictionary with test results and statistics
        """
        from common.error_handling import safe_call

        results: dict[str, Any] = {
            "total": len(self.tests),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total_energy": 0.0,
            "entropy": 0.0,
            "tests": [],
        }

        # Calculate execution order based on amplitude (priority)
        sorted_tests = sorted(self.tests, key=lambda t: t.get_probability(), reverse=True)

        for test in sorted_tests:
            state = safe_call(
                test.execute,
                operation_name=f"Execute test {test.name}",
                default_return=TestState.FAILED,
            )

            if state == TestState.PASSED:
                results["passed"] += 1
            elif state == TestState.FAILED:
                results["failed"] += 1
            else:
                results["skipped"] += 1

            if test.execution_time:
                results["total_energy"] += test.calculate_energy()

            results["tests"].append(
                {
                    "name": test.name,
                    "state": state.value,
                    "probability": test.get_probability(),
                    "time": test.execution_time,
                    "energy": (test.calculate_energy() if test.execution_time else None),
                }
            )

        # Calculate Shannon entropy of test outcomes
        total = results["total"]
        if total > 0:
            p_pass = results["passed"] / total
            p_fail = results["failed"] / total
            p_skip = results["skipped"] / total

            entropy = 0.0
            for p in [p_pass, p_fail, p_skip]:
                if p > 0:
                    entropy -= p * math.log2(p)

            results["entropy"] = entropy

        return results

    def calculate_test_interference(self, test1: QuantumTest, test2: QuantumTest) -> float:
        """
        Calculate interference between two tests.

        Physics: I = |ψ₁ + ψ₂|² = |ψ₁|² + |ψ₂|² + 2|ψ₁||ψ₂|cos(φ₁ - φ₂).

        Args:
            test1: First test
            test2: Second test

        Returns:
            Interference intensity
        """
        amplitude1 = test1.amplitude
        amplitude2 = test2.amplitude
        phase_diff = test1.phase - test2.phase

        # Interference term
        return amplitude1**2 + amplitude2**2 + 2 * amplitude1 * amplitude2 * math.cos(phase_diff)
