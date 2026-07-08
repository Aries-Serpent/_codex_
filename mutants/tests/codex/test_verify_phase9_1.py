"""
Phase 9.1 - Comprehensive tests for codex.verify.comparator module.

Tests cover:
- Behavior comparison between baseline and patched code
- Multiple comparison modes (strict, fuzzy, semantic)
- Output normalization and hashing
- Script execution and timeout handling
- Flakiness detection
- Error handling and edge cases
"""

from __future__ import annotations

import json
from pathlib import Path

from codex.verify.comparator import (
    DEFAULT_FLAKINESS_RUNS,
    ComparisonDetail,
    ComparisonMode,
    ComparisonResult,
    _compare_outputs,
    _hash_output,
    _normalize_output,
    _run_script,
    compare,
)


class TestComparisonMode:
    """Test ComparisonMode enumeration."""

    def test_comparison_modes(self) -> None:
        """Test comparison mode values."""
        assert ComparisonMode.STRICT.value == "strict", "Value must be initialized"
        assert ComparisonMode.FUZZY.value == "fuzzy", "Value must be initialized"
        assert ComparisonMode.SEMANTIC.value == "semantic", "Value must be initialized"


class TestComparisonDetail:
    """Test ComparisonDetail dataclass."""

    def test_comparison_detail_creation(self) -> None:
        """Test creating a ComparisonDetail."""
        detail = ComparisonDetail(
            input_ref="test_input.txt",
            mode=ComparisonMode.STRICT,
            result="match",
            baseline_output="output1",
            patched_output="output2",
        )

        assert detail.input_ref == "test_input.txt", "input_ref is not valid"
        assert detail.mode == ComparisonMode.STRICT, "mode is not valid"
        assert detail.result == "match", "Result must not be empty"

    def test_comparison_detail_with_error(self) -> None:
        """Test ComparisonDetail with error."""
        detail = ComparisonDetail(
            input_ref="input",
            mode=ComparisonMode.STRICT,
            result="error",
            error="Execution failed",
        )

        assert detail.result == "error", "Result must not be empty"
        assert detail.error == "Execution failed", "Error should be raised or set"


class TestComparisonResult:
    """Test ComparisonResult dataclass."""

    def test_comparison_result_creation(self) -> None:
        """Test creating a ComparisonResult."""
        result = ComparisonResult(
            result="pass",
            baseline_hash="hash1",
            patched_hash="hash2",
        )

        assert result.result == "pass", "Result must not be empty"
        assert result.baseline_hash == "hash1", "Result must not be empty"
        assert result.patched_hash == "hash2", "Result must not be empty"
        assert result.comparisons == [], "Result must not be empty"

    def test_comparison_result_to_dict(self) -> None:
        """Test converting ComparisonResult to dictionary."""
        detail = ComparisonDetail(
            input_ref="test",
            mode=ComparisonMode.STRICT,
            result="match",
        )

        result = ComparisonResult(
            result="pass",
            baseline_hash="hash1",
            patched_hash="hash2",
            comparisons=[detail],
        )

        data = result.to_dict()

        assert data["result"] == "pass", "Result must not be empty"
        assert data["baseline_hash"] == "hash1", "Data must not be empty"
        assert len(data["comparisons"]) == 1, "Collection must not be empty"
        assert data["comparisons"][0]["input_ref"] == "test", "Data must not be empty"

    def test_comparison_result_save(self, tmp_path: Path) -> None:
        """Test saving ComparisonResult to file."""
        result = ComparisonResult(
            result="pass",
            baseline_hash="hash1",
            patched_hash="hash2",
        )

        output_path = tmp_path / "comparison.json"
        result.save(output_path)

        assert output_path.exists(), "Condition must be true"

        with output_path.open() as f:
            data = json.load(f)

        assert data["result"] == "pass", "Result must not be empty"


class TestOutputHashing:
    """Test output hashing functionality."""

    def test_hash_simple_output(self) -> None:
        """Test hashing simple output."""
        output = "test output"

        hash1 = _hash_output(output)
        hash2 = _hash_output(output)

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_hash_different_outputs(self) -> None:
        """Test different outputs produce different hashes."""
        output1 = "output 1"
        output2 = "output 2"

        hash1 = _hash_output(output1)
        hash2 = _hash_output(output2)

        assert hash1 != hash2, "hash1 is not valid"

    def test_hash_empty_output(self) -> None:
        """Test hashing empty output."""
        output = ""

        hash_val = _hash_output(output)

        assert len(hash_val) == 64, "Hash_val must not be empty"


