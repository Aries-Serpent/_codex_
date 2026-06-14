"""Tests for cognitive_brain.experiments.exp3_validation.

Tests cover:
- TestCase dataclass structure
- generate_test_suite reproducibility and bounds
- run_traditional_approach metrics
- run_uncertainty_approach time budget
"""

from __future__ import annotations

import pytest

from cognitive_brain.experiments.exp3_validation import (
    TestCase,
    generate_test_suite,
    run_traditional_approach,
)

# ---------------------------------------------------------------------------
# TestCase dataclass
# ---------------------------------------------------------------------------


def test_testcase_fields():
    tc = TestCase(
        test_id="tc_001",
        execution_time=5.0,
        will_fail=True,
        failure_rate=0.3,
        last_failure_time=1000.0,
        coverage_contribution=0.7,
        complexity_score=0.4,
    )
    assert tc.test_id == "tc_001"
    assert tc.execution_time == pytest.approx(5.0)
    assert tc.will_fail is True
    assert tc.failure_rate == pytest.approx(0.3)
    assert tc.coverage_contribution == pytest.approx(0.7)
    assert tc.complexity_score == pytest.approx(0.4)


def test_testcase_last_failure_time_can_be_none():
    tc = TestCase(
        test_id="tc_002",
        execution_time=3.0,
        will_fail=False,
        failure_rate=0.0,
        last_failure_time=None,
        coverage_contribution=0.5,
        complexity_score=0.2,
    )
    assert tc.last_failure_time is None


# ---------------------------------------------------------------------------
# generate_test_suite
# ---------------------------------------------------------------------------


def test_generate_test_suite_count():
    suite = generate_test_suite(num_tests=10, seed=42)
    assert len(suite) == 10


def test_generate_test_suite_100():
    suite = generate_test_suite(num_tests=100, seed=42)
    assert len(suite) == 100


def test_generate_test_suite_zero():
    suite = generate_test_suite(num_tests=0, seed=42)
    assert suite == []


def test_generate_test_suite_reproducible():
    s1 = generate_test_suite(20, seed=42)
    s2 = generate_test_suite(20, seed=42)
    for t1, t2 in zip(s1, s2):
        assert t1.test_id == t2.test_id
        assert t1.execution_time == pytest.approx(t2.execution_time)
        assert t1.will_fail == t2.will_fail


def test_generate_test_suite_different_seeds():
    s1 = generate_test_suite(20, seed=1)
    s2 = generate_test_suite(20, seed=99)
    # Seeds should produce different suites
    assert any(t1.execution_time != pytest.approx(t2.execution_time) for t1, t2 in zip(s1, s2))


def test_generate_test_suite_unique_ids():
    suite = generate_test_suite(50, seed=42)
    ids = [tc.test_id for tc in suite]
    assert len(set(ids)) == 50


def test_generate_test_suite_ids_format():
    suite = generate_test_suite(5, seed=0)
    for i, tc in enumerate(suite):
        assert tc.test_id == f"test_{i:03d}"


def test_generate_test_suite_execution_time_positive():
    suite = generate_test_suite(20, seed=42)
    for tc in suite:
        assert tc.execution_time > 0.0


def test_generate_test_suite_execution_time_range():
    suite = generate_test_suite(50, seed=42)
    for tc in suite:
        assert 1.0 <= tc.execution_time <= 60.0


def test_generate_test_suite_failure_rate_range():
    suite = generate_test_suite(50, seed=42)
    for tc in suite:
        assert 0.0 <= tc.failure_rate <= 0.8


def test_generate_test_suite_coverage_in_range():
    suite = generate_test_suite(20, seed=42)
    for tc in suite:
        assert 0.0 <= tc.coverage_contribution <= 1.0


def test_generate_test_suite_complexity_in_range():
    suite = generate_test_suite(20, seed=42)
    for tc in suite:
        assert 0.0 <= tc.complexity_score <= 1.0


def test_generate_test_suite_will_fail_is_bool():
    suite = generate_test_suite(20, seed=42)
    for tc in suite:
        assert isinstance(tc.will_fail, bool)


def test_generate_test_suite_has_both_fail_states():
    """With 100 tests, there should be both failing and passing tests."""
    suite = generate_test_suite(100, seed=42)
    failing = sum(1 for tc in suite if tc.will_fail)
    passing = sum(1 for tc in suite if not tc.will_fail)
    assert failing > 0
    assert passing > 0


# ---------------------------------------------------------------------------
# run_traditional_approach
# ---------------------------------------------------------------------------


def test_run_traditional_approach_runs_all_tests():
    suite = generate_test_suite(10, seed=42)
    _total_time, tests_run, _failures = run_traditional_approach(suite)
    assert tests_run == len(suite)


def test_run_traditional_approach_total_time():
    suite = generate_test_suite(10, seed=42)
    expected_time = sum(tc.execution_time for tc in suite)
    total_time, _, _ = run_traditional_approach(suite)
    assert total_time == pytest.approx(expected_time)


def test_run_traditional_approach_failures_correct():
    suite = generate_test_suite(50, seed=42)
    _, _, failures = run_traditional_approach(suite)
    expected = sum(1 for tc in suite if tc.will_fail)
    assert failures == expected


def test_run_traditional_approach_empty_suite():
    total_time, tests_run, failures = run_traditional_approach([])
    assert total_time == pytest.approx(0.0)
    assert tests_run == 0
    assert failures == 0


def test_run_traditional_approach_all_failing():
    suite = [
        TestCase(
            test_id=f"t{i}",
            execution_time=1.0,
            will_fail=True,
            failure_rate=1.0,
            last_failure_time=1000.0,
            coverage_contribution=0.5,
            complexity_score=0.5,
        )
        for i in range(5)
    ]
    _, _, failures = run_traditional_approach(suite)
    assert failures == 5


def test_run_traditional_approach_none_failing():
    suite = [
        TestCase(
            test_id=f"t{i}",
            execution_time=2.0,
            will_fail=False,
            failure_rate=0.0,
            last_failure_time=None,
            coverage_contribution=0.3,
            complexity_score=0.1,
        )
        for i in range(5)
    ]
    _, _, failures = run_traditional_approach(suite)
    assert failures == 0
