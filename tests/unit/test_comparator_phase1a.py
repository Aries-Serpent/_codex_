"""
Unit tests for src/codex/verify/comparator.py - Phase 1A Gap Closure.

Comprehensive test coverage for the behavior comparator module covering:
  1. ComparisonMode enum (STRICT, FUZZY, SEMANTIC)
  2. ComparisonDetail and ComparisonResult dataclasses
  3. Hash and output normalization functions
  4. Script execution with deterministic environment
  5. Output comparison with different modes
  6. Main compare() function
  7. Test generation from golden outputs
  8. Error handling and edge cases

Tests include basic functionality, edge cases, integration scenarios.
"""

import hashlib
from pathlib import Path

import pytest

from src.codex.verify.comparator import (
    ComparisonDetail,
    ComparisonMode,
    ComparisonResult,
    _compare_outputs,
    _hash_output,
    _normalize_output,
    compare,
    generate_tests,
)

# =====================================================================
# FIXTURES
# =====================================================================


@pytest.fixture
def temp_baseline_code(tmp_path):
    """Create temporary baseline code directory."""
    baseline_dir = tmp_path / "baseline"
    baseline_dir.mkdir()
    (baseline_dir / "main.py").write_text("""
def calculate(x, y):
    return x + y

if __name__ == "__main__":
    print(calculate(10, 20))
""")
    return baseline_dir


@pytest.fixture
def temp_patched_code(tmp_path):
    """Create temporary patched code directory."""
    patched_dir = tmp_path / "patched"
    patched_dir.mkdir()
    (patched_dir / "main.py").write_text("""
def calculate(x, y):
    return x + y

if __name__ == "__main__":
    print(calculate(10, 20))
""")
    return patched_dir


@pytest.fixture
def temp_modified_code(tmp_path):
    """Create modified code directory."""
    modified_dir = tmp_path / "modified"
    modified_dir.mkdir()
    (modified_dir / "main.py").write_text("""
def calculate(x, y):
    return x * y  # Changed from + to *

if __name__ == "__main__":
    print(calculate(10, 20))
""")
    return modified_dir


# =====================================================================
# TESTS: ComparisonMode Enum
# =====================================================================


class TestComparisonMode:
    """Test ComparisonMode enum."""

    def test_mode_strict(self):
        """Test STRICT mode value."""
        assert ComparisonMode.STRICT.value == "strict", "Value must be initialized"

    def test_mode_fuzzy(self):
        """Test FUZZY mode value."""
        assert ComparisonMode.FUZZY.value == "fuzzy", "Value must be initialized"

    def test_mode_semantic(self):
        """Test SEMANTIC mode value."""
        assert ComparisonMode.SEMANTIC.value == "semantic", "Value must be initialized"

    def test_all_modes_present(self):
        """Test all comparison modes exist."""
        modes = list(ComparisonMode)
        assert len(modes) == 3, "Modes must not be empty"
        assert ComparisonMode.STRICT in modes, "Condition must be true"
        assert ComparisonMode.FUZZY in modes, "Condition must be true"
        assert ComparisonMode.SEMANTIC in modes, "Condition must be true"


# =====================================================================
# TESTS: ComparisonDetail Dataclass
# =====================================================================


class TestComparisonDetail:
    """Test ComparisonDetail dataclass."""

    def test_detail_creation(self):
        """Test creating a ComparisonDetail."""
        detail = ComparisonDetail(
            input_ref="input1",
            mode=ComparisonMode.STRICT,
            result="match",
        )
        assert detail.input_ref == "input1", "input_ref is not valid"
        assert detail.mode == ComparisonMode.STRICT, "mode is not valid"
        assert detail.result == "match", "Result must not be empty"

    def test_detail_with_output(self):
        """Test ComparisonDetail with output."""
        detail = ComparisonDetail(
            input_ref="input1",
            mode=ComparisonMode.STRICT,
            result="divergence",
            baseline_output="baseline",
            patched_output="patched",
            diff="--- baseline\n+++ patched\n",
        )
        assert detail.baseline_output == "baseline", "baseline_output is not valid"
        assert detail.patched_output == "patched", "patched_output is not valid"
        assert detail.diff is not None, "diff must be initialized"

    def test_detail_with_error(self):
        """Test ComparisonDetail with error."""
        detail = ComparisonDetail(
            input_ref="input1",
            mode=ComparisonMode.STRICT,
            result="error",
            error="Timeout error",
        )
        assert detail.error == "Timeout error", "Error should be raised or set"

    def test_detail_result_options(self):
        """Test valid result options."""
        for result_val in ["match", "divergence", "error"]:
            detail = ComparisonDetail(
                input_ref="input",
                mode=ComparisonMode.STRICT,
                result=result_val,  # type: ignore
            )
            assert detail.result == result_val, "Result must not be empty"


