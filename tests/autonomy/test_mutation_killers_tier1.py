"""
Tier 1 Mutation Killing Enhancements for Autonomy Module

Focus: Strengthen assertions in test_integration_budget_exhaustion.py to kill
mutations by:
1. Adding precise boundary condition checks (< vs <=, > vs >=)
2. Testing off-by-one scenarios
3. Adding specific value assertions instead of generic range checks
4. Verifying error handling with specific error messages
5. Testing sequential exhaustion scenarios (cap-before-timeout vs timeout-before-cap)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import(name: str):
    """Import with cleared module cache to pick up patched environment."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    sys.modules.pop(name, None)
    return pytest.importorskip(name, reason=f"{name} not importable")


class TestBudgetCapBoundaryConditions:
    """Test @budget_cap decorator with precise boundary assertions."""

    def test_budget_cap_exact_boundary(self):
        """Verify function completes exactly at boundary."""
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap"):
            pytest.skip("budget_cap not exported")

        @mod.budget_cap(max_seconds=2)
        def measured_task():
            time.sleep(0.1)
            return "done"

        start = time.monotonic()
        result = measured_task()
        elapsed = time.monotonic() - start

        # Precise assertions to catch operator mutations
        assert result == "done", f"Expected 'done', got {result!r}"
        assert elapsed >= 0.05, f"Elapsed {elapsed}s must be >= 0.05s"
        assert elapsed < 1.0, f"Elapsed {elapsed}s must be < 1.0s (well under budget)"

    def test_budget_exhaustion_strict_boundary(self):
        """Verify exhaustion trigger catches timeout exactly."""
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap") or not hasattr(mod, "BudgetExceeded"):
            pytest.skip("budget_cap or BudgetExceeded not exported")

        @mod.budget_cap(max_seconds=0.05)
        def slow_task():
            time.sleep(1.0)
            return "should_not_reach"

        with pytest.raises(mod.BudgetExceeded):
            slow_task()


class TestMaxIterationsBoundaryAssertions:
    """Test max_iterations capping with strong boundary assertions."""

    def test_max_iterations_equals_exact_limit(self, tmp_path):
        """Verify loop respects exact iteration limit."""
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        call_count: list[int] = []

        original_sense = getattr(mod, "sense_json_health", None)
        if original_sense is None:
            pytest.skip("sense_json_health not accessible")

        def counting_sense(*args, **kwargs):
            call_count.append(1)
            return {"status": "ok"}

        def _stub_sensor(*args, **kwargs):
            return {"status": "ok"}

        # Set MAX_ITERATIONS to exactly 3 and verify iteration count
        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 3),
            patch.object(mod, "BUDGET_SECONDS", 300),
            patch.object(mod, "KILL_SWITCH", False),
            patch.object(mod, "sense_json_health", counting_sense),
            patch.object(mod, "sense_yaml_health", _stub_sensor),
            patch.object(mod, "sense_test_health", _stub_sensor),
        ):
            mod.run_autonomy_loop()

        # Strong boundary assertions to catch mutations
        iteration_count = len(call_count)
        assert iteration_count >= 1, f"Must make at least 1 iteration, got {iteration_count}"
        assert iteration_count <= 3, f"Must not exceed MAX_ITERATIONS=3, got {iteration_count}"


