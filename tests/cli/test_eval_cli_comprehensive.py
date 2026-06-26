"""Comprehensive tests for src/codex_ml/cli/evaluate.py module.

Tests cover:
- Metric function registry
- Sequence coercion
- Prompt sanitization
- Evaluation pipeline helpers
"""

import pytest


class TestMetricFunctions:
    """Tests for METRIC_FUNCS registry."""

    def test_metric_funcs_registry_exists(self):
        """Test that METRIC_FUNCS registry is defined."""
        from codex_ml.cli.evaluate import METRIC_FUNCS

        assert isinstance(METRIC_FUNCS, dict)

    def test_metric_funcs_contains_accuracy(self):
        """Test that accuracy metric is registered."""
        from codex_ml.cli.evaluate import METRIC_FUNCS

        assert "accuracy" in METRIC_FUNCS, "Condition must be true"
        assert callable(METRIC_FUNCS["accuracy"]), "Condition must be true"

    def test_metric_funcs_contains_token_accuracy(self):
        """Test that token_accuracy metric is registered."""
        from codex_ml.cli.evaluate import METRIC_FUNCS

        assert "token_accuracy" in METRIC_FUNCS, "Condition must be true"
        assert callable(METRIC_FUNCS["token_accuracy"]), "Condition must be true"

    def test_metric_funcs_contains_f1(self):
        """Test that f1 metric is registered."""
        from codex_ml.cli.evaluate import METRIC_FUNCS

        assert "f1" in METRIC_FUNCS, "Condition must be true"
        assert callable(METRIC_FUNCS["f1"]), "Condition must be true"

    def test_metric_funcs_contains_perplexity(self):
        """Test that perplexity metric is registered."""
        from codex_ml.cli.evaluate import METRIC_FUNCS

        assert "perplexity" in METRIC_FUNCS, "Condition must be true"
        assert callable(METRIC_FUNCS["perplexity"]), "Condition must be true"


class TestSequenceCoercion:
    """Tests for _coerce_sequence function."""

    def test_coerce_sequence_with_none(self):
        """Test _coerce_sequence returns None for None."""
        from codex_ml.cli.evaluate import _coerce_sequence

        assert _coerce_sequence(None) is None, "Condition must be true"

    def test_coerce_sequence_with_list(self):
        """Test _coerce_sequence preserves list."""
        from codex_ml.cli.evaluate import _coerce_sequence

        result = _coerce_sequence(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_coerce_sequence_with_tuple(self):
        """Test _coerce_sequence converts tuple to list."""
        from codex_ml.cli.evaluate import _coerce_sequence

        result = _coerce_sequence(("a", "b", "c"))
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)

    def test_coerce_sequence_with_set(self):
        """Test _coerce_sequence converts set to list."""
        from codex_ml.cli.evaluate import _coerce_sequence

        result = _coerce_sequence({"a", "b", "c"})
        assert isinstance(result, list)
        assert set(result) == {"a", "b", "c"}

    def test_coerce_sequence_with_string(self):
        """Test _coerce_sequence wraps string in list."""
        from codex_ml.cli.evaluate import _coerce_sequence

        result = _coerce_sequence("test_string")
        assert result == ["test_string"], "Result must not be empty"

    def test_coerce_sequence_with_integer(self):
        """Test _coerce_sequence returns None for integer."""
        from codex_ml.cli.evaluate import _coerce_sequence

        result = _coerce_sequence(42)
        assert result is None, "Result must not be empty"


class TestSanitizePromptList:
    """Tests for _sanitize_prompt_list function."""

    def test_sanitize_prompt_list_with_strings(self):
        """Test _sanitize_prompt_list with string list."""
        from codex_ml.cli.evaluate import _sanitize_prompt_list

        result, _changed = _sanitize_prompt_list(["prompt1", "prompt2"])
        assert isinstance(result, list)
        assert len(result) == 2, "Result must not be empty"

    def test_sanitize_prompt_list_empty(self):
        """Test _sanitize_prompt_list with empty list."""
        from codex_ml.cli.evaluate import _sanitize_prompt_list

        result, changed = _sanitize_prompt_list([])
        assert result == [], "Result must not be empty"
        assert changed is False, "changed is not valid"

    def test_sanitize_prompt_list_with_dicts(self):
        """Test _sanitize_prompt_list with dict entries."""
        from codex_ml.cli.evaluate import _sanitize_prompt_list

        items = [
            {"prompt": "test prompt", "expected": "output"},
            {"input": "test input", "label": "label"},
        ]
        result, _changed = _sanitize_prompt_list(items)
        assert isinstance(result, list)
        assert len(result) == 2, "Result must not be empty"

    def test_sanitize_prompt_list_mixed_types(self):
        """Test _sanitize_prompt_list with mixed types."""
        from codex_ml.cli.evaluate import _sanitize_prompt_list

        items = ["string_prompt", {"prompt": "dict_prompt"}, 123]
        result, _changed = _sanitize_prompt_list(items)
        assert isinstance(result, list)
        assert len(result) == 3, "Result must not be empty"


class TestEvaluateCLIIntegration:
    """Integration tests for evaluate CLI module."""

    def test_module_imports(self):
        """Test that module can be imported."""
        from codex_ml.cli import evaluate

        assert hasattr(evaluate, "METRIC_FUNCS")
        assert hasattr(evaluate, "_coerce_sequence")
        assert hasattr(evaluate, "_sanitize_prompt_list")

    def test_logger_configured(self):
        """Test that logger is properly configured."""
        from codex_ml.cli import evaluate

        assert hasattr(evaluate, "logger")

    def test_optional_imports_handled(self):
        """Test that optional imports are handled gracefully."""
        from codex_ml.cli import evaluate

        # Module should be importable regardless of optional deps
        assert hasattr(evaluate, "_HAS_TORCH")
        assert hasattr(evaluate, "_HAS_MLFLOW")
        assert hasattr(evaluate, "_HAS_HYDRA")

    def test_metric_imports(self):
        """Test that metric functions are imported correctly."""
        from codex_ml.cli.evaluate import (
            accuracy,
            classification_f1,
            perplexity,
            token_accuracy,
        )

        assert callable(accuracy), "Condition must be true"
        assert callable(classification_f1), "Condition must be true"
        assert callable(perplexity), "Condition must be true"
        assert callable(token_accuracy), "Condition must be true"


class TestMetricFunctionsBasic:
    """Basic tests for individual metric functions."""

    def test_accuracy_function_callable(self):
        """Test accuracy function is callable."""
        from codex_ml.cli.evaluate import accuracy

        assert callable(accuracy), "Condition must be true"

    def test_token_accuracy_function_callable(self):
        """Test token_accuracy function is callable."""
        from codex_ml.cli.evaluate import token_accuracy

        assert callable(token_accuracy), "Condition must be true"

    def test_classification_f1_function_callable(self):
        """Test classification_f1 function is callable."""
        from codex_ml.cli.evaluate import classification_f1

        assert callable(classification_f1), "Condition must be true"

    def test_perplexity_function_callable(self):
        """Test perplexity function is callable."""
        from codex_ml.cli.evaluate import perplexity

        assert callable(perplexity), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
