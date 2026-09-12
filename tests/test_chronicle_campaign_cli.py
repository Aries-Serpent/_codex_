"""Tests for the chronicle campaign CLI enhancements."""

from __future__ import annotations

import json
import signal
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import codex.cli as cli_package
from scripts.ci.auto_fix_common_issues import CommonIssueFixer
from scripts.ci.enhanced_diagnostics import run_enhanced_diagnostics

CLICK_CLI_MODULE = sys.modules["codex._cli_click"]
CLI = cli_package.cli


@pytest.fixture()
def runner() -> CliRunner:
    """Create a Click runner."""

    return CliRunner()


@pytest.fixture(autouse=True)
def campaign_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolate all Chronicle-generated state inside a temporary repository."""

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.chdir(repo_root)
    evidence_dir = repo_root / ".codex" / "evidence"
    monkeypatch.setenv("CODEX_EVIDENCE_DIR", str(evidence_dir))
    monkeypatch.setattr(CLICK_CLI_MODULE, "REPO_ROOT", repo_root)
    monkeypatch.setattr(
        CLICK_CLI_MODULE,
        "CAMPAIGN_METRICS_LOG",
        repo_root / ".codex" / "campaign_metrics.jsonl",
    )

    # archive.api resolves these paths at import time, so isolate both the
    # environment-driven and already-imported forms.
    from aries_serpent_core.archive import api as archive_api

    monkeypatch.setattr(archive_api, "EVIDENCE_DIR", evidence_dir)
    monkeypatch.setattr(archive_api, "EVIDENCE_FILE", evidence_dir / "archive_ops.jsonl")
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
    output_path = campaign_repo / "diagnostics.json"
    with patch(
        "scripts.ci.enhanced_diagnostics.run_enhanced_diagnostics",
        return_value=fake_report,
    ) as mock_run:
        result = runner.invoke(
            CLI,
            [
                "chronicle",
                "auto-fix",
                "--check-only",
                "--json",
                "--output",
                str(output_path),
            ],
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "passed"
    mock_run.assert_called_once()
    assert mock_run.call_args.kwargs == {
        "repo_root": campaign_repo,
        "pattern": None,
        "pattern_name": None,
        "output_path": output_path,
        "timeout_seconds": 120.0,
    }
    metrics_path = campaign_repo / ".codex" / "campaign_metrics.jsonl"
    assert not metrics_path.exists()


def test_chronicle_autofix_check_only_timeout_is_nonzero_and_keeps_json(
    runner: CliRunner,
    campaign_repo: Path,
) -> None:
    """A bounded diagnostic timeout remains machine-readable and read-only."""

    output_path = campaign_repo / "diagnostics.json"
    fake_report = {
        "status": "timed_out",
        "total_issues": 0,
        "auto_fixable": 0,
        "manual_review": 0,
        "diagnostics_complete": False,
    }
    with patch(
        "scripts.ci.enhanced_diagnostics.run_enhanced_diagnostics",
        return_value=fake_report,
    ):
        result = runner.invoke(
            CLI,
            [
                "chronicle",
                "auto-fix",
                "--check-only",
                "--json",
                "--output",
                str(output_path),
                "--timeout-seconds",
                "1",
            ],
        )

    assert result.exit_code == 124
    assert json.loads(result.output)["status"] == "timed_out"
    assert not (campaign_repo / ".codex" / "campaign_metrics.jsonl").exists()


def test_check_only_does_not_persist_cascade_state(campaign_repo: Path) -> None:
    """Detection may update in-memory cascade counters but not tracked state."""

    state_path = campaign_repo / ".codex" / "cascade_detector_state.json"
    state_path.parent.mkdir(parents=True)
    original = '{"pattern_attempts": {}, "circuit_state": {}}\n'
    state_path.write_text(original, encoding="utf-8")

    fixer = CommonIssueFixer(campaign_repo, check_only=True)
    fixer.cascade_detector.record_attempt(1, ["src/example.py"])

    assert state_path.read_text(encoding="utf-8") == original


def test_enhanced_diagnostics_writes_requested_output(campaign_repo: Path) -> None:
    """The explicit diagnostics output remains the sole intended check-only write."""

    output_path = campaign_repo.parent / "chronicle-diagnostics.json"
    with patch.object(CommonIssueFixer, "run_all_patterns", return_value=False):
        report = run_enhanced_diagnostics(campaign_repo, output_path=output_path)

    assert output_path.exists()
    assert json.loads(output_path.read_text(encoding="utf-8")) == report
    assert report["diagnostics_complete"] is True
    assert not (campaign_repo / ".codex" / "campaign_metrics.jsonl").exists()
    assert not (campaign_repo / ".codex" / "cascade_detector_state.json").exists()


@pytest.mark.skipif(not hasattr(signal, "SIGALRM"), reason="POSIX interval timer required")
def test_enhanced_diagnostics_timeout_writes_partial_output(campaign_repo: Path) -> None:
    """A bounded scan stops and still writes structured partial diagnostics."""

    output_path = campaign_repo.parent / "chronicle-timeout.json"

    def slow_scan(_self: CommonIssueFixer, **_kwargs: object) -> bool:
        time.sleep(1)
        return False

    with patch.object(CommonIssueFixer, "run_all_patterns", slow_scan):
        report = run_enhanced_diagnostics(
            campaign_repo,
            output_path=output_path,
            timeout_seconds=0.01,
        )

    assert report["status"] == "timed_out"
    assert report["diagnostics_complete"] is False
    assert json.loads(output_path.read_text(encoding="utf-8")) == report


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
