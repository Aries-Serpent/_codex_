"""Tests for scripts/budget_uncertainty.py — Phase 4/5: Epistemic Uncertainty + Budget Caps.

Covers DirichletBeliefs, budget_cap decorator, BudgetExceeded,
scenario functions, persist_result, and main entry point.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Import helper ────────────────────────────────────────────────────────────


def _import():
    """Import budget_uncertainty, skipping if unavailable."""
    repo_root = Path(__file__).parent.parent.parent
    scripts_dir = str(repo_root / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    return pytest.importorskip("budget_uncertainty", reason="budget_uncertainty not importable")


# ── DirichletBeliefs ─────────────────────────────────────────────────────────


class TestDirichletBeliefs:
    def test_default_uniform_alphas(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b", "c"])
        assert b.alphas == [1.0, 1.0, 1.0]

    def test_posterior_means_uniform(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b"])
        pm = b.posterior_means
        assert abs(pm["a"] - 0.5) < 1e-9, "Condition must be true"
        assert abs(pm["b"] - 0.5) < 1e-9, "Condition must be true"

    def test_posterior_means_after_observe(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["pass", "fail"])
        b.observe("pass", weight=3.0)
        pm = b.posterior_means
        # alphas: [4.0, 1.0] → pass = 4/5 = 0.8
        assert abs(pm["pass"] - 0.8) < 1e-9, "Condition must be true"
        assert abs(pm["fail"] - 0.2) < 1e-9, "Condition must be true"

    def test_observe_increments_alpha(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["x", "y"])
        b.observe("x")
        assert b.alphas[0] == 2.0, "Condition must be true"

    def test_entropy_is_positive(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b", "c"])
        assert b.entropy > 0, "entropy must be greater than zero"

    def test_entropy_decreases_with_certainty(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b"])
        h_initial = b.entropy
        for _ in range(50):
            b.observe("a")
        assert b.entropy < h_initial, "entropy is not valid"

    def test_best_option(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["win", "lose"])
        b.observe("win", weight=10.0)
        assert b.best_option == "win", "best_option is not valid"

    def test_to_dict_keys(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b"])
        d = b.to_dict()
        assert "options" in d, "Condition must be true"
        assert "alphas" in d, "Condition must be true"
        assert "posterior_means" in d, "Condition must be true"
        assert "entropy" in d, "Condition must be true"
        assert "best_option" in d, "Condition must be true"

    def test_to_dict_entropy_rounded(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b"])
        d = b.to_dict()
        # Entropy should have at most 4 decimal places
        entropy_str = str(d["entropy"])
        if "." in entropy_str:
            assert len(entropy_str.split(".")[1]) <= 4, "Collection must not be empty"

    def test_custom_alphas(self):
        mod = _import()
        b = mod.DirichletBeliefs(options=["a", "b"], alphas=[2.0, 5.0])
        pm = b.posterior_means
        assert abs(pm["b"] - 5 / 7) < 1e-9, "Condition must be true"

    def test_observe_unknown_option_raises_clear_error(self):
        """observe() must raise ValueError with a clear message for unknown options."""
        mod = _import()
        b = mod.DirichletBeliefs(options=["pass", "fail"])
        with pytest.raises(ValueError, match="Unknown option"):
            b.observe("skip")

    def test_observe_unknown_option_message_names_expected_set(self):
        """Error message must name both the bad option and the valid options."""
        mod = _import()
        b = mod.DirichletBeliefs(options=["yes", "no"])
        with pytest.raises(ValueError, match="'maybe'"):
            b.observe("maybe")


# ── budget_cap decorator ─────────────────────────────────────────────────────


class TestBudgetCap:
    def test_does_not_raise_within_budget(self):
        mod = _import()

        @mod.budget_cap(max_seconds=10.0, label="test_fast")
        def fast_fn():
            return "ok"

        assert fast_fn() == "ok", "Condition must be true"

    def test_raises_budget_exceeded_when_over(self):
        mod = _import()

        @mod.budget_cap(max_seconds=0.001, label="test_slow")
        def slow_fn():
            time.sleep(0.05)
            return "done"

        with pytest.raises(mod.BudgetExceeded):
            slow_fn()

    def test_budget_exceeded_message_contains_label(self):
        mod = _import()

        @mod.budget_cap(max_seconds=0.001, label="my_task")
        def fn():
            time.sleep(0.05)

        with pytest.raises(mod.BudgetExceeded, match="my_task"):
            fn()

    def test_env_override_respected(self, monkeypatch):
        mod = _import()
        monkeypatch.setenv("UNCERTAINTY_BUDGET_SECONDS", "0.001")

        @mod.budget_cap(max_seconds=100.0, label="env_test")
        def fn():
            time.sleep(0.05)

        with pytest.raises(mod.BudgetExceeded):
            fn()

    def test_preserves_return_value(self):
        mod = _import()

        @mod.budget_cap(max_seconds=5.0)
        def fn():
            return 42

        assert fn() == 42, "Condition must be true"


# ── scenario functions ───────────────────────────────────────────────────────


class TestScenarios:
    def test_scenario_ci_health_returns_dict(self, tmp_path, monkeypatch):
        mod = _import()
        # Patch the REPO_ROOT so no real file is read
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        result = mod.scenario_ci_health()
        assert isinstance(result, dict)
        assert "beliefs" in result, "Result must not be empty"

    def test_scenario_ci_health_with_summary_file(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        summary = tmp_path / "validation_summary.json"
        summary.write_text(json.dumps({"status": "failed"}), encoding="utf-8")
        result = mod.scenario_ci_health()
        assert isinstance(result, dict)
        assert "beliefs" in result, "Result must not be empty"

    def test_scenario_ci_health_with_pass_status(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        summary = tmp_path / "validation_summary.json"
        summary.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
        result = mod.scenario_ci_health()
        assert isinstance(result, dict)

    def test_scenario_decision_returns_dict(self):
        mod = _import()
        result = mod.scenario_decision(["option_a", "option_b", "option_c"])
        assert isinstance(result, dict)
        assert "beliefs" in result, "Result must not be empty"

    def test_scenario_decision_best_option_in_options(self):
        mod = _import()
        opts = ["alpha", "beta", "gamma"]
        result = mod.scenario_decision(opts)
        assert result["beliefs"]["best_option"] in opts, "Result must not be empty"


# ── persist_result ───────────────────────────────────────────────────────────


class TestPersistResult:
    def test_writes_json_file(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "BUDGET_DIR", tmp_path / "budget")
        result = {"beliefs": {"best_option": "a"}, "scenario": "test"}
        path = mod.persist_result(result)
        assert path.exists(), "Condition must be true"
        data = json.loads(path.read_text())
        assert data["scenario"] == "test", "Data must not be empty"

    def test_creates_budget_dir(self, tmp_path, monkeypatch):
        mod = _import()
        budget_dir = tmp_path / "new_budget_dir"
        monkeypatch.setattr(mod, "BUDGET_DIR", budget_dir)
        mod.persist_result({"beliefs": {}, "scenario": "test"})
        assert budget_dir.exists(), "Condition must be true"


# ── main entry point ─────────────────────────────────────────────────────────


class TestMain:
    def test_main_ci_health_scenario(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "BUDGET_DIR", tmp_path / "budget")
        with patch("sys.argv", ["budget_uncertainty.py", "--scenario", "ci_health"]):
            rc = mod.main()
        assert rc == 0, "rc is not valid"

    def test_main_decision_scenario(self, tmp_path, monkeypatch):
        mod = _import()
        monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(mod, "BUDGET_DIR", tmp_path / "budget")
        with patch(
            "sys.argv",
            [
                "budget_uncertainty.py",
                "--scenario",
                "decision",
                "--options",
                "pass fail skip",
            ],
        ):
            rc = mod.main()
        assert rc == 0, "rc is not valid"
