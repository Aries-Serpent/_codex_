"""
Test Codex Audit Orchestrator

Test module for codex audit orchestrator.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools import codex_audit_orchestrator as orchestrator


def _patch_output_roots(tmp_path: Path) -> None:
    orchestrator.AUDIT_ROOT = tmp_path / "audit_artifacts"
    orchestrator.CONTEXT_DIR = orchestrator.AUDIT_ROOT / "context"
    orchestrator.GAP_PLANS_DIR = orchestrator.AUDIT_ROOT / "gap_plans"
    orchestrator.ERROR_CAPTURES_DIR = orchestrator.AUDIT_ROOT / "error_captures"
    orchestrator.LOGS_DIR = orchestrator.AUDIT_ROOT / "logs"
    orchestrator.REPORTS_DIR = orchestrator.AUDIT_ROOT / "reports"


def test_orchestrator_steps_create_artifacts(tmp_path):
    """End-to-end smoke test for key orchestrator phases."""

    _patch_output_roots(tmp_path)

    orchestrator.step_1_2_create_output_dirs()
    orchestrator.step_1_1_resolve_repo_root_and_branches()
    orchestrator.step_2_2_stub_scan()
    orchestrator.step_3_3_repro_checklist()

    repo_context = orchestrator.CONTEXT_DIR / "repo_context.json"
    stub_index = orchestrator.CONTEXT_DIR / "stub_index.json"
    repro_doc = orchestrator.REPORTS_DIR / "_codex_reproducibility_checklist_proposed.md"

    assert repo_context.exists(), "repo context should be serialized"
    data = json.loads(repo_context.read_text())
    assert data.get("current_branch"), "branch info should be populated"
    assert orchestrator.LOGS_DIR.exists(), "log directory created"

    assert stub_index.exists(), "stub index should be written"
    stub_data = json.loads(stub_index.read_text())
    assert "stubs" in stub_data, "Data must not be empty"

    assert repro_doc.exists(), "repro checklist proposal is expected"
    assert "Reproducibility Checklist" in repro_doc.read_text(), "Condition must be true"


def test_list_steps_subprocess(tmp_path):
    """Ensure the CLI surfaces available steps without modifying the repo."""

    script = Path(__file__).resolve().parents[2] / "tools" / "codex_audit_orchestrator.py"
    result = subprocess.run(
        [sys.executable, str(script), "--list-steps"],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )

    assert result.returncode == 0, "Result must not be empty"
    assert "1.1" in result.stdout or "1.2" in result.stdout, "Result must not be empty"


def test_main_exits_non_zero_on_step_failure(tmp_path, monkeypatch):
    """`main` should propagate failures instead of masking them."""

    _patch_output_roots(tmp_path)

    def failing_step(ctx):
        return None

    failing_wrapped = orchestrator.phase_step(1, "1.1", "Test step")(failing_step)
    monkeypatch.setattr(orchestrator, "PHASE_FUNCTIONS", [failing_wrapped])

    exit_code = orchestrator.main(["--steps", "1.1"])

    assert exit_code == 1, "exit_code is not valid"
