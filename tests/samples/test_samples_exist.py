"""
Test Samples Exist

Test module for samples exist.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_sample_files_present():
    expected = [
        ROOT / "samples" / "assistant_message_summary.sample.json",
        ROOT / "samples" / "broken_fence.sample.md",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    assert not missing, f"Missing sample files: {missing}"


def test_docs_pages_present():
    expected = [
        ROOT / "docs" / "ops" / "local_gates.md",
        ROOT / "docs" / "checklists" / "approval_gate_checklist.md",
        ROOT / "docs" / "samples" / "intent_validation_example.md",
        ROOT / "docs" / "templates" / "intent_validation_gate.md",
        ROOT / "docs" / "decision_records" / "ADR-intent-approval-gate.md",
        ROOT / "docs" / "decision_records" / "ADR-codex-evaluator-v3.md",
        ROOT / "docs" / "rubrics" / "codex_eval_rubric_v3.md",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    assert not missing, f"Missing docs pages: {missing}"
