"""
Test Selection Guard

Test module for selection guard.
"""

import json
from pathlib import Path

import tools.selection_guard as sg

RULES = {
    "required_signals": [
        "docs/rubrics/codex_eval_rubric_v3.md",
        "docs/ops/local_gates.md",
        "docs/checklists/approval_gate_checklist.md",
        "docs/samples/intent_validation_example.md",
        "samples/broken_fence.sample.md",
        "tests/evaluators/test_validate_fences_sample.py",
        "tests/samples/test_samples_exist.py",
    ],
    "path_hints": ["output_diff.diff", "pr_message", "diff"],
    "selection_path_hint": "turn_mapping.task_e_*~*.turn.worklog.messages[*]",
}


def _cand(payload: str) -> dict:
    return {"turn": {"pr": {"output_diff": {"diff": payload}}, "pr_message": payload}}


def test_iter_candidates_uses_selection_hint() -> None:
    data = {
        "turn_mapping": {
            "task_e_001~usertrn_foo": {
                "turn": {
                    "worklog": {
                        "messages": [
                            {"id": "a1"},
                            {"id": "a2"},
                        ]
                    }
                }
            },
            "a1": _cand("touch README.md"),
            "a2": _cand(
                "docs/ops/local_gates.md and docs/checklists/approval_gate_checklist.md and "
                "docs/rubrics/codex_eval_rubric_v3.md and samples/broken_fence.sample.md and "
                "tests/samples/test_samples_exist.py and tests/evaluators/test_validate_fences_sample.py and "
                "docs/samples/intent_validation_example.md"
            ),
        }
    }
    candidates = sg._iter_candidates(data, RULES)
    assert [cand.turn_id for cand in candidates] == ["a1", "a2"]


def test_ranks_candidate_with_required_signals(tmp_path: Path) -> None:
    tm = {
        "task_e_001~usertrn_foo": {"children": ["a1", "a2", "a3", "a4"]},
        "a1": _cand("touch README.md"),
        "a2": _cand("add docs/ops/local_gates.md and docs/checklists/approval_gate_checklist.md"),
        "a3": _cand(
            "add docs/rubrics/codex_eval_rubric_v3.md and samples/broken_fence.sample.md and "
            "tests/samples/test_samples_exist.py and tests/evaluators/test_validate_fences_sample.py "
            "and docs/samples/intent_validation_example.md and docs/ops/local_gates.md and "
            "docs/checklists/approval_gate_checklist.md"
        ),
        "a4": _cand("update PR template only"),
    }
    data = {"turn_mapping": tm}
    candidates = sg._iter_candidates(data, RULES)
    assert len(candidates) == 4, "Candidates must not be empty"
    assert not candidates[2].missing, "Condition must be true"


def test_cli_selected_fails_when_missing(tmp_path: Path, monkeypatch) -> None:
    tm = {
        "task_e_001~usertrn_foo": {"children": ["a1", "a2"]},
        "a1": _cand("just a diff without docs"),
        "a2": _cand(
            "docs/ops/local_gates.md and docs/checklists/approval_gate_checklist.md and "
            "docs/rubrics/codex_eval_rubric_v3.md and samples/broken_fence.sample.md and "
            "tests/samples/test_samples_exist.py and tests/evaluators/test_validate_fences_sample.py and "
            "docs/samples/intent_validation_example.md"
        ),
    }
    data = {"turn_mapping": tm}
    rules_path = tmp_path / "rules.json"
    data_path = tmp_path / "summary.json"
    rules_path.write_text(json.dumps(RULES), encoding="utf-8")
    data_path.write_text(json.dumps(data), encoding="utf-8")

    rc = sg.main(["--rules", str(rules_path), "--input", str(data_path), "--selected", "1"])
    assert rc == 1, "rc is not valid"
    rc2 = sg.main(["--rules", str(rules_path), "--input", str(data_path), "--selected", "2"])
    assert rc2 == 0, "rc2 is not valid"
