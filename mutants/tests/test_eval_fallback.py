"""
Test Eval Fallback

Test module for eval fallback.
"""

from __future__ import annotations

import importlib

import pytest


def test_lite_sequence_evaluation_matches_shapes():
    module = importlib.import_module("codex_ml.eval.evaluator")
    result = module.lite_sequence_evaluation(
        [
            "hello world",
            "foo bar",
        ],
        [
            "hello there",
            "foo bar",
        ],
    )
    assert set(result) >= {"token_accuracy", "perplexity_proxy", "exact_match", "samples"}
    assert result["samples"] == pytest.approx(2.0), "Result must not be empty"


def test_evaluate_model_dependency_error(monkeypatch):
    module = importlib.import_module("codex_ml.eval.evaluator")
    monkeypatch.setattr(module, "_HAS_TORCH", False, raising=False)
    monkeypatch.setattr(module, "_HAS_DATASETS", False, raising=False)
    with pytest.raises(module.EvaluationDependencyError) as exc:
        module.evaluate_model(object(), object(), ["hello"])
    assert "torch" in exc.value.missing, "Value must be initialized"
