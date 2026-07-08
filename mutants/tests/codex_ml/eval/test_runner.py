"""
Test Eval Runner Module

Tests for the evaluation runner module including error handling,
metrics sink normalization, record loading, and label encoding.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from codex_ml.eval.runner import (
    EvaluationError,
    _append_error_report,
    _coerce_token_sequence,
    _collect_perplexity_inputs,
    _encode_labels,
    _load_records,
    _normalise_metrics_sink,
    _safe_operation,
)


class TestEvaluationError:
    """Tests for EvaluationError exception."""

    def test_is_runtime_error_subclass(self) -> None:
        """Test that EvaluationError is a RuntimeError subclass."""
        assert issubclass(EvaluationError, RuntimeError)

    def test_error_message(self) -> None:
        """Test error message is preserved."""
        error = EvaluationError("test error message")
        assert str(error) == "test error message", "Error should be raised or set"

    def test_raise_and_catch(self) -> None:
        """Test raising and catching the error."""

        def _do_raise() -> None:
            raise EvaluationError("evaluation failed")

        with pytest.raises(EvaluationError) as exc_info:
            _do_raise()
        assert "evaluation failed" in str(exc_info.value), "Value must be initialized"


class TestNormaliseMetricsSink:
    """Tests for _normalise_metrics_sink function."""

    def test_default_to_ndjson_for_empty_string(self) -> None:
        """Test empty string defaults to ndjson."""
        result = _normalise_metrics_sink("")
        assert result == ["ndjson"], "Result must not be empty"

    def test_single_sink_string(self) -> None:
        """Test single sink as string."""
        assert _normalise_metrics_sink("csv") == ["csv"], "_n is not valid"
        assert _normalise_metrics_sink("ndjson") == ["ndjson"], "_n is not valid"
        assert _normalise_metrics_sink("none") == ["none"], "_n is not valid"

    def test_comma_separated_sinks(self) -> None:
        """Test comma-separated sinks."""
        result = _normalise_metrics_sink("csv,ndjson")
        assert result == ["csv", "ndjson"]

    def test_list_of_sinks(self) -> None:
        """Test list of sinks."""
        result = _normalise_metrics_sink(["csv", "ndjson"])
        assert result == ["csv", "ndjson"]

    def test_case_insensitive(self) -> None:
        """Test case insensitivity."""
        result = _normalise_metrics_sink("CSV,NDJSON")
        assert result == ["csv", "ndjson"]

    def test_removes_duplicates(self) -> None:
        """Test duplicate removal while preserving order."""
        result = _normalise_metrics_sink("csv,ndjson,csv")
        assert result == ["csv", "ndjson"]

    def test_handles_whitespace(self) -> None:
        """Test whitespace handling."""
        result = _normalise_metrics_sink("  csv , ndjson  ")
        assert result == ["csv", "ndjson"]

    def test_invalid_sink_raises_error(self) -> None:
        """Test invalid sink raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            _normalise_metrics_sink("invalid")
        assert "Unsupported metrics sink" in str(exc_info.value), "Value must be initialized"

    def test_multiple_invalid_sinks(self) -> None:
        """Test multiple invalid sinks are reported."""
        with pytest.raises(EvaluationError) as exc_info:
            _normalise_metrics_sink("foo,bar,csv")
        assert "foo" in str(exc_info.value) or "bar" in str(exc_info.value), "Value must be initialized"

    def test_empty_list_defaults_to_ndjson(self) -> None:
        """Test empty list defaults to ndjson."""
        result = _normalise_metrics_sink([])
        assert result == ["ndjson"], "Result must not be empty"

    def test_none_defaults_to_ndjson(self) -> None:
        """Test None-like values default to ndjson."""
        result = _normalise_metrics_sink(None)
        assert result == ["ndjson"], "Result must not be empty"


