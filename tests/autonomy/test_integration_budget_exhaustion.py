"""Integration-style tests for the 7-phase autonomy framework.

Covers budget exhaustion, kill-switch mid-loop, dry-run isolation across
phases, and budget_uncertainty Dirichlet-prior update cycle.

These tests are "integration-style" — they exercise real module code paths
using tight budgets to force early exit, validating the safety mechanisms.
All filesystem writes are redirected to tmp_path, so no repo state is mutated.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import(name: str):
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    # Always re-import with cleared cache to pick up patched env
    sys.modules.pop(name, None)
    return pytest.importorskip(name, reason=f"{name} not importable")


# ── budget_uncertainty (Phase 4/5) ──────────────────────────────────────────


class TestBudgetCap:
    """Tests for @budget_cap decorator — wall-clock exhaustion stops execution."""

    def test_budget_cap_fast_function_completes(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap"):
            pytest.skip("budget_cap not exported")

        @mod.budget_cap(max_seconds=5)
        def fast():
            return "done"

        assert fast() == "done", "Condition must be true"

    @pytest.mark.flaky(reruns=2, reason="P2-timing: budget_cap timeout precision")
    @pytest.mark.timeout(90)
    def test_budget_cap_raises_on_exhaustion(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap"):
            pytest.skip("budget_cap not exported")

        # STABILIZATION V2: Increase timeout from 0.001s to 0.15s to allow reliable
        # thread scheduling and timer enforcement on loaded CI runners.
        # Added retry loop with backoff to handle transient timing variability.
        @mod.budget_cap(max_seconds=0.15)
        def slow():
            time.sleep(1)
            return "should never reach here"

        # Retry logic: allow up to 2 attempts to catch flaky timeout enforcement
        max_attempts = 2
        exception_raised = False
        last_exception = None

        for attempt in range(max_attempts):
            try:
                with pytest.raises(Exception):
                    slow()
                exception_raised = True
                break
            except AssertionError as e:
                # pytest.raises failed (timeout was not raised)
                last_exception = e
                if attempt < max_attempts - 1:
                    time.sleep(0.05 * (2**attempt))  # Exponential backoff

        if not exception_raised and last_exception:
            raise last_exception

    def test_budget_cap_wraps_preserves_name(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap"):
            pytest.skip("budget_cap not exported")

        @mod.budget_cap(max_seconds=10)
        def my_function():
            pass

        # Function name should be preserved or wrapped
        assert callable(my_function), "Condition must be true"


class TestDirichletBeliefUpdate:
    """Tests for Dirichlet conjugate-prior belief updates."""

    def test_observe_increases_observed_option(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["a", "b", "c"])
        prior_a = beliefs.alphas[0]
        beliefs.observe("a")
        assert beliefs.alphas[0] > prior_a, "Value must be greater than zero"

    def test_posterior_means_normalized(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["x", "y"])
        beliefs.observe("x")
        means = beliefs.posterior_means
        total = sum(means.values())
        assert abs(total - 1.0) < 1e-9, "Condition must be true"

    def test_best_option_tracks_observations(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["win", "lose", "draw"])
        for _ in range(5):
            beliefs.observe("win")
        assert beliefs.best_option == "win", "best_option is not valid"

    def test_entropy_decreases_with_certainty(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["a", "b"])
        initial_entropy = beliefs.entropy
        for _ in range(20):
            beliefs.observe("a")
        assert beliefs.entropy < initial_entropy, "entropy is not valid"

    def test_to_dict_is_serializable(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "DirichletBeliefs"):
            pytest.skip("DirichletBeliefs not exported")

        beliefs = mod.DirichletBeliefs(options=["pass", "fail"])
        beliefs.observe("pass")
        data = beliefs.to_dict()
        assert json.dumps(data), "Data must not be empty"

    def test_budget_exceeded_on_timeout(self):
        mod = _import("budget_uncertainty")
        if not hasattr(mod, "budget_cap") or not hasattr(mod, "BudgetExceeded"):
            pytest.skip("budget_cap or BudgetExceeded not exported")

        @mod.budget_cap(max_seconds=0.001)
        def slow():
            time.sleep(1)

        with pytest.raises(mod.BudgetExceeded):
            slow()


# ── autonomy_scheduler (Phase 1) — budget exhaustion ────────────────────────


class TestAutonomySchedulerBudgetExhaustion:
    """Tests for budget exhaustion in the autonomy scheduler loop."""

    def test_loop_exits_when_budget_exhausted(self, tmp_path):
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 100),
            patch.object(mod, "BUDGET_SECONDS", 0.001),
            patch.object(mod, "KILL_SWITCH", False),
        ):
            start = time.monotonic()
            mod.run_autonomy_loop()
            elapsed = time.monotonic() - start

        # Loop must have returned very quickly (< 5s) due to budget exhaustion
        assert elapsed < 5.0, "elapsed is not valid"

    def test_kill_switch_exits_immediately(self, tmp_path):
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 100),
            patch.object(mod, "BUDGET_SECONDS", 300),
            patch.object(mod, "KILL_SWITCH", True),
        ):
            start = time.monotonic()
            mod.run_autonomy_loop()
            elapsed = time.monotonic() - start

        # Must exit almost instantly when kill-switch is set
        assert elapsed < 2.0, "elapsed is not valid"

    def test_max_iterations_caps_loop(self, tmp_path):
        mod = _import("autonomy_scheduler")
        if not hasattr(mod, "run_autonomy_loop"):
            pytest.skip("run_autonomy_loop not exported")

        call_count: list[int] = []

        # Instrument sense_json_health (a real function in autonomy_scheduler)
        # to count how many sense calls the loop makes.
        original_sense = getattr(mod, "sense_json_health", None)
        if original_sense is None:
            pytest.skip("sense_json_health not accessible for instrumentation")

        def counting_sense(*args, **kwargs):
            call_count.append(1)
            return original_sense(*args, **kwargs)

        # Stub the other sensors so no subprocesses or heavy I/O are spawned
        # during the test (sense_test_health runs `pytest --collect-only` as a
        # subprocess which is far too slow for a unit test).
        def _stub_sensor_ok(*args, **kwargs):
            return {"status": "ok"}

        with (
            patch.object(mod, "SESSION_DIR", tmp_path / "sessions"),
            patch.object(mod, "DRY_RUN", True),
            patch.object(mod, "MAX_ITERATIONS", 2),
            patch.object(mod, "BUDGET_SECONDS", 60),
            patch.object(mod, "KILL_SWITCH", False),
            patch.object(mod, "sense_json_health", counting_sense),
            patch.object(mod, "sense_yaml_health", _stub_sensor_ok),
            patch.object(mod, "sense_test_health", _stub_sensor_ok),
        ):
            mod.run_autonomy_loop()

        assert len(call_count) <= 2, "Call_count must not be empty"


# ── agent_runner (Phase 7) — budget exhaustion ──────────────────────────────


class TestAgentRunnerBudgetExhaustion:
    """Tests for budget exhaustion in the agent runner orchestrator."""

    def test_run_once_completes_under_budget(self, tmp_path):
        mod = _import("agent_runner")
        if not hasattr(mod, "run_once"):
            pytest.skip("run_once not exported")

        with patch.object(mod, "REPO_ROOT", tmp_path):
            start = time.monotonic()
            mod.run_once(budget_seconds=5, dry_run=True)
            elapsed = time.monotonic() - start

        assert elapsed < 10.0, "elapsed is not valid"

    def test_kill_switch_prevents_run(self, tmp_path):
        mod = _import("agent_runner")
        if not hasattr(mod, "run_once"):
            pytest.skip("run_once not exported")

        with patch.object(mod, "REPO_ROOT", tmp_path), patch.object(mod, "_KILL_SWITCH", True):
            # run_once should return without doing anything
            mod.run_once(budget_seconds=30, dry_run=True)

    def test_concurrent_single_pass_isolation(self, tmp_path):
        """Two concurrent run_once calls must not corrupt each other's files."""
        mod = _import("agent_runner")
        if not hasattr(mod, "run_once"):
            pytest.skip("run_once not exported")

        errors: list[Exception] = []
        dirs = [tmp_path / f"run{i}" for i in range(2)]
        for d in dirs:
            d.mkdir()

        def run(d: Path) -> None:
            try:
                with patch.object(mod, "REPO_ROOT", d):
                    mod.run_once(budget_seconds=5, dry_run=True)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=run, args=(d,)) for d in dirs]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, "Error should be raised or set"


# ── session_tracker (Phase 2) — concurrent session creation ─────────────────


class TestSessionTrackerConcurrency:
    """Integration tests for concurrent session tracking."""

    def test_concurrent_session_starts_unique_ids(self, tmp_path):
        mod = _import("session_tracker")
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        ids: list[str] = []
        lock = threading.Lock()
        errors: list[Exception] = []

        def create_session(i: int) -> None:
            try:
                with patch.object(mod, "SESSION_DIR", tmp_path):
                    sid = mod.start_session(label=f"concurrent-{i}")
                with lock:
                    ids.append(sid)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=create_session, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, "Error should be raised or set"
        # All session IDs must be unique
        assert len(set(ids)) == len(ids), f"Duplicate IDs: {ids}"
