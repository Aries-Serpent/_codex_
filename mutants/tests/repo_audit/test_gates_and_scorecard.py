"""
Test Gates And Scorecard

Test module for gates and scorecard.
"""

from pathlib import Path

from codex_audit.gates import run_gates
from codex_audit.policy import write_policy_mapping
from codex_audit.scorecard import render_scorecard


def test_run_gates_and_render_scorecard(tmp_path: Path) -> None:
    repo_root = Path.cwd()
    gate_results_path = tmp_path / "gate_results.json"
    policy_path = tmp_path / "ra_policy_map.json"
    scorecard_path = tmp_path / "repo_audit_scorecard.md"

    policy_map = write_policy_mapping(policy_path)
    results = run_gates(repo_root=repo_root, output_path=gate_results_path)
    assert gate_results_path.exists(), "Result must not be empty"
    assert results, "Gate results should contain entries"

    output = render_scorecard(
        gate_results_path=gate_results_path, policy_map=policy_map, output_path=scorecard_path
    )
    assert output.exists(), "Condition must be true"
    text = output.read_text(encoding="utf-8")
    assert "Repo Audit Scorecard" in text, "Condition must be true"
    assert "GATE-" in text, "Condition must be true"
    assert "RA-" in text, "Condition must be true"
