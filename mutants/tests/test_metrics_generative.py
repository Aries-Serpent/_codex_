from __future__ import annotations

"""
Test Metrics Generative

Test module for metrics generative.
"""

#!/usr/bin/env python3
"""Tests for optional generative metrics (BLEU, ROUGE-L) behavior."""

import json
from pathlib import Path

from codex_ml.config import EvaluationConfig
from codex_ml.eval.runner import run_evaluation
from codex_ml.metrics.registry import get_metric, list_metrics


def test_bleu_optional_behavior():
    """BLEU metric returns None or numeric value in [0, 1]."""
    metric = get_metric("bleu")

    # Test with simple inputs
    result = metric(preds=["hello world"], targets=["hello world"])

    # Should return None (if nltk not installed) or float in [0, 1]
    assert result is None or (isinstance(result, (int, float)) and 0 <= result <= 1)

    # Test with mismatch
    result2 = metric(preds=["foo"], targets=["bar"])
    assert result2 is None or (isinstance(result2, (int, float)) and 0 <= result2 <= 1)


def test_rouge_l_optional_behavior():
    """ROUGE-L metric returns None or numeric value in [0, 1]."""
    metric = get_metric("rougeL")

    # Test with simple inputs
    result = metric(preds=["the quick brown fox"], targets=["the quick brown fox"])

    # Should return None (if rouge_score not installed) or float in [0, 1]
    assert result is None or (isinstance(result, (int, float)) and 0 <= result <= 1)

    # Test with partial match
    result2 = metric(preds=["the quick fox"], targets=["the quick brown fox"])
    assert result2 is None or (isinstance(result2, (int, float)) and 0 <= result2 <= 1)


def test_registry_lists_generative_names():
    """Registry includes bleu and rougeL metrics."""
    available = list_metrics()

    # Check that generative metrics are registered
    assert "bleu" in available, "Condition must be true"
    # Note: Registry key is lowercase "rougel" but decorator is "rougeL"
    assert "rougel" in [m.lower() for m in available], "Condition must be true"


def test_runner_no_generative_dependency_required(tmp_path: Path):
    """Evaluation can run without generative extras when not requested."""
    # Create a minimal dataset
    dataset = tmp_path / "test.jsonl"
    records = [
        {"prediction": "hello", "target": "hello", "text": "test1"},
        {"prediction": "world", "target": "world", "text": "test2"},
    ]
    dataset.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    output_dir = tmp_path / "output"
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["exact_match", "f1"],  # No generative metrics
        output_dir=str(output_dir),
        seed=42,
        prediction_field="prediction",
        target_field="target",
        text_field="text",
    )

    # Should succeed without generative dependencies
    result = run_evaluation(cfg)
    assert "metrics" in result, "Result must not be empty"
    assert "exact_match" in result["metrics"], "Result must not be empty"
    assert "f1" in result["metrics"], "Result must not be empty"


def test_bleu_metric_with_identical_inputs():
    """BLEU should return 1.0 or None for identical inputs."""
    metric = get_metric("bleu")

    preds = ["the cat sat on the mat"]
    targets = ["the cat sat on the mat"]

    result = metric(preds, targets)

    # Should be None (deps missing) or 1.0 (perfect match)
    if result is not None:
        assert isinstance(result, (int, float))
        assert result >= 0.99, "result must be greater than zero"


def test_rouge_metric_with_identical_inputs():
    """ROUGE-L should return 1.0 or None for identical inputs."""
    metric = get_metric("rougeL")

    preds = ["the quick brown fox jumps over the lazy dog"]
    targets = ["the quick brown fox jumps over the lazy dog"]

    result = metric(preds, targets)

    # Should be None (deps missing) or close to 1.0 (perfect match)
    if result is not None:
        assert isinstance(result, (int, float))
        assert result >= 0.99, "result must be greater than zero"


def test_runner_handles_rouge_float_return(tmp_path: Path, monkeypatch):
    """Verify runner correctly handles ROUGE returning a float."""
    # Create a minimal dataset
    dataset = tmp_path / "test.jsonl"
    records = [
        {"prediction": "hello world", "target": "hello world", "text": "test"},
    ]
    dataset.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    # Mock rouge_l to return a float directly
    def mock_rouge_l(preds, targets):
        return 0.95  # Return float directly

    # Register mock metric in registry instead of patching module
    from codex_ml.metrics import registry

    monkeypatch.setitem(registry._METRIC_REGISTRY, "rouge_l", mock_rouge_l)

    output_dir = tmp_path / "output"
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["rouge_l"],
        output_dir=str(output_dir),
        seed=42,
        prediction_field="prediction",
        target_field="target",
        text_field="text",
    )

    result = run_evaluation(cfg)
    assert result["metrics"]["rouge_l"] == 0.95, "Result must not be empty"


def test_runner_handles_rouge_dict_return(tmp_path: Path, monkeypatch):
    """Verify runner correctly handles ROUGE returning a dict."""
    # Create a minimal dataset
    dataset = tmp_path / "test.jsonl"
    records = [
        {"prediction": "hello world", "target": "hello world", "text": "test"},
    ]
    dataset.write_text("\n".join(json.dumps(r) for r in records) + "\n")

    # Mock rouge_l to return a dict with rougeL_f key
    def mock_rouge_l(preds, targets):
        return {"rougeL_f": 0.88, "rougeL": 0.88}

    import codex_ml.eval.metrics as metrics_module

    monkeypatch.setattr(metrics_module, "rouge_l", mock_rouge_l)

    output_dir = tmp_path / "output"
    cfg = EvaluationConfig(
        dataset_path=str(dataset),
        dataset_format="jsonl",
        metrics=["rouge_l"],
        output_dir=str(output_dir),
        seed=42,
        prediction_field="prediction",
        target_field="target",
        text_field="text",
    )

    result = run_evaluation(cfg)
    assert result["metrics"]["rouge_l"] == 0.88, "Result must not be empty"
