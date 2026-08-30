"""Tests for the chronicle campaign CLI enhancements."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import codex.cli as cli_package

CLICK_CLI_MODULE = sys.modules["codex._cli_click"]
CLI = cli_package.cli


@pytest.fixture()
def runner() -> CliRunner:
    """Create a Click runner."""

    return CliRunner()


@pytest.fixture()
def campaign_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Patch the CLI module to write campaign artifacts into a temp repository."""

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr(CLICK_CLI_MODULE, "REPO_ROOT", repo_root)
    monkeypatch.setattr(
        CLICK_CLI_MODULE,
        "CAMPAIGN_METRICS_LOG",
        repo_root / ".codex" / "campaign_metrics.jsonl",
    )
    return repo_root


def test_chronicle_checkpoint_and_resume_round_trip(runner: CliRunner, campaign_repo: Path) -> None:
    """A created checkpoint can be restored through the CLI."""

    result = runner.invoke(
        CLI,
        [
            "chronicle",
            "checkpoint",
            "--session-id",
            "S-test",
            "--task",
            "stabilize chronicle campaign",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    checkpoint_id = payload["checkpoint_id"]

    resume_result = runner.invoke(
        CLI,
        ["chronicle", "resume-session", checkpoint_id, "--format", "json"],
    )
    assert resume_result.exit_code == 0, resume_result.output
    restored = json.loads(resume_result.output)
    assert restored["session_id"] == "S-test"
    assert restored["task"] == "stabilize chronicle campaign"


def test_chronicle_route_task_prefers_task_agent(runner: CliRunner) -> None:
    """Deterministic validation commands should recommend the task agent."""

    result = runner.invoke(
        CLI,
        ["chronicle", "route-task", "pytest -q tests/cli", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recommended_runner"] == "task"
    assert payload["recommended_agent"] == "task"


def test_chronicle_agent_chain_outputs_codeql_chain(runner: CliRunner) -> None:
    """The codeql chain should expose the dedicated remediation agents."""

    result = runner.invoke(
        CLI,
        ["chronicle", "agent-chain", "--focus", "codeql", "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    agents = [step["agent"] for step in payload["steps"]]
    assert agents == [
        "codeql-alert-resolution-agent",
        "code-scanning-remediation-agent",
    ]


def test_chronicle_autofix_check_only_uses_enhanced_diagnostics(
    runner: CliRunner,
    campaign_repo: Path,
) -> None:
    """Diagnostics mode should delegate to the enhanced diagnostics wrapper."""

    fake_report = {
        "status": "passed",
        "total_issues": 0,
        "auto_fixable": 0,
        "manual_review": 0,
        "next_steps": ["All auto-fixable issues resolved!"],
    }
    with patch(
        "scripts.ci.enhanced_diagnostics.run_enhanced_diagnostics",
        return_value=fake_report,
    ) as mock_run:
        result = runner.invoke(CLI, ["chronicle", "auto-fix", "--check-only", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "passed"
    mock_run.assert_called_once()
    assert mock_run.call_args.kwargs == {
        "repo_root": campaign_repo,
        "pattern": None,
        "pattern_name": None,
        "output_path": None,
    }
    metrics_path = campaign_repo / ".codex" / "campaign_metrics.jsonl"
    metrics = metrics_path.read_text(encoding="utf-8").strip().splitlines()
    assert metrics
    metric_payload = json.loads(metrics[-1])
    assert metric_payload["event"] == "autofix_invoked"
    assert metric_payload["mode"] == "diagnostics"


def test_chronicle_autofix_apply_uses_bulk_orchestrator(runner: CliRunner) -> None:
    """Remediation mode should delegate to the bulk remediation wrapper."""

    fake_report = {
        "status": "failed",
        "total_issues": 3,
        "auto_fixable": 2,
        "manual_review": 1,
        "next_steps": ["Run: python scripts/ci/auto_fix_common_issues.py"],
    }
    with patch(
        "scripts.ci.bulk_remediation_orchestrator.run_bulk_remediation",
        return_value=fake_report,
    ) as mock_run:
        result = runner.invoke(CLI, ["chronicle", "auto-fix", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["auto_fixable"] == 2
    mock_run.assert_called_once()