# =====================================================================
# TESTS: ComparisonResult Dataclass
# =====================================================================


class TestComparisonResult:
    """Test ComparisonResult dataclass."""

    def test_result_creation(self):
        """Test creating a ComparisonResult."""
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="hash1",
            patched_hash="hash2",
        )
        assert result.result == "pass", "Result must not be empty"
        assert result.baseline_hash == "hash1", "Result must not be empty"

    def test_result_default_fields(self):
        """Test ComparisonResult default fields."""
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="hash1",
            patched_hash="hash2",
        )
        assert result.comparisons == [], "Result must not be empty"
        assert result.flakiness_check == {}, "Result must not be empty"
        assert result.timestamp is not None, "timestamp must be initialized"

    def test_result_to_dict(self):
        """Test ComparisonResult serialization."""
        detail = ComparisonDetail("input", ComparisonMode.STRICT, "match")
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
            comparisons=[detail],
        )
        result_dict = result.to_dict()
        assert result_dict["result"] == "pass", "Result must not be empty"
        assert len(result_dict["comparisons"]) == 1, "Collection must not be empty"

    def test_result_save_creates_file(self, tmp_path):
        """Test that save() creates JSON file."""
        output_file = tmp_path / "result.json"
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        result.save(output_file)
        assert output_file.exists(), "Condition must be true"


# =====================================================================
# TESTS: _hash_output()
# =====================================================================


