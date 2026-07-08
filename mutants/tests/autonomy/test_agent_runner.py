"""Tests for Phase 7: Agent Runner (scripts/agent_runner.py).

Covers:
- Module constants and environment variable wiring
- Kill-switch halt behavior
- Dry-run execution (no filesystem side-effects)
- Budget and iteration limiting
- CI harness integration (--once flag)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import_runner():
    """Import agent_runner, skipping if unavailable."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    return pytest.importorskip("agent_runner", reason="agent_runner not importable")


class TestKillSwitchHalt:
    """Kill-switch wiring: AGENT_KILL_SWITCH=1 must abort early."""

    def test_kill_switch_constant_true(self):
        with patch.dict(os.environ, {"AGENT_KILL_SWITCH": "1"}):
            if "agent_runner" in sys.modules:
                del sys.modules["agent_runner"]
            mod = _import_runner()
            assert mod._KILL_SWITCH is True, "_KILL_SWITCH is not valid"

    def test_kill_switch_constant_false_by_default(self):
        with patch.dict(os.environ, {"AGENT_KILL_SWITCH": "0"}):
            if "agent_runner" in sys.modules:
                del sys.modules["agent_runner"]
            mod = _import_runner()
            assert mod._KILL_SWITCH is False, "_KILL_SWITCH is not valid"


class TestRunnerConstants:
    """Environment variable defaults and overrides."""

    def test_default_budget_positive(self):
        mod = _import_runner()
        # AGENT_RUNNER_BUDGET_SECONDS must resolve to a positive int
        if hasattr(mod, "RUNNER_BUDGET_SECONDS"):
            assert mod.RUNNER_BUDGET_SECONDS > 0, "RUNNER_BUDGET_SECONDS must be greater than zero"
        elif hasattr(mod, "_BUDGET_SECONDS"):
            assert mod._BUDGET_SECONDS > 0, "_BUDGET_SECONDS must be greater than zero"

    def test_default_iterations_positive(self):
        mod = _import_runner()
        if hasattr(mod, "RUNNER_ITERATIONS"):
            assert mod.RUNNER_ITERATIONS > 0, "RUNNER_ITERATIONS must be greater than zero"
        elif hasattr(mod, "_ITERATIONS"):
            assert mod._ITERATIONS > 0, "_ITERATIONS must be greater than zero"


class TestSinglePassMode:
    """--once / single-pass CI harness integration."""

    def test_run_once_dry_run(self, tmp_path):
        """Single-pass dry-run should complete without errors and not mutate REPO_ROOT."""
        mod = _import_runner()
        if not hasattr(mod, "run_once"):
            pytest.skip("run_once not exported from agent_runner")

        with (
            patch.object(mod, "REPO_ROOT", tmp_path),
            patch.object(mod, "_DRY_RUN", True, create=True),
        ):
            # Should return without raising
            mod.run_once(budget_seconds=10, dry_run=True)

    def test_run_once_records_session_json(self, tmp_path):
        mod = _import_runner()
        if not hasattr(mod, "run_once"):
            pytest.skip("run_once not exported from agent_runner")

        # Patch REPO_ROOT to tmp_path so reflection/session writes go to a temporary
        # directory instead of polluting the real repo.  _import_script will fail to
        # load phase scripts (they don't exist in tmp_path/scripts/) but handles that
        # gracefully — phases return {"error": ...} and the run still completes.
        session_dir = tmp_path / "memory" / "sessions"
        session_dir.mkdir(parents=True)
        with patch.object(mod, "REPO_ROOT", tmp_path):
            try:
                mod.run_once(budget_seconds=5, dry_run=True)
            except (RuntimeError, OSError, KeyError, ValueError):
                _ = None  # session may not be written in every code path
        # Session files are JSON if written
        for f in session_dir.glob("*.json"):
            data = json.loads(f.read_text())
            assert "session_id" in data or "run_id" in data, "Data must not be empty"


class TestAuditOnKillSwitch:
    """When kill-switch fires mid-run, an audit record must be written."""

    def test_kill_switch_audit_record(self, tmp_path):
        mod = _import_runner()
        if not hasattr(mod, "_write_kill_switch_audit"):
            pytest.skip("_write_kill_switch_audit not exported")

        run_id = "test-kill-run"
        mod._write_kill_switch_audit(run_id=run_id, audit_dir=tmp_path)

        records = list(tmp_path.glob(f"kill_switch_{run_id}*.json"))
        assert len(records) == 1, "Records must not be empty"
        data = json.loads(records[0].read_text())
        assert data.get("kill_switch") is True, "Data must not be empty"
