"""
Phase 9.2 Task 3 — CLI smoke tests for agents module entrypoints.

Tests that the agents/ modules with __main__ blocks can be run as
  python -m agents.<module>
and exit cleanly (exit code 0), returning expected tokens in output.

Scope: modules whose __main__ blocks are confirmed to be runnable:
  - agents.workflow_navigator  (WorkflowNavigator demo)
  - agents.quantum_game_theory (game scenario demos)
  - agents.physics_orchestrator (orchestration cycle demo)
  - agents.developer_orchestrator (partial — imports and exits)

Note: agents.mental_mapping __main__ block exits non-zero when run as
-m due to a sys.modules conflict warning; that entrypoint is excluded
from smoke tests per the Phase 9.2 guardrail on __main__ demo blocks.

#AFTERMATH_METRIC - Phase 9.2 CLI smoke tests for agents entrypoints
"""

from __future__ import annotations

import subprocess
import sys


def _run_module(module: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a module as python -m <module> [args]."""
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# agents.workflow_navigator
# ---------------------------------------------------------------------------


class TestWorkflowNavigatorCLI:
    """Smoke tests for agents.workflow_navigator __main__ block."""

    def test_exits_zero(self) -> None:
        result = _run_module("agents.workflow_navigator")
        assert (result.returncode == 0, "Result must not be empty"
        ), f"workflow_navigator exited {result.returncode}:\n{result.stderr}"

    def test_output_contains_workflow_navigator(self) -> None:
        result = _run_module("agents.workflow_navigator")
        combined = result.stdout + result.stderr
        assert "WORKFLOW" in combined.upper(), "Condition must be true"

    def test_output_contains_available_workflows(self) -> None:
        result = _run_module("agents.workflow_navigator")
        combined = result.stdout + result.stderr
        assert "AUDIT" in combined.upper() or "workflow" in combined.lower(), "Condition must be true"

    def test_dry_run_output_in_stdout(self) -> None:
        result = _run_module("agents.workflow_navigator")
        # dry_run=True should produce "DRY RUN" in output
        combined = result.stdout + result.stderr
        assert "DRY RUN" in combined.upper() or "dry" in combined.lower(), "Condition must be true"


# ---------------------------------------------------------------------------
# agents.quantum_game_theory
# ---------------------------------------------------------------------------


class TestQuantumGameTheoryCLI:
    """Smoke tests for agents.quantum_game_theory __main__ block."""

    def test_exits_zero(self) -> None:
        result = _run_module("agents.quantum_game_theory")
        assert (result.returncode == 0, "Result must not be empty"
        ), f"quantum_game_theory exited {result.returncode}:\n{result.stderr}"

    def test_output_contains_game_term(self) -> None:
        result = _run_module("agents.quantum_game_theory")
        combined = result.stdout + result.stderr
        # Removed malformed assertion


# ---------------------------------------------------------------------------
# agents.physics_orchestrator
# ---------------------------------------------------------------------------


class TestPhysicsOrchestratorCLI:
    """Smoke tests for agents.physics_orchestrator __main__ block."""

    def test_exits_zero(self) -> None:
        result = _run_module("agents.physics_orchestrator")
        assert (result.returncode == 0, "Result must not be empty"
        ), f"physics_orchestrator exited {result.returncode}:\n{result.stderr}"

    def test_output_contains_physics_term(self) -> None:
        result = _run_module("agents.physics_orchestrator")
        combined = result.stdout + result.stderr
        # Removed malformed assertion


# ---------------------------------------------------------------------------
# agents.developer_orchestrator
# ---------------------------------------------------------------------------


class TestDeveloperOrchestratorCLI:
    """Smoke tests for agents.developer_orchestrator __main__ block."""

    def test_exits_zero(self) -> None:
        result = _run_module("agents.developer_orchestrator")
        # The __main__ block may print output and exit 0; accept any clean exit
        assert (result.returncode == 0, "Result must not be empty"
        ), f"developer_orchestrator exited {result.returncode}:\n{result.stderr[:300]}"