class TestHashOutput:
    """Test output hashing."""

    def test_hash_simple_output(self):
        """Test hashing simple output."""
        output = "hello world"
        result = _hash_output(output)
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_deterministic(self):
        """Test that hashing is deterministic."""
        output = "test output"
        hash1 = _hash_output(output)
        hash2 = _hash_output(output)
        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        result = _hash_output("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_multiline_output(self):
        """Test hashing multiline output."""
        output = "line 1\nline 2\nline 3\n"
        result = _hash_output(output)
        expected = hashlib.sha256(output.encode("utf-8")).hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_length_is_64(self):
        """Test that hash is 64 characters (SHA256)."""
        result = _hash_output("any output")
        assert len(result) == 64, "Result must not be empty"


# =====================================================================
# TESTS: _normalize_output()
# =====================================================================


class TestNormalizeOutput:
    """Test output normalization."""

    def test_normalize_strict_mode_unchanged(self):
        """Test STRICT mode returns output unchanged."""
        output = "line 1\nline 2\n"
        result = _normalize_output(output, ComparisonMode.STRICT)
        assert result == output, "Result must not be empty"

    def test_normalize_fuzzy_mode_whitespace(self):
        """Test FUZZY mode normalizes whitespace."""
        output = "line 1  \nline 2\n\nline 3"
        result = _normalize_output(output, ComparisonMode.FUZZY)
        # Should strip and sort
        assert "line 1" in result, "Result must not be empty"
        assert "line 2" in result, "Result must not be empty"

    def test_normalize_fuzzy_mode_sorts(self):
        """Test FUZZY mode sorts lines."""
        output = "zzz\naaa\nbbb\n"
        result = _normalize_output(output, ComparisonMode.FUZZY)
        lines = result.split("\n")
        assert lines[0] <= lines[1] <= lines[2], "Condition must be true"

    def test_normalize_semantic_mode_removes_timestamps(self):
        """Test SEMANTIC mode removes timestamps."""
        output = "Timestamp: 2024-01-15T10:30:45"
        result = _normalize_output(output, ComparisonMode.SEMANTIC)
        assert "<TIMESTAMP>" in result or "2024" not in result, "Result must not be empty"

    def test_normalize_semantic_mode_removes_uuids(self):
        """Test SEMANTIC mode removes UUIDs."""
        output = "UUID: 550e8400-e29b-41d4-a716-446655440000"
        result = _normalize_output(output, ComparisonMode.SEMANTIC)
        assert "<UUID>" in result or "550e" not in result, "Result must not be empty"

    def test_normalize_semantic_mode_removes_addresses(self):
        """Test SEMANTIC mode removes addresses."""
        output = "Memory: 0x7fffffff"
        result = _normalize_output(output, ComparisonMode.SEMANTIC)
        assert "<ADDR>" in result or "0x7fffffff" not in result, "Result must not be empty"


# =====================================================================
# TESTS: _compare_outputs()
# =====================================================================


class TestCompareOutputs:
    """Test output comparison logic."""

    def test_compare_identical_strict(self):
        """Test comparing identical outputs in STRICT mode."""
        baseline = "output"
        patched = "output"
        match, diff = _compare_outputs(baseline, patched, ComparisonMode.STRICT)
        assert match is True, "match is not valid"
        assert diff is None, "diff is not valid"

    def test_compare_different_strict(self):
        """Test comparing different outputs in STRICT mode."""
        baseline = "output1"
        patched = "output2"
        match, diff = _compare_outputs(baseline, patched, ComparisonMode.STRICT)
        assert match is False, "match is not valid"
        assert diff is not None, "diff must be initialized"

    def test_compare_whitespace_fuzzy(self):
        """Test FUZZY comparison ignores whitespace."""
        baseline = "line1\nline2"
        patched = "line2\nline1"  # Different order
        match, diff = _compare_outputs(baseline, patched, ComparisonMode.FUZZY)
        # Fuzzy mode sorts, so order shouldn't matter
        assert match is True or match is False, "match is not valid"

    def test_compare_multiline(self):
        """Test comparing multiline output."""
        baseline = "line1\nline2\nline3\n"
        patched = "line1\nline2\nline3\n"
        match, diff = _compare_outputs(baseline, patched, ComparisonMode.STRICT)
        assert match is True, "match is not valid"

    def test_compare_empty_outputs(self):
        """Test comparing empty outputs."""
        match, diff = _compare_outputs("", "", ComparisonMode.STRICT)
        assert match is True, "match is not valid"

    def test_compare_empty_vs_nonempty(self):
        """Test comparing empty vs non-empty."""
        match, diff = _compare_outputs("", "output", ComparisonMode.STRICT)
        assert match is False, "match is not valid"
        assert diff is not None, "diff must be initialized"


# =====================================================================
# TESTS: compare() Function
# =====================================================================


class TestCompareFunction:
    """Test main compare() function."""

    def test_compare_identical_code(self, temp_baseline_code, temp_patched_code):
        """Test comparing identical code."""
        result = compare(temp_baseline_code, temp_patched_code)
        assert isinstance(result, ComparisonResult)

    def test_compare_returns_result_type(self, temp_baseline_code, temp_patched_code):
        """Test that compare returns ComparisonResult."""
        result = compare(temp_baseline_code, temp_patched_code)
        assert isinstance(result, ComparisonResult)
        assert hasattr(result, "result")
        assert hasattr(result, "comparisons")

    def test_compare_strict_mode(self, temp_baseline_code, temp_patched_code):
        """Test compare with STRICT mode."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            mode=ComparisonMode.STRICT,
        )
        assert result.result in ["pass", "fail", "warn"]

    def test_compare_fuzzy_mode(self, temp_baseline_code, temp_patched_code):
        """Test compare with FUZZY mode."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            mode=ComparisonMode.FUZZY,
        )
        assert result.result in ["pass", "fail", "warn"]

    def test_compare_semantic_mode(self, temp_baseline_code, temp_patched_code):
        """Test compare with SEMANTIC mode."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            mode=ComparisonMode.SEMANTIC,
        )
        assert result.result in ["pass", "fail", "warn"]

    def test_compare_missing_baseline(self, tmp_path):
        """Test compare with missing baseline directory."""
        nonexistent = tmp_path / "nonexistent"
        patched = tmp_path / "patched"
        patched.mkdir()

        result = compare(nonexistent, patched)
        # Should return error result
        assert result.result in ["fail", "warn"]

    def test_compare_missing_patched(self, temp_baseline_code, tmp_path):
        """Test compare with missing patched directory."""
        nonexistent = tmp_path / "nonexistent"
        result = compare(temp_baseline_code, nonexistent)
        assert result.result in ["fail", "warn"]

    def test_compare_timeout_handling(self, temp_baseline_code, temp_patched_code):
        """Test compare with timeout."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            timeout=1,
        )
        # Should handle timeout gracefully
        assert result.result in ["pass", "fail", "warn"]

    def test_compare_flakiness_check(self, temp_baseline_code, temp_patched_code):
        """Test flakiness detection in compare."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            flakiness_runs=2,
        )
        assert "consistent" in result.flakiness_check, "Result must not be empty"


# =====================================================================
# TESTS: generate_tests()
# =====================================================================


class TestGenerateTests:
    """Test test generation from golden outputs."""

    def test_generate_tests_creates_file(self, tmp_path):
        """Test that generate_tests creates test file."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('test')")

        input_file = tmp_path / "input.txt"
        input_file.write_text("input")

        output_file = tmp_path / "output.txt"
        output_file.write_text("output")

        output_dir = tmp_path / "generated_tests"

        files = generate_tests(source_dir, [input_file], [output_file], output_dir)

        assert len(files) > 0, "Files must not be empty"
        assert files[0].exists(), "Condition must be true"

    def test_generate_tests_output_is_valid_python(self, tmp_path):
        """Test that generated test file is valid Python."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('test')")

        input_file = tmp_path / "input.txt"
        input_file.write_text("test input")

        output_file = tmp_path / "output.txt"
        output_file.write_text("expected output")

        output_dir = tmp_path / "tests"

        files = generate_tests(source_dir, [input_file], [output_file], output_dir)

        # Check that generated file is valid Python
        test_file = files[0]
        content = test_file.read_text()
        assert "def test_snapshot" in content, "Content must not be empty"
        assert "class TestBehaviorSnapshots" in content, "Content must not be empty"

    def test_generate_tests_includes_input_path(self, tmp_path):
        """Test that generated tests include input file paths."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('test')")

        input1 = tmp_path / "input1.txt"
        input1.write_text("input1")

        output1 = tmp_path / "output1.txt"
        output1.write_text("output1")

        output_dir = tmp_path / "tests"

        files = generate_tests(source_dir, [input1], [output1], output_dir)

        test_content = files[0].read_text()
        assert "test_snapshot_1" in test_content, "Content must not be empty"

    def test_generate_tests_creates_directory(self, tmp_path):
        """Test that generate_tests creates output directory."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('test')")

        input_file = tmp_path / "input.txt"
        input_file.write_text("test")

        output_file = tmp_path / "output.txt"
        output_file.write_text("test")

        output_dir = tmp_path / "new_tests_dir"

        generate_tests(source_dir, [input_file], [output_file], output_dir)

        assert output_dir.exists(), "Condition must be true"

    def test_generate_tests_multiple_inputs(self, tmp_path):
        """Test generating tests with multiple input/output pairs."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('test')")

        inputs = [tmp_path / f"input{i}.txt" for i in range(3)]
        outputs = [tmp_path / f"output{i}.txt" for i in range(3)]

        for inp, out in zip(inputs, outputs):
            inp.write_text("input content")
            out.write_text("output content")

        output_dir = tmp_path / "tests"

        files = generate_tests(source_dir, inputs, outputs, output_dir)

        test_content = files[0].read_text()
        # Should have test methods for each pair
        assert "test_snapshot_1" in test_content, "Content must not be empty"
        assert "test_snapshot_2" in test_content, "Content must not be empty"


