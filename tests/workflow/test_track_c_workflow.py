"""
Test Track C Workflow

Test module for track c workflow.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from codex_ml.workflow import DEFAULT_ROUTER, WorkflowOrchestrator, run_capability
from codex_ml.workflow.track_c_workflow import (
    SIX_PHASES,
    CapabilityPlan,
    CapabilityRouter,
    WorkflowContext,
)


def test_phase_ordering_and_summary() -> None:
    ctx = run_capability("tokenization", router=DEFAULT_ROUTER)
    assert ctx.phase_history == list(SIX_PHASES), "phase_history is not valid"
    assert ctx.summary["capability"] == "tokenization", "Condition must be true"
    assert "artifacts" in ctx.summary, "Condition must be true"


def test_capability_routing_alias() -> None:
    ctx = run_capability("token", router=DEFAULT_ROUTER)
    assert ctx.capability == "tokenization", "capability is not valid"
    assert "tokenization" in ctx.routes, "Condition must be true"


def test_error_capture_and_rollbacks(tmp_path: Path) -> None:
    def failing_construction(
        ctx: WorkflowContext, plan: CapabilityPlan
    ) -> None:  # pragma: no cover - executed in test
        ctx.register_rollback(
            "failing_construction", lambda context: context.notes.append("rolled-back")
        )
        raise RuntimeError("synthetic failure")

    plan = CapabilityPlan(
        name="unstable",
        aliases=("unstable-alias",),
        search_targets=("inputs",),
        construction_steps=("will-fail",),
        pruning_rules=("none",),
        phase_overrides={"Best-Effort Construction": failing_construction},
    )
    router = CapabilityRouter([plan])
    orchestrator = WorkflowOrchestrator(router=router)
    ctx = orchestrator.run("unstable-alias")

    assert ctx.errors, "Expected error record from failing phase"
    assert ctx.errors[0].phase == "Best-Effort Construction", "Error should be raised or set"
    assert "rolled-back" in ctx.notes, "Condition must be true"


@pytest.mark.parametrize("capability", ["tokenization"])
def test_cli_entrypoint_runs_offline(capability: str, tmp_path: Path) -> None:
    summary_path = tmp_path / "summary.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_codex_workflow.py",
            "--capability",
            capability,
            "--summary",
            str(summary_path),
            "--require-phase-order",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload[0]["offline"] is True, "Condition must be true"
    assert payload[0]["phases"] == list(SIX_PHASES), "Condition must be true"