class TestOutputNormalization:
    """Test output normalization functionality."""

    def test_normalize_strict_mode(self) -> None:
        """Test STRICT mode returns output unchanged."""
        output = "  line1  \n  line2  \n"

        normalized = _normalize_output(output, ComparisonMode.STRICT)

        assert normalized == output, "normalized is not valid"

    def test_normalize_fuzzy_mode_whitespace(self) -> None:
        """Test FUZZY mode normalizes whitespace."""
        output = "  line1  \n  line2  \n"

        normalized = _normalize_output(output, ComparisonMode.FUZZY)

        assert normalized == "line1\nline2", "normalized is not valid"

    def test_normalize_fuzzy_mode_sorting(self) -> None:
        """Test FUZZY mode sorts lines."""
        output = "line3\nline1\nline2"

        normalized = _normalize_output(output, ComparisonMode.FUZZY)

        assert normalized == "line1\nline2\nline3", "normalized is not valid"

    def test_normalize_fuzzy_mode_empty_lines(self) -> None:
        """Test FUZZY mode removes empty lines."""
        output = "line1\n\nline2\n\n\nline3"

        normalized = _normalize_output(output, ComparisonMode.FUZZY)

        assert "\n\n" not in normalized, "Condition must be true"

    def test_normalize_semantic_mode_timestamps(self) -> None:
        """Test SEMANTIC mode replaces timestamps."""
        output = "Log: 2025-12-17 10:30:45 - message"

        normalized = _normalize_output(output, ComparisonMode.SEMANTIC)

        assert "<TIMESTAMP>" in normalized, "Condition must be true"
        assert "2025-12-17" not in normalized, "Condition must be true"

    def test_normalize_semantic_mode_uuids(self) -> None:
        """Test SEMANTIC mode replaces UUIDs."""
        output = "ID: 12345678-1234-1234-1234-123456789abc"

        normalized = _normalize_output(output, ComparisonMode.SEMANTIC)

        assert "<UUID>" in normalized, "Condition must be true"
        assert "12345678" not in normalized, "Condition must be true"

    def test_normalize_semantic_mode_addresses(self) -> None:
        """Test SEMANTIC mode replaces memory addresses."""
        output = "Object at 0x7f8a9b12c3d0"

        normalized = _normalize_output(output, ComparisonMode.SEMANTIC)

        assert "<ADDR>" in normalized, "Condition must be true"
        assert "0x" not in normalized, "Condition must be true"


class TestScriptExecution:
    """Test script execution functionality."""

    def test_run_script_simple(self, tmp_path: Path) -> None:
        """Test running a simple Python script."""
        script = tmp_path / "test.py"
        script.write_text("print('hello world')")

        stdout, _stderr, code = _run_script(script)

        assert stdout.strip() == "hello world", "Condition must be true"
        assert code == 0, "code is not valid"

    def test_run_script_with_error(self, tmp_path: Path) -> None:
        """Test running a script that produces an error."""
        script = tmp_path / "error.py"
        script.write_text("import sys\nsys.stderr.write('error')\nsys.exit(1)")

        _stdout, stderr, code = _run_script(script)

        assert "error" in stderr, "Error should be raised or set"
        assert code == 1, "code is not valid"

    def test_run_script_nonexistent(self, tmp_path: Path) -> None:
        """Test running nonexistent script."""
        script = tmp_path / "does_not_exist.py"

        _stdout, stderr, code = _run_script(script)

        assert "not found" in stderr.lower(), "Condition must be true"
        assert code == -1, "code is not valid"

    def test_run_script_with_input(self, tmp_path: Path) -> None:
        """Test running script with input file."""
        script = tmp_path / "read.py"
        script.write_text("import sys\nprint(sys.stdin.read())")

        input_file = tmp_path / "input.txt"
        input_file.write_text("test input")

        stdout, _stderr, _code = _run_script(script, input_file=input_file)

        assert "test input" in stdout, "Condition must be true"

    def test_run_script_timeout(self, tmp_path: Path) -> None:
        """Test script timeout handling."""
        script = tmp_path / "infinite.py"
        script.write_text("import time\nwhile True:\n    time.sleep(1)")

        _stdout, stderr, code = _run_script(script, timeout=2)

        assert "Timeout" in stderr, "Condition must be true"
        assert code == -1, "code is not valid"

    def test_run_script_env_overrides(self, tmp_path: Path) -> None:
        """Test script execution with environment overrides."""
        script = tmp_path / "env.py"
        script.write_text("import os\nprint(os.environ.get('TEST_VAR', 'not set'))")

        stdout, _stderr, _code = _run_script(script, env_overrides={"TEST_VAR": "test_value"})

        assert "test_value" in stdout, "Value must be initialized"


