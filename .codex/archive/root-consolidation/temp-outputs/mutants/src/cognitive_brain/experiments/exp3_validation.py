"""
EXP-3 Validation: Uncertainty-Based Test Prioritization.

This experiment validates the UncertaintyOptimizer's ability to:
1. Prioritize high-value tests
2. Reduce total test execution time by 25%+
3. Maintain > 95% failure detection rate

Methodology:
- Generate 100 synthetic test cases with varying characteristics
- Run traditional (all tests) vs uncertainty-optimized approaches
- Compare execution time and failure detection rate
"""

import random
from dataclasses import dataclass

from cognitive_brain.quantum import TestExecutionMetrics
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.uncertainty import UncertaintyOptimizer


@dataclass
class TestCase:
    """Synthetic test case for validation."""

    test_id: str
    execution_time: float
    will_fail: bool  # Ground truth
    failure_rate: float  # Historical
    last_failure_time: float
    coverage_contribution: float
    complexity_score: float


def generate_test_suite(num_tests: int = 100, seed: int = 42) -> list[TestCase]:
    """
    Generate synthetic test suite for validation.

    Args:
        num_tests: Number of tests to generate
        seed: Random seed for reproducibility

    Returns:
        List of test cases
    """
    # Copilot: Using random.Random() instance for reproducible test data generation.
    # This is NOT for security/cryptographic purposes - Bandit B311 is a false positive here.
    # These are experiment scenarios for testing test prioritization algorithms.
    _rng = random.Random(seed)  # nosec B311
    tests = []
    current_time = 2000.0

    for i in range(num_tests):
        # Varied execution times (1-60 seconds)
        exec_time = _rng.uniform(1.0, 60.0)

        # Varied failure rates (0-80%)
        historical_failure_rate = _rng.uniform(0.0, 0.8)

        # Some tests will fail (correlated with failure rate)
        will_fail = _rng.random() < historical_failure_rate

        # Last failure time (some never failed)
        if _rng.random() < historical_failure_rate:
            # Failed recently
            last_failure = current_time - _rng.uniform(0.0, 7 * 86400.0)  # Within 7 days
        else:
            last_failure = None

        # Coverage contribution (0-100%)
        coverage = _rng.uniform(0.0, 1.0)

        # Complexity score (0-100%)
        complexity = _rng.uniform(0.0, 1.0)

        tests.append(
            TestCase(
                test_id=f"test_{i:03d}",
                execution_time=exec_time,
                will_fail=will_fail,
                failure_rate=historical_failure_rate,
                last_failure_time=last_failure,  # type: ignore[arg-type]
                coverage_contribution=coverage,
                complexity_score=complexity,
            )
        )

    return tests


def run_traditional_approach(test_suite: list[TestCase]) -> tuple[float, int, int]:
    """
    Run all tests (traditional approach).

    Args:
        test_suite: List of test cases

    Returns:
        Tuple of (total_time, tests_run, failures_detected)
    """
    total_time = sum(test.execution_time for test in test_suite)
    tests_run = len(test_suite)
    failures_detected = sum(1 for test in test_suite if test.will_fail)

    return total_time, tests_run, failures_detected


def run_uncertainty_approach(
    test_suite: list[TestCase], time_budget_factor: float = 0.75
) -> tuple[float, int, int]:
    """
    Run uncertainty-optimized test selection.

    Args:
        test_suite: List of test cases
        time_budget_factor: Fraction of total time to use (default: 0.75 = 25% reduction)

    Returns:
        Tuple of (total_time, tests_run, failures_detected)
    """
    # Calculate time budget (75% of total for 25% reduction)
    traditional_time = sum(test.execution_time for test in test_suite)
    time_budget = traditional_time * time_budget_factor

    # Initialize optimizer
    config = QuantumConfig(quantum_mode=True, uncertainty=True, rollout_percentage=100)
    optimizer = UncertaintyOptimizer(config)

    # Update metrics for all tests
    for test in test_suite:
        optimizer.update_test_metrics(
            TestExecutionMetrics(
                test_id=test.test_id,
                execution_time=test.execution_time,
                failure_rate=test.failure_rate,
                last_failure_time=test.last_failure_time,
                coverage_contribution=test.coverage_contribution,
                complexity_score=test.complexity_score,
            )
        )

    # Optimize schedule
    current_time = 2000.0
    test_ids = [test.test_id for test in test_suite]
    selected_ids, _priorities = optimizer.optimize_test_schedule(
        test_ids, time_budget, current_time
    )

    # Count failures detected
    selected_tests = {test.test_id: test for test in test_suite if test.test_id in selected_ids}
    failures_detected = sum(1 for test_id in selected_ids if selected_tests[test_id].will_fail)

    # Calculate actual time used
    actual_time = sum(selected_tests[test_id].execution_time for test_id in selected_ids)

    return actual_time, len(selected_ids), failures_detected


def run_exp3_validation() -> dict:
    """
    Run EXP-3 validation experiment.

    Returns:
        Dictionary with experiment results
    """
    print("=" * 60)
    print("EXP-3: Uncertainty-Based Test Prioritization Validation")
    print("=" * 60)

    # Generate test suite
    print("\nGenerating test suite...")
    test_suite = generate_test_suite(num_tests=100, seed=42)
    print(f"Generated {len(test_suite)} test cases")

    # Run traditional approach
    print("\nRunning traditional approach (all tests)...")
    trad_time, trad_tests, trad_failures = run_traditional_approach(test_suite)
    print(f"  Time: {trad_time:.1f}s")
    print(f"  Tests run: {trad_tests}")
    print(f"  Failures detected: {trad_failures}")

    # Run uncertainty approach
    print("\nRunning uncertainty-optimized approach (75% time budget)...")
    unc_time, unc_tests, unc_failures = run_uncertainty_approach(test_suite, 0.75)
    print(f"  Time: {unc_time:.1f}s")
    print(f"  Tests run: {unc_tests}")
    print(f"  Failures detected: {unc_failures}")

    # Calculate metrics
    time_reduction = ((trad_time - unc_time) / trad_time) * 100
    detection_rate = (unc_failures / trad_failures) * 100 if trad_failures > 0 else 0.0
    tests_reduction = ((trad_tests - unc_tests) / trad_tests) * 100

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Time reduction: {time_reduction:.1f}% (target: ≥25%)")
    print(f"Failure detection rate: {detection_rate:.1f}% (target: ≥95%)")
    print(f"Tests reduction: {tests_reduction:.1f}%")

    # Determine success
    success = time_reduction >= 25.0 and detection_rate >= 95.0
    status = "✅ SUCCESS" if success else "⚠️ PARTIAL SUCCESS"
    print(f"\nStatus: {status}")

    if success:
        print("Uncertainty optimizer meets all targets!")
    else:
        if time_reduction < 25.0:
            print(f"  - Time reduction below target ({time_reduction:.1f}% < 25%)")
        if detection_rate < 95.0:
            print(f"  - Detection rate below target ({detection_rate:.1f}% < 95%)")

    print("=" * 60)

    return {
        "experiment_id": "EXP-3",
        "num_tests": len(test_suite),
        "traditional_time": trad_time,
        "traditional_tests": trad_tests,
        "traditional_failures": trad_failures,
        "uncertainty_time": unc_time,
        "uncertainty_tests": unc_tests,
        "uncertainty_failures": unc_failures,
        "time_reduction_pct": time_reduction,
        "detection_rate_pct": detection_rate,
        "tests_reduction_pct": tests_reduction,
        "success": success,
    }


if __name__ == "__main__":
    run_exp3_validation()
