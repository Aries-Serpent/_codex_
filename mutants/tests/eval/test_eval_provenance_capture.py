#!/usr/bin/env python3
"""Test Eval Provenance Capture

Test that evaluation runner captures complete provenance including git commit and seed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import run_evaluation


@pytest.fixture
def sample_eval_dataset(tmp_path: Path) -> Path:
    """Create a minimal evaluation dataset."""
    dataset = tmp_path / "eval_data.jsonl"
    records = [
        {"prediction": "hello", "target": "hello", "text": "test1"},
        {"prediction": "world", "target": "world", "text": "test2"},
    ]
    dataset.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return dataset


def test_evaluation_captures_git_commit_in_provenance(
    sample_eval_dataset: Path, tmp_path: Path, monkeypatch
) -> None:
    """Verify that evaluation exports environment with git commit hash."""
    # Mock git to return a known commit
    fake_commit = "abc123def456"

    def _fake_git_commit():
        return fake_commit

    import codex_ml.utils.provenance as prov_module

    monkeypatch.setattr(prov_module, "_git_commit", _fake_git_commit)

    output_dir = tmp_path / "eval_output"
    cfg = EvaluationConfig(
        dataset_path=str(sample_eval_dataset),
        dataset_format="jsonl",
        metrics=["exact_match"],
        output_dir=str(output_dir),
        seed=42,
        prediction_field="prediction",
        target_field="target",
        text_field="text",
    )

    run_evaluation(cfg)

    # Check that provenance was exported
    provenance_dir = output_dir / "provenance"
    assert provenance_dir.exists(), "Condition must be true"

    env_json = provenance_dir / "environment.json"
    assert env_json.exists(), "Condition must be true"

    env_data = json.loads(env_json.read_text())
    assert env_data["git_commit"] == fake_commit, "Data must not be empty"

    # Check concise NDJSON summary
    env_ndjson = provenance_dir / "environment.ndjson"
    assert env_ndjson.exists(), "Condition must be true"

    ndjson_data = json.loads(env_ndjson.read_text().strip())
    assert ndjson_data["git_commit"] == fake_commit, "Data must not be empty"
    assert ndjson_data["seed"] == 42, "Data must not be empty"
    assert ndjson_data["command"] == "evaluate", "Data must not be empty"
    assert "dataset_path" in ndjson_data, "Data must not be empty"


def test_evaluation_seed_is_deterministic(sample_eval_dataset: Path, tmp_path: Path) -> None:
    """Verify that evaluation with same seed produces identical results."""
    cfg = EvaluationConfig(
        dataset_path=str(sample_eval_dataset),
        dataset_format="jsonl",
        metrics=["exact_match", "f1"],
        output_dir=str(tmp_path / "run1"),
        seed=999,
        prediction_field="prediction",
        target_field="target",
        text_field="text",
    )

    result1 = run_evaluation(cfg)

    # Run again with same seed
    cfg.output_dir = str(tmp_path / "run2")
    result2 = run_evaluation(cfg)

    # Results should be identical
    assert result1["metrics"] == result2["metrics"], "Result must not be empty"
    assert result1["num_records"] == result2["num_records"], "Result must not be empty"
