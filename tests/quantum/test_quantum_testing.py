"""Tests for quantum testing framework."""

from __future__ import annotations

import math

import pytest

from quantum import QuantumTest, QuantumTestSuite, TestState


class TestQuantumTest:
    """Test QuantumTest class."""

    def test_test_creation(self):
        """Test creating a quantum test."""
        test = QuantumTest(name="test_example", test_func=lambda: True, amplitude=0.9)
        assert test.name == "test_example", "name is not valid"
        assert test.state == TestState.SUPERPOSITION, "state is not valid"
        assert test.amplitude == 0.9, "amplitude is not valid"

    def test_get_probability(self):
        """Test probability calculation using Born rule."""
        test = QuantumTest(name="test", test_func=lambda: True, amplitude=0.8)
        prob = test.get_probability()
        assert prob == pytest.approx(0.64), "prob is not valid"

    def test_execute_pass(self):
        """Test executing a passing test."""
        test = QuantumTest(name="test_pass", test_func=lambda: True)
        state = test.execute()
        assert state == TestState.PASSED, "state is not valid"
        assert test.state == TestState.PASSED, "state is not valid"
        assert test.execution_time is not None, "execution_time must be initialized"
        assert test.execution_time >= 0, "execution_time must be greater than zero"

    def test_execute_fail(self):
        """Test executing a failing test."""
        test = QuantumTest(name="test_fail", test_func=lambda: False)
        state = test.execute()
        assert state == TestState.FAILED, "state is not valid"
        assert test.state == TestState.FAILED, "state is not valid"

    def test_execute_exception(self):
        """Test executing a test that raises exception."""

        def raising_func():
            raise ValueError("Test error")

        test = QuantumTest(name="test_exception", test_func=raising_func)
        state = test.execute()
        assert state == TestState.FAILED, "state is not valid"
        assert test.error is not None, "error must be initialized"
        assert isinstance(test.error, ValueError)

    def test_calculate_energy(self):
        """Test energy calculation using Planck relation."""
        test = QuantumTest(name="test", test_func=lambda: True)
        test.execute()

        energy = test.calculate_energy()
        assert energy > 0, "energy must be greater than zero"
        assert energy != float("inf"), "energy is not valid"

    def test_calculate_energy_not_executed(self):
        """Test energy calculation for unexecuted test."""
        test = QuantumTest(name="test", test_func=lambda: True)
        energy = test.calculate_energy()
        assert energy == float("inf"), "energy is not valid"


