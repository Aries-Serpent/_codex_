from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

pytest.importorskip("omegaconf")

from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import EvaluationError, run_evaluation


def _write_dataset(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    path = tmp_path / "dataset.jsonl"
    lines = [json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def test_run_evaluation_generates_reports(tmp_path: Path) -> None:
    records = [
        {
            "prediction": "cat sat",
            "target": "cat sat",
            "text": "cat sat",
            "target_tokens": [0, 1],
            "prediction_tokens": [0, 1],
            "nll": [0.0, math.log(4.0)],
        },
        {
            "prediction": "dog ran",
            "target": "cat sat",
            "text": "dog ran",
            "target_tokens": [1, 1],
            "prediction_tokens": [0, 1],
            "nll": [math.log(4.0), math.log(4.0)],
        },
    ]
    dataset = _write_dataset(tmp_path, records)
    output_dir = tmp_path / "reports"
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        prediction_field="prediction",
        target_field="target",
        text_field="text",
        metrics=["accuracy", "micro_f1", "perplexity"],
        output_dir=str(output_dir),
        report_filename="summary.json",
        ndjson_filename="records.ndjson",
    )
    result = run_evaluation(cfg)
    summary_path = Path(result["summary_path"])
    ndjson_path = Path(result["records_path"])
    manifest_path = Path(result["manifest_path"])
    assert summary_path.exists()
    assert ndjson_path.exists()
    assert manifest_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["num_records"] == 2
    assert summary["metrics"]["accuracy"] == pytest.approx(0.5)
    assert summary["metrics"]["micro_f1"] == pytest.approx(0.5)
    expected_ppl = math.exp((0.0 + math.log(4.0) * 3) / 4)
    assert summary["metrics"]["perplexity"] == pytest.approx(expected_ppl)


def test_run_evaluation_missing_tokens_errors(tmp_path: Path) -> None:
    dataset = _write_dataset(
        tmp_path,
        [
            {"prediction": "a", "target": "a", "text": "a"},
        ],
    )
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["perplexity"],
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(EvaluationError):
        run_evaluation(cfg)


def test_run_evaluation_mixed_perplexity_inputs_errors(tmp_path: Path) -> None:
    dataset = _write_dataset(
        tmp_path,
        [
            {
                "prediction": "a",
                "target": "a",
                "text": "a",
                "target_tokens": [0, 1],
                "nll": [0.0, 0.1],
            },
            {
                "prediction": "b",
                "target": "b",
                "text": "b",
                "target_tokens": [0, 1],
                "logits": [[-1.0, -2.0], [-1.5, -0.5]],
            },
        ],
    )
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["perplexity"],
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(EvaluationError):
        run_evaluation(cfg)


def test_run_evaluation_token_accuracy_mismatched_tokens(tmp_path: Path) -> None:
    dataset = _write_dataset(
        tmp_path,
        [
            {
                "prediction": "a",
                "target": "a",
                "text": "a",
                "prediction_tokens": [0, 1],
                "target_tokens": [0],
            }
        ],
    )
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        prediction_field="prediction",
        target_field="target",
        text_field="text",
        metrics=["token_accuracy"],
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(EvaluationError):
        run_evaluation(cfg)


def test_run_evaluation_shared_label_mapping(tmp_path: Path) -> None:
    dataset = _write_dataset(
        tmp_path,
        [
            {"prediction": "cat", "target": "dog", "text": "a"},
            {"prediction": "dog", "target": "cat", "text": "b"},
        ],
    )
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        prediction_field="prediction",
        target_field="target",
        text_field="text",
        metrics=["micro_f1", "macro_f1"],
        output_dir=str(tmp_path / "out"),
    )
    result = run_evaluation(cfg)
    summary = json.loads(Path(result["summary_path"]).read_text(encoding="utf-8"))
    assert summary["metrics"]["micro_f1"] == pytest.approx(0.0)
    assert summary["metrics"]["macro_f1"] == pytest.approx(0.0)
