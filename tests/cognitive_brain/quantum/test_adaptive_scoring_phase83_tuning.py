from __future__ import annotations

import json

from cognitive_brain.quantum.adaptive_scoring import AdaptiveScoringOptimizer


def test_tune_k1_from_pda_history(tmp_path):
    pda = tmp_path / "pda_iterations.jsonl"
    rows = [
        {"status": "complete", "ci_checks_green": 6, "ci_checks_red": 1},
        {"status": "resolved", "ci_checks_green": 4, "ci_checks_red": 0},
        {"status": "failed", "ci_checks_green": 0, "ci_checks_red": 3},
    ]
    pda.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    optimizer = AdaptiveScoringOptimizer()
    tuned = optimizer.tune_k1_from_pda_history(pda)

    assert 0.20 <= tuned <= 0.45
    assert optimizer.get_current_k1() == tuned


def test_tune_k1_from_pda_history_ignores_invalid_lines(tmp_path):
    pda = tmp_path / "pda_iterations.jsonl"
    pda.write_text('{"status":"complete"}\nnot-json\n{"status":"implemented"}', encoding="utf-8")

    optimizer = AdaptiveScoringOptimizer()
    tuned = optimizer.tune_k1_from_pda_history(pda)
    assert tuned < 0.40


def test_extract_success_signal_ignores_boolean_ci_counts():
    optimizer = AdaptiveScoringOptimizer()

    assert (
        optimizer._extract_success_signal({"ci_checks_green": True, "ci_checks_red": False}) is None
    )
    assert optimizer._extract_success_signal({"ci_checks_green": 3, "ci_checks_red": False}) is None
    assert optimizer._extract_success_signal({"ci_checks_green": True, "ci_checks_red": 1}) is None