class TestQuantumTestSuite:
    """Test QuantumTestSuite class."""

    def test_suite_creation(self):
        """Test creating a test suite."""
        suite = QuantumTestSuite()
        assert suite.tests == [], "tests is not valid"
        assert suite.temperature == 1.0, "temperature is not valid"

    def test_add_test(self):
        """Test adding tests to suite."""
        suite = QuantumTestSuite()
        test = QuantumTest(name="test1", test_func=lambda: True)
        suite.add_test(test)
        assert len(suite.tests) == 1, "Collection must not be empty"
        assert suite.tests[0] is test, "Condition must be true"

    def test_execute_with_thermodynamic_scheduling(self):
        """Test executing test suite with thermodynamic scheduling."""
        suite = QuantumTestSuite()

        # Add tests with different amplitudes
        suite.add_test(QuantumTest(name="test1", test_func=lambda: True, amplitude=0.9))
        suite.add_test(QuantumTest(name="test2", test_func=lambda: True, amplitude=0.7))
        suite.add_test(QuantumTest(name="test3", test_func=lambda: False, amplitude=0.8))

        results = suite.execute_with_thermodynamic_scheduling()

        assert results["total"] == 3, "Result must not be empty"
        assert results["passed"] == 2, "Result must not be empty"
        assert results["failed"] == 1, "Result must not be empty"
        assert results["skipped"] == 0, "Result must not be empty"
        assert results["total_energy"] > 0, "Value must be greater than zero"
        assert len(results["tests"]) == 3, "Collection must not be empty"

    def test_entropy_calculation(self):
        """Test Shannon entropy calculation for test outcomes."""
        suite = QuantumTestSuite()

        # All pass -> zero entropy
        for i in range(4):
            suite.add_test(QuantumTest(name=f"pass{i}", test_func=lambda: True))

        results = suite.execute_with_thermodynamic_scheduling()
        # All same outcome = low entropy
        assert results["entropy"] == pytest.approx(0.0), "Result must not be empty"

    def test_entropy_mixed_outcomes(self):
        """Test entropy with mixed outcomes."""
        suite = QuantumTestSuite()

        # Mix of pass/fail
        suite.add_test(QuantumTest(name="pass1", test_func=lambda: True))
        suite.add_test(QuantumTest(name="fail1", test_func=lambda: False))

        results = suite.execute_with_thermodynamic_scheduling()
        # Mixed outcomes = higher entropy
        assert results["entropy"] > 0, "Value must be greater than zero"

    def test_calculate_test_interference(self):
        """Test interference calculation between tests."""
        suite = QuantumTestSuite()

        test1 = QuantumTest(name="test1", test_func=lambda: True, amplitude=0.8, phase=0.0)
        test2 = QuantumTest(name="test2", test_func=lambda: True, amplitude=0.6, phase=math.pi / 2)

        interference = suite.calculate_test_interference(test1, test2)

        # Check interference formula: |ψ₁|² + |ψ₂|² + 2|ψ₁||ψ₂|cos(φ₁ - φ₂)
        expected = 0.8**2 + 0.6**2 + 2 * 0.8 * 0.6 * math.cos(-math.pi / 2)
        assert interference == pytest.approx(expected), "interference is not valid"

    def test_execution_order_by_priority(self):
        """Test that tests execute in priority order (by amplitude)."""
        suite = QuantumTestSuite()

        execution_order = []

        def make_test_func(name):
            def test_func():
                execution_order.append(name)
                return True

            return test_func

        suite.add_test(
            QuantumTest(
                name="low_priority",
                test_func=make_test_func("low"),
                amplitude=0.5,  # Low amplitude = low priority
            )
        )
        suite.add_test(
            QuantumTest(
                name="high_priority",
                test_func=make_test_func("high"),
                amplitude=0.9,  # High amplitude = high priority
            )
        )
        suite.add_test(
            QuantumTest(name="medium_priority", test_func=make_test_func("medium"), amplitude=0.7)
        )

        suite.execute_with_thermodynamic_scheduling()

        # Should execute in order: high, medium, low
        assert execution_order == ["high", "medium", "low"]


@pytest.mark.integration
class TestQuantumTestingIntegration:
    """Integration tests for quantum testing framework."""

    def test_real_test_execution(self):
        """Test executing real test scenarios."""
        suite = QuantumTestSuite(temperature=1.5)

        # Add various real-world test scenarios
        suite.add_test(
            QuantumTest(
                name="test_import", test_func=lambda: __import__("sys") is not None, amplitude=1.0
            )
        )

        suite.add_test(QuantumTest(name="test_math", test_func=lambda: True, amplitude=0.95))

        suite.add_test(
            QuantumTest(
                name="test_string", test_func=lambda: "hello".upper() == "HELLO", amplitude=0.90
            )
        )

        results = suite.execute_with_thermodynamic_scheduling()

        assert results["passed"] == 3, "Result must not be empty"
        assert results["failed"] == 0, "Result must not be empty"
        assert results["total_energy"] > 0, "Value must be greater than zero"
        assert 0 <= results["entropy"] <= 1.0, "Result must not be empty"

    def test_performance_characteristics(self):
        """Test performance characteristics of test execution."""
        suite = QuantumTestSuite()

        # Add many quick tests
        for i in range(100):
            suite.add_test(QuantumTest(name=f"test_{i}", test_func=lambda: True, amplitude=0.8))

        import time

        start = time.time()
        results = suite.execute_with_thermodynamic_scheduling()
        elapsed = time.time() - start

        assert results["total"] == 100, "Result must not be empty"
        assert results["passed"] == 100, "Result must not be empty"
        # Should complete reasonably fast
        assert elapsed < 5.0, "elapsed is not valid"