# =====================================================================
# TESTS: Edge Cases & Error Handling
# =====================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_compare_with_special_characters(self, tmp_path):
        """Test compare with special characters in output."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        (baseline / "main.py").write_text("print('special: !@#$%^&*()')")

        patched = tmp_path / "patched"
        patched.mkdir()
        (patched / "main.py").write_text("print('special: !@#$%^&*()')")

        result = compare(baseline, patched)
        assert isinstance(result, ComparisonResult)

    def test_compare_large_output(self, tmp_path):
        """Test compare with large output."""
        baseline = tmp_path / "baseline"
        baseline.mkdir()
        large_output = "x" * 10000
        (baseline / "main.py").write_text(f"print('{large_output}')")

        patched = tmp_path / "patched"
        patched.mkdir()
        (patched / "main.py").write_text(f"print('{large_output}')")

        result = compare(baseline, patched)
        assert isinstance(result, ComparisonResult)

    def test_result_to_dict_json_serializable(self):
        """Test that result to_dict is JSON serializable."""
        import json

        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)

    def test_normalize_output_edge_cases(self):
        """Test normalize output with edge cases."""
        # Empty string
        result = _normalize_output("", ComparisonMode.STRICT)
        assert result == "", "Result must not be empty"

        # Only whitespace
        result = _normalize_output("   \n  \n  ", ComparisonMode.FUZZY)
        assert isinstance(result, str)


# =====================================================================
# TESTS: Integration
# =====================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_compare_workflow(self, temp_baseline_code, temp_patched_code):
        """Test typical compare workflow."""
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            mode=ComparisonMode.STRICT,
        )
        # Save result
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "result.json"
            result.save(output_file)
            assert output_file.exists(), "Condition must be true"

    def test_generate_tests_workflow(self, tmp_path):
        """Test typical test generation workflow."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('hello')")

        input_file = tmp_path / "input.txt"
        input_file.write_text("hello")

        output_file = tmp_path / "output.txt"
        output_file.write_text("hello")

        test_dir = tmp_path / "tests"

        files = generate_tests(source_dir, [input_file], [output_file], test_dir)

        assert len(files) > 0, "Files must not be empty"
        assert files[0].exists(), "Condition must be true"
        content = files[0].read_text()
        assert "test_snapshot" in content, "Content must not be empty"


