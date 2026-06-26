"""
Test Prompt And Errors

Test module for prompt and errors.
"""

from pathlib import Path

from codex_audit.errors import (
    ErrorRecord,
    append_error_record,
    attach_ra_references,
    load_error_records,
)
from codex_audit.gates import run_gates
from codex_audit.policy import write_policy_mapping
from codex_audit.prompting import prepare_repo_status_prompt


def test_error_record_includes_ra_refs(tmp_path: Path) -> None:
    json_path = tmp_path / "errors.json"
    record = ErrorRecord(
        phase_id=2,
        step_label="2.5",
        description="Sample step",
        message="Something went wrong",
        brief_context="ctx",
    )
    attach_ra_references(record, ["RA-1", "RA-4"])
    append_error_record(json_path, record)
    assert json_path.exists(), "Condition must be true"
    stored = list(load_error_records(json_path))
    assert stored[0].ra_references == ["RA-1", "RA-4"]


def test_prepare_repo_status_prompt(tmp_path: Path) -> None:
    repo_root = Path.cwd()
    gate_results_path = tmp_path / "gate_results.json"
    policy_path = tmp_path / "ra_policy_map.json"
    scorecard_path = tmp_path / "repo_audit_scorecard.md"
    output_path = tmp_path / "repo_status_update_prompt.txt"

    write_policy_mapping(policy_path)
    run_gates(repo_root=repo_root, output_path=gate_results_path)

    prompt_path = prepare_repo_status_prompt(
        template_path=repo_root / "prompts" / "repo_status_update_for_codex.md",
        gate_results_path=gate_results_path,
        policy_map_path=policy_path,
        scorecard_path=scorecard_path,
        output_path=output_path,
    )

    assert prompt_path.exists(), "Condition must be true"
    contents = prompt_path.read_text(encoding="utf-8")
    assert "RA Policy Links" in contents, "Content must not be empty"
    assert "Gate Summary" in contents, "Content must not be empty"
    assert "repo_audit_scorecard.md" in contents, "Content must not be empty"