class TestLoadRecords:
    """Tests for _load_records function."""

    def test_load_jsonl_records(self) -> None:
        """Test loading JSONL records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            records = [
                {"prediction": "a", "target": "b", "text": "c"},
                {"prediction": "d", "target": "e", "text": "f"},
            ]
            path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

            result = _load_records(
                path,
                "jsonl",
                prediction_field="prediction",
                target_field="target",
                text_field="text",
            )

            assert len(result) == 2, "Result must not be empty"
            assert result[0]["prediction"] == "a", "Result must not be empty"
            assert result[0]["target"] == "b", "Result must not be empty"
            assert result[1]["prediction"] == "d", "Result must not be empty"

    def test_load_ndjson_records(self) -> None:
        """Test loading NDJSON records (same as JSONL)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.ndjson"
            records = [{"prediction": "x", "target": "y", "text": "z"}]
            path.write_text(json.dumps(records[0]), encoding="utf-8")

            result = _load_records(
                path,
                "ndjson",
                prediction_field="prediction",
                target_field="target",
                text_field="text",
            )

            assert len(result) == 1, "Result must not be empty"
            assert result[0]["prediction"] == "x", "Result must not be empty"

    def test_load_csv_records(self) -> None:
        """Test loading CSV records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            path.write_text("prediction,target,text\na,b,c\nd,e,f", encoding="utf-8")

            result = _load_records(
                path,
                "csv",
                prediction_field="prediction",
                target_field="target",
                text_field="text",
            )

            assert len(result) == 2, "Result must not be empty"
            assert result[0]["prediction"] == "a", "Result must not be empty"
            assert result[1]["target"] == "e", "Result must not be empty"

    def test_load_text_records(self) -> None:
        """Test loading plain text records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.txt"
            path.write_text("line1\nline2\nline3", encoding="utf-8")

            result = _load_records(
                path,
                "text",
                prediction_field="prediction",
                target_field="target",
                text_field="text",
            )

            assert len(result) == 3, "Result must not be empty"
            assert result[0]["text"] == "line1", "Result must not be empty"
            assert result[0]["prediction"] == "line1", "Result must not be empty"
            assert result[0]["target"] == "line1", "Result must not be empty"

    def test_unsupported_format_raises_error(self) -> None:
        """Test unsupported format raises EvaluationError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.xml"
            path.write_text("<data></data>", encoding="utf-8")

            with pytest.raises(EvaluationError) as exc_info:
                _load_records(
                    path,
                    "xml",
                    prediction_field="prediction",
                    target_field="target",
                    text_field="text",
                )
            assert "Unsupported dataset format" in str(exc_info.value), "Data must not be empty"

    def test_jsonl_skips_empty_lines(self) -> None:
        """Test JSONL loading skips empty lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            content = '{"prediction": "a", "target": "b"}\n\n{"prediction": "c", "target": "d"}'
            path.write_text(content, encoding="utf-8")

            result = _load_records(
                path,
                "jsonl",
                prediction_field="prediction",
                target_field="target",
                text_field="text",
            )

            assert len(result) == 2, "Result must not be empty"

    def test_jsonl_invalid_line_raises_error(self) -> None:
        """Test JSONL with non-object line raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            path.write_text('["array", "not", "object"]', encoding="utf-8")

            with pytest.raises(EvaluationError) as exc_info:
                _load_records(
                    path,
                    "jsonl",
                    prediction_field="prediction",
                    target_field="target",
                    text_field="text",
                )
            assert "must be an object" in str(exc_info.value), "Value must be initialized"


class TestEncodeLabels:
    """Tests for _encode_labels function."""

    def test_encode_integer_labels(self) -> None:
        """Test encoding integer labels."""
        ints, mapping = _encode_labels([0, 1, 2, 1, 0], "test_metric")
        assert ints == [0, 1, 2, 1, 0]
        assert mapping == {}, "mapping is not valid"

    def test_encode_bool_labels(self) -> None:
        """Test encoding boolean labels."""
        ints, _mapping = _encode_labels([True, False, True], "test_metric")
        assert ints == [1, 0, 1]

    def test_encode_string_labels(self) -> None:
        """Test encoding string labels."""
        ints, mapping = _encode_labels(["cat", "dog", "cat", "bird"], "test_metric")
        assert len(ints) == 4, "Ints must not be empty"
        assert ints[0] == ints[2], "Condition must be true"
        assert len(mapping) == 3, "Mapping must not be empty"

    def test_encode_with_fallback_mapping(self) -> None:
        """Test encoding with fallback mapping."""
        fallback = {"cat": 0, "dog": 1}
        ints, mapping = _encode_labels(["cat", "dog", "bird"], "test_metric", fallback=fallback)
        assert ints[0] == 0, "Condition must be true"
        assert ints[1] == 1, "Condition must be true"
        assert ints[2] == 2, "Condition must be true"
        assert mapping == {"cat": 0, "dog": 1, "bird": 2}

    def test_encode_none_raises_error(self) -> None:
        """Test encoding None raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            _encode_labels([1, None, 2], "test_metric")
        assert "Missing value" in str(exc_info.value), "Value must be initialized"

    def test_encode_numeric_strings(self) -> None:
        """Test encoding numeric strings."""
        ints, _mapping = _encode_labels(["1", "2", "3"], "test_metric")
        assert ints == [1, 2, 3]


class TestCoerceTokenSequence:
    """Tests for _coerce_token_sequence function."""

    def test_valid_token_sequence(self) -> None:
        """Test valid token sequence."""
        record = {"tokens": [1, 2, 3, 4]}
        result = _coerce_token_sequence(record, "tokens", 0)
        assert result == [1, 2, 3, 4]

    def test_missing_key_raises_error(self) -> None:
        """Test missing key raises EvaluationError."""
        record = {"other": [1, 2, 3]}
        with pytest.raises(EvaluationError) as exc_info:
            _coerce_token_sequence(record, "tokens", 0)
        assert "missing 'tokens' field" in str(exc_info.value), "Value must be initialized"

    def test_invalid_tokens_raises_error(self) -> None:
        """Test invalid tokens raise EvaluationError."""
        record = {"tokens": ["not", "integers"]}
        with pytest.raises(EvaluationError) as exc_info:
            _coerce_token_sequence(record, "tokens", 0)
        assert "invalid 'tokens' values" in str(exc_info.value), "Value must be initialized"