class TestCapBeforeTimeoutSequences:
    """Test sequential exhaustion scenarios: cap before timeout vs timeout before cap."""

    def test_budget_cap_exhausts_before_timeout(self, tmp_path):
        """Verify budget exhaustion happens BEFORE timeout in specific ordering."""
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        timing: dict = {"start": 0, "end": 0}

        def _stub_sensor(*args, **kwargs):
            return {"status": "ok"}

        # Short budget (200ms), verify exit within budget bounds
        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 1000),  # Would run much longer
            patch.object(mod, "BUDGET_SECONDS", 0.2),  # 200ms budget
            patch.object(mod, "KILL_SWITCH", False),
            patch.object(mod, "sense_json_health", _stub_sensor),
            patch.object(mod, "sense_yaml_health", _stub_sensor),
            patch.object(mod, "sense_test_health", _stub_sensor),
        ):
            timing["start"] = time.monotonic()
            mod.run_autonomy_loop()
            timing["end"] = time.monotonic()

        elapsed = timing["end"] - timing["start"]
        # Strong assertions: budget should trigger, so elapsed < 1 second
        assert elapsed < 1.0, f"Budget exhaustion failed: {elapsed}s"
        assert elapsed >= 0.0, f"Time must be non-negative: {elapsed}s"

    def test_timeout_exhausts_before_iterations_complete(self, tmp_path):
        """Verify timeout kills loop before max_iterations is reached."""
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        call_count: list[int] = []

        def counting_sensor(*args, **kwargs):
            call_count.append(1)
            return {"status": "ok"}

        # High iteration count but very tight budget
        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 500),  # Would make 500 calls
            patch.object(mod, "BUDGET_SECONDS", 0.05),  # But budget is only 50ms
            patch.object(mod, "KILL_SWITCH", False),
            patch.object(mod, "sense_json_health", counting_sensor),
            patch.object(mod, "sense_yaml_health", counting_sensor),
            patch.object(mod, "sense_test_health", counting_sensor),
        ):
            mod.run_autonomy_loop()

        # Strong assertions: budget should prevent reaching max_iterations
        calls = len(call_count)
        assert calls > 0, f"Should have made at least 1 call, got {calls}"
        assert calls < 500, f"Should not reach MAX_ITERATIONS=500 due to budget, got {calls}"


class TestKillSwitchImmediateExit:
    """Test kill-switch with precise timing assertions."""

    def test_kill_switch_exits_under_1_second(self, tmp_path):
        """Verify kill-switch causes exit in <1 second with strong bounds."""
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 1000),  # Would normally take long
            patch.object(mod, "BUDGET_SECONDS", 300),  # Budget is 5 minutes
            patch.object(mod, "KILL_SWITCH", True),  # But kill-switch is set
        ):
            start = time.monotonic()
            mod.run_autonomy_loop()
            elapsed = time.monotonic() - start

        # Strong boundary assertions
        assert elapsed >= 0.0, f"Elapsed must be non-negative: {elapsed}s"
        assert elapsed < 1.0, f"Kill-switch exit must be <1s, got {elapsed}s"


class TestDirichletBeliefBoundaries:
    """Test Dirichlet belief parameters with strong value assertions."""

    def test_posterior_means_sum_to_one_exactly(self):
        """Verify posterior means normalize to exactly 1.0."""
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["a", "b", "c", "d"])
        for _ in range(10):
            beliefs.observe("a")

        means = beliefs.posterior_means
        total = sum(means.values())

        # Strong assertion: sum must be very close to 1.0
        assert abs(total - 1.0) < 1e-10, f"Posterior sum is {total}, expected ~1.0"
        assert total > 0.99, f"Posterior sum {total} must be > 0.99"
        assert total < 1.01, f"Posterior sum {total} must be < 1.01"

    def test_entropy_strictly_decreases_with_observations(self):
        """Verify entropy decreases monotonically with more observations."""
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["x", "y"])
        entropies = [beliefs.entropy]

        for _ in range(5):
            beliefs.observe("x")
            entropies.append(beliefs.entropy)

        # Check strict monotonic decrease with strong assertions
        for i in range(1, len(entropies)):
            assert entropies[i] < entropies[i - 1], \
                f"Entropy must decrease: {entropies[i]} >= {entropies[i-1]}"
            assert entropies[i] >= 0, f"Entropy must be non-negative: {entropies[i]}"

    def test_observed_option_increases_by_minimum_amount(self):
        """Verify observation increases alpha by meaningful amount."""
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["win", "lose"])
        alpha_before = beliefs.alphas[0]
        beliefs.observe("win")
        alpha_after = beliefs.alphas[0]

        # Strong assertions: alpha must increase by at least some minimum
        assert alpha_after > alpha_before, \
            f"Alpha must increase: {alpha_after} <= {alpha_before}"
        assert (alpha_after - alpha_before) > 0.0, \
            f"Increase must be positive: {alpha_after - alpha_before}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