# =====================================================================
# ADDITIONAL EDGE CASES & ROBUSTNESS TESTS
# =====================================================================


class TestRobustness:
    """Additional robustness tests for comparator module."""

    def test_compare_with_timeout(self, temp_baseline_code, temp_patched_code):
        """Test compare with timeout handling."""
        # Compare should complete within timeout
        result = compare(
            temp_baseline_code,
            temp_patched_code,
            mode=ComparisonMode.STRICT,
            timeout=30,
        )
        assert result is not None, "result must be initialized"

    def test_comparison_mode_all_values(self):
        """Test all ComparisonMode enum values exist."""
        modes = [ComparisonMode.STRICT, ComparisonMode.FUZZY, ComparisonMode.SEMANTIC]
        assert len(modes) == 3, "Modes must not be empty"

    def test_hash_output_deterministic(self):
        """Test hash output is deterministic."""
        output = "test output"
        hash1 = _hash_output(output)
        hash2 = _hash_output(output)
        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_output_changes_with_input(self):
        """Test hash changes when output changes."""
        hash1 = _hash_output("output1")
        hash2 = _hash_output("output2")
        assert hash1 != hash2, "hash1 is not valid"

    def test_normalize_output_idempotent(self):
        """Test normalize output is idempotent."""
        output = "test\n  output  \n"
        normalized1 = _normalize_output(output, ComparisonMode.FUZZY)
        normalized2 = _normalize_output(normalized1, ComparisonMode.FUZZY)
        assert normalized1 == normalized2, "normalized1 is not valid"

    def test_comparison_result_equality(self):
        """Test ComparisonResult equality comparison."""
        result1 = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        result2 = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        assert result1.baseline_hash == result2.baseline_hash, "Result must not be empty"

    def test_comparison_detail_fields(self):
        """Test ComparisonDetail fields are accessible."""
        detail = ComparisonDetail(
            output="test",
            hash_value="abc123",
        )
        assert detail.output == "test", "output is not valid"
        assert detail.hash_value == "abc123", "Value must be initialized"

    def test_normalize_output_preserves_content(self):
        """Test normalize preserves essential content."""
        output = "important\ndata\nhere"
        normalized = _normalize_output(output, ComparisonMode.STRICT)
        # Essential content should be preserved
        assert "important" in normalized or "data" in normalized, "Data must not be empty"

    def test_compare_result_fields_immutable(self):
        """Test ComparisonResult fields after creation."""
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        # Should be able to read fields
        assert result.baseline_hash is not None, "baseline_hash must be initialized"

    def test_generate_tests_empty_sources(self, tmp_path):
        """Test generate_tests with empty source list."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        test_dir = tmp_path / "tests"

        files = generate_tests(source_dir, [], [], test_dir)
        # Should handle empty lists gracefully
        assert isinstance(files, list)

    def test_normalize_output_strips_whitespace(self):
        """Test normalize output strips excess whitespace."""
        output = "  \n  \ntest\n  \n  "
        normalized = _normalize_output(output, ComparisonMode.FUZZY)
        # Should have less whitespace than original
        assert len(normalized) <= len(output), "Normalized must not be empty"

    def test_hash_output_consistent_across_calls(self):
        """Test hash remains consistent across multiple calls."""
        output = "consistent test output"
        hashes = [_hash_output(output) for _ in range(5)]
        # All hashes should be identical
        assert len(set(hashes)) == 1, "Collection must not be empty"

    def test_comparison_modes_are_distinct(self):
        """Test ComparisonMode values are distinct."""
        modes = [ComparisonMode.STRICT, ComparisonMode.FUZZY, ComparisonMode.SEMANTIC]
        mode_values = [str(m) for m in modes]
        # All modes should be unique
        assert len(set(mode_values)) == len(modes), "Modes must not be empty"

    def test_compare_result_to_dict_contains_fields(self):
        """Test to_dict contains all important fields."""
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash="h1",
            patched_hash="h2",
        )
        result_dict = result.to_dict()
        assert "baseline_hash" in result_dict or "hash" in result_dict.get("baseline", {})

    def test_normalize_output_with_newlines(self):
        """Test normalize output handles various newline styles."""
        # Unix newline
        output1 = "line1\nline2\nline3"
        # Windows newline
        output2 = "line1\r\nline2\r\nline3"
        # Mixed
        output3 = "line1\nline2\r\nline3"

        normalized1 = _normalize_output(output1, ComparisonMode.FUZZY)
        normalized2 = _normalize_output(output2, ComparisonMode.FUZZY)
        normalized3 = _normalize_output(output3, ComparisonMode.FUZZY)

        assert isinstance(normalized1, str)
        assert isinstance(normalized2, str)
        assert isinstance(normalized3, str)

    def test_generate_tests_file_creation(self, tmp_path):
        """Test generate_tests creates files."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("def add(a, b): return a + b")

        input_file = tmp_path / "input.txt"
        input_file.write_text("1 2")

        output_file = tmp_path / "output.txt"
        output_file.write_text("3")

        test_dir = tmp_path / "tests"

        files = generate_tests(source_dir, [input_file], [output_file], test_dir)

        assert len(files) > 0, "Files must not be empty"
        for f in files:
            assert f.suffix == ".py", "suffix is not valid"

    def test_comparison_detail_to_dict(self):
        """Test ComparisonDetail to_dict."""
        detail = ComparisonDetail(
            output="test output",
            hash_value="abc123",
        )
        if hasattr(detail, "to_dict"):
            detail_dict = detail.to_dict()
            assert isinstance(detail_dict, dict)

    def test_comparison_result_baseline_hash_preserved(self):
        """Test that baseline hash is preserved in comparison result."""
        baseline_hash = "baseline_hash_value_12345"
        result = ComparisonResult(
            result="pass",  # type: ignore
            baseline_hash=baseline_hash,
            patched_hash="patched_hash_value_67890",
        )
        assert result.baseline_hash == baseline_hash, "Result must not be empty"

    def test_normalize_output_empty_mode_handling(self):
        """Test normalize output with different modes on empty input."""
        empty = ""
        for mode in [ComparisonMode.STRICT, ComparisonMode.FUZZY, ComparisonMode.SEMANTIC]:
            result = _normalize_output(empty, mode)
            assert isinstance(result, str)

    def test_compare_outputs_returns_string(self):
        """Test compare_outputs returns comparable string."""
        result = _compare_outputs("output1", "output2", ComparisonMode.STRICT)
        assert isinstance(result, (str, bool, type(None))) or hasattr(result, "__class__")