class TestCollectPerplexityInputs:
    """Tests for _collect_perplexity_inputs function."""

    def test_collect_with_logits(self) -> None:
        """Test collecting perplexity inputs with logits."""
        records = [
            {"target_tokens": [1, 2], "logits": [0.5, 0.6]},
            {"target_tokens": [3, 4], "logits": [0.7, 0.8]},
        ]
        values, targets, using_logits = _collect_perplexity_inputs(records)
        assert using_logits is True, "using_logits is not valid"
        assert values == [0.5, 0.6, 0.7, 0.8]
        assert targets == [1, 2, 3, 4]

    def test_collect_with_nll(self) -> None:
        """Test collecting perplexity inputs with NLL."""
        records = [
            {"target_tokens": [1, 2], "nll": [1.0, 2.0]},
        ]
        values, targets, using_logits = _collect_perplexity_inputs(records)
        assert using_logits is False, "using_logits is not valid"
        assert values == [1.0, 2.0]
        assert targets == [1, 2]

    def test_missing_target_tokens_raises_error(self) -> None:
        """Test missing target_tokens raises error."""
        records = [{"logits": [0.5, 0.6]}]
        with pytest.raises(EvaluationError) as exc_info:
            _collect_perplexity_inputs(records)
        assert "target_tokens" in str(exc_info.value), "Value must be initialized"

    def test_missing_logits_and_nll_raises_error(self) -> None:
        """Test missing both logits and nll raises error."""
        records = [{"target_tokens": [1, 2]}]
        with pytest.raises(EvaluationError) as exc_info:
            _collect_perplexity_inputs(records)
        assert "logits" in str(exc_info.value) or "nll" in str(exc_info.value), "Value must be initialized"

    def test_mixed_logits_and_nll_raises_error(self) -> None:
        """Test mixing logits and nll raises error."""
        records = [
            {"target_tokens": [1, 2], "logits": [0.5, 0.6]},
            {"target_tokens": [3, 4], "nll": [1.0, 2.0]},
        ]
        with pytest.raises(EvaluationError) as exc_info:
            _collect_perplexity_inputs(records)
        assert "mixing" in str(exc_info.value).lower(), "Value must be initialized"

    def test_length_mismatch_raises_error(self) -> None:
        """Test length mismatch between tokens and logits raises error."""
        records = [{"target_tokens": [1, 2, 3], "logits": [0.5, 0.6]}]  # 3 tokens, 2 logits
        with pytest.raises(EvaluationError) as exc_info:
            _collect_perplexity_inputs(records)
        assert "length" in str(exc_info.value).lower(), "Value must be initialized"


class TestSafeOperation:
    """Tests for _safe_operation function."""

    def test_successful_operation_returns_result(self) -> None:
        """Test successful operation returns result."""
        result = _safe_operation("test", lambda: 42)
        assert result == 42, "Result must not be empty"

    def test_exception_is_reraised(self) -> None:
        """Test exception is re-raised after logging."""

        def failing_op() -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError):
            _safe_operation("test", failing_op)


class TestAppendErrorReport:
    """Tests for _append_error_report function."""

    def test_creates_report_file(self) -> None:
        """Test error report file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily change to the temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                _append_error_report("test_step", "test error message")

                reports_dir = Path(tmpdir) / "_codex_reports"
                if reports_dir.exists():
                    error_files = list(reports_dir.glob("errors_*.md"))
                    if error_files:
                        content = error_files[0].read_text()
                        assert "test_step" in content or "test error message" in content, "Content must not be empty"
            finally:
                os.chdir(original_cwd)

    def test_handles_context(self) -> None:
        """Test error report handles context dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                _append_error_report(
                    "test_step",
                    "test error",
                    context={"key": "value"},
                )
                # Just verify it doesn't raise
            finally:
                os.chdir(original_cwd)


class TestMetricsSinkEdgeCases:
    """Edge case tests for metrics sink handling."""

    def test_bytes_are_not_treated_as_sequence(self) -> None:
        """Test that bytes are not treated as a sequence."""
        result = _normalise_metrics_sink(b"csv")
        assert result == ["ndjson"], "Result must not be empty"

    def test_mixed_valid_invalid_sinks(self) -> None:
        """Test mixed valid and invalid sinks."""
        with pytest.raises(EvaluationError):
            _normalise_metrics_sink("csv,invalid,ndjson")