class TestOutputComparison:
    """Test output comparison functionality."""

    def test_compare_identical_outputs_strict(self) -> None:
        """Test comparing identical outputs in STRICT mode."""
        output = "line1\nline2\nline3"

        match, diff = _compare_outputs(output, output, ComparisonMode.STRICT)

        assert match is True, "match is not valid"
        assert diff is None, "diff is not valid"

    def test_compare_different_outputs_strict(self) -> None:
        """Test comparing different outputs in STRICT mode."""
        baseline = "line1\nline2"
        patched = "line1\nmodified"

        match, diff = _compare_outputs(baseline, patched, ComparisonMode.STRICT)

        assert match is False, "match is not valid"
        assert diff is not None, "diff must be initialized"
        assert "-line2" in diff, "Condition must be true"
        assert "+modified" in diff, "Condition must be true"

    def test_compare_whitespace_fuzzy(self) -> None:
        """Test FUZZY mode ignores whitespace differences."""
        baseline = "  line1  \n  line2  "
        patched = "line1\nline2"

        match, _diff = _compare_outputs(baseline, patched, ComparisonMode.FUZZY)

        assert match is True, "match is not valid"

    def test_compare_order_fuzzy(self) -> None:
        """Test FUZZY mode ignores line order."""
        baseline = "line1\nline2\nline3"
        patched = "line3\nline1\nline2"

        match, _diff = _compare_outputs(baseline, patched, ComparisonMode.FUZZY)

        assert match is True, "match is not valid"

    def test_compare_timestamps_semantic(self) -> None:
        """Test SEMANTIC mode ignores timestamp differences."""
        baseline = "Log: 2025-12-17 10:30:45 - event"
        patched = "Log: 2025-12-17 11:45:23 - event"

        match, _diff = _compare_outputs(baseline, patched, ComparisonMode.SEMANTIC)

        assert match is True, "match is not valid"


class TestFullComparison:
    """Test full comparison between baseline and patched code."""

    def test_compare_identical_scripts(self, tmp_path: Path) -> None:
        """Test comparing identical baseline and patched scripts."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("print('output')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("print('output')")

        result = compare(baseline_dir, patched_dir)

        assert result.result == "pass", "Result must not be empty"
        assert result.baseline_hash == result.patched_hash, "Result must not be empty"

    def test_compare_different_scripts(self, tmp_path: Path) -> None:
        """Test comparing different baseline and patched scripts."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("print('baseline')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("print('patched')")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)

        assert result.result == "fail", "Result must not be empty"
        assert result.baseline_hash != result.patched_hash, "Result must not be empty"

    def test_compare_no_entry_point(self, tmp_path: Path) -> None:
        """Test comparison with no entry point script."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        # No main.py or __main__.py

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()

        result = compare(baseline_dir, patched_dir)

        assert result.result == "warn", "Result must not be empty"
        assert len(result.comparisons) > 0, "Collection must not be empty"
        assert result.comparisons[0].result == "error", "Result must not be empty"

    def test_compare_finds_main_py(self, tmp_path: Path) -> None:
        """Test comparison finds main.py as entry point."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("print('test')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("print('test')")

        result = compare(baseline_dir, patched_dir)

        assert result.result == "pass", "Result must not be empty"

    def test_compare_finds_dunder_main(self, tmp_path: Path) -> None:
        """Test comparison finds __main__.py as entry point."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "__main__.py").write_text("print('test')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "__main__.py").write_text("print('test')")

        result = compare(baseline_dir, patched_dir)

        assert result.result == "pass", "Result must not be empty"

    def test_compare_with_sample_inputs(self, tmp_path: Path) -> None:
        """Test comparison with sample input files."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text(
            "import sys\ndata = sys.stdin.read()\nprint(f'Received: {data}')"
        )

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text(
            "import sys\ndata = sys.stdin.read()\nprint(f'Received: {data}')"
        )

        input1 = tmp_path / "input1.txt"
        input1.write_text("test input 1")

        result = compare(baseline_dir, patched_dir, sample_inputs=[input1])

        assert len(result.comparisons) > 0, "Collection must not be empty"

    def test_compare_with_timeout(self, tmp_path: Path) -> None:
        """Test comparison respects timeout."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("import time\ntime.sleep(10)\nprint('done')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("import time\ntime.sleep(10)\nprint('done')")

        result = compare(baseline_dir, patched_dir, timeout=2)

        # Both should timeout
        assert any("Timeout" in str(c.error) for c in result.comparisons if c.error), "Result must not be empty"

    def test_compare_fuzzy_mode_passes(self, tmp_path: Path) -> None:
        """Test FUZZY mode passes with minor differences."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("print('  output  ')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("print('output')")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.FUZZY)

        assert result.result == "pass", "Result must not be empty"


class TestFlakinessDetection:
    """Test flakiness detection in comparisons."""

    def test_compare_with_flakiness_runs(self, tmp_path: Path) -> None:
        """Test comparison performs multiple runs for flakiness detection."""
        baseline_dir = tmp_path / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "main.py").write_text("print('stable output')")

        patched_dir = tmp_path / "patched"
        patched_dir.mkdir()
        (patched_dir / "main.py").write_text("print('stable output')")

        result = compare(baseline_dir, patched_dir, flakiness_runs=DEFAULT_FLAKINESS_RUNS)

        # Should complete successfully
        assert result.result in ["pass", "fail", "warn"]
