"""
Comprehensive tests for the Codex Verify module.

Tests cover:
- Behavior comparison
- Comparison modes (strict, fuzzy, semantic)
- Flakiness detection
- Test generation
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestBehaviorComparator:
    """Tests for behavior comparison functionality."""

    def test_compare_identical_outputs(self, tmp_path: Path):
        """Test comparison of identical outputs."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        # Create identical scripts
        script = "print('hello')\n"
        (baseline_dir / "main.py").write_text(script, encoding="utf-8")
        (patched_dir / "main.py").write_text(script, encoding="utf-8")
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        
        assert result.result == "pass"
        assert len(result.comparisons) > 0

    def test_compare_different_outputs(self, tmp_path: Path):
        """Test comparison of different outputs."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        (baseline_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("print('world')\n", encoding="utf-8")
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        
        assert result.result == "fail"

    def test_compare_fuzzy_mode(self, tmp_path: Path):
        """Test fuzzy comparison mode."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        # Scripts with different whitespace but same content
        (baseline_dir / "main.py").write_text("print('a')\nprint('b')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("print('b')\nprint('a')\n", encoding="utf-8")
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.FUZZY)
        
        # Fuzzy mode should pass (same lines, different order)
        assert result.result == "pass"

    def test_compare_no_entry_point(self, tmp_path: Path):
        """Test comparison when no entry point is found."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        # Empty directories
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        
        assert result.result == "warn"
        assert any(c.result == "error" for c in result.comparisons)

    def test_comparison_result_to_dict(self, tmp_path: Path):
        """Test ComparisonResult serialization."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        (baseline_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        data = result.to_dict()
        
        assert "result" in data
        assert "baseline_hash" in data
        assert "patched_hash" in data
        assert "comparisons" in data
        assert "flakiness_check" in data

    def test_comparison_result_save(self, tmp_path: Path):
        """Test saving ComparisonResult to file."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        (baseline_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        
        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        
        output_path = tmp_path / "diff.json"
        result.save(output_path)
        
        assert output_path.exists()
        with output_path.open() as f:
            data = json.load(f)
        assert data["result"] in ["pass", "fail", "warn"]


class TestOutputNormalization:
    """Tests for output normalization."""

    def test_normalize_strict(self):
        """Test strict mode normalization (no changes)."""
        from src.codex.verify.comparator import _normalize_output, ComparisonMode
        
        output = "  line1  \n  line2  \n"
        result = _normalize_output(output, ComparisonMode.STRICT)
        
        assert result == output

    def test_normalize_fuzzy(self):
        """Test fuzzy mode normalization."""
        from src.codex.verify.comparator import _normalize_output, ComparisonMode
        
        output = "  line2  \n  line1  \n  "
        result = _normalize_output(output, ComparisonMode.FUZZY)
        
        # Should be stripped, sorted
        assert "line1" in result
        assert "line2" in result

    def test_normalize_semantic(self):
        """Test semantic mode normalization."""
        from src.codex.verify.comparator import _normalize_output, ComparisonMode
        
        output = "Timestamp: 2025-12-17T12:00:00 ID: abc12345-1234-1234-1234-123456789012"
        result = _normalize_output(output, ComparisonMode.SEMANTIC)
        
        assert "<TIMESTAMP>" in result
        assert "<UUID>" in result


class TestOutputComparison:
    """Tests for output comparison logic."""

    def test_compare_outputs_match(self):
        """Test comparing matching outputs."""
        from src.codex.verify.comparator import _compare_outputs, ComparisonMode
        
        match, diff = _compare_outputs("hello", "hello", ComparisonMode.STRICT)
        
        assert match is True
        assert diff is None

    def test_compare_outputs_mismatch(self):
        """Test comparing mismatched outputs."""
        from src.codex.verify.comparator import _compare_outputs, ComparisonMode
        
        match, diff = _compare_outputs("hello", "world", ComparisonMode.STRICT)
        
        assert match is False
        assert diff is not None
        assert "-hello" in diff or "+world" in diff

    def test_compare_outputs_fuzzy_whitespace(self):
        """Test fuzzy comparison ignores whitespace."""
        from src.codex.verify.comparator import _compare_outputs, ComparisonMode
        
        match, diff = _compare_outputs("  hello  ", "hello", ComparisonMode.FUZZY)
        
        assert match is True


class TestHashOutput:
    """Tests for output hashing."""

    def test_hash_output_deterministic(self):
        """Test that output hashing is deterministic."""
        from src.codex.verify.comparator import _hash_output
        
        output = "test output"
        hash1 = _hash_output(output)
        hash2 = _hash_output(output)
        
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_hash_output_different(self):
        """Test that different outputs have different hashes."""
        from src.codex.verify.comparator import _hash_output
        
        hash1 = _hash_output("output1")
        hash2 = _hash_output("output2")
        
        assert hash1 != hash2


class TestTestGeneration:
    """Tests for test generation functionality."""

    def test_generate_tests_creates_file(self, tmp_path: Path):
        """Test that test generation creates test file."""
        from src.codex.verify.comparator import generate_tests
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
        
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        input_file = samples_dir / "input1.txt"
        output_file = samples_dir / "output1.txt"
        input_file.write_text("test input\n", encoding="utf-8")
        output_file.write_text("test output\n", encoding="utf-8")
        
        output_dir = tmp_path / "tests"
        
        generated = generate_tests(source_dir, [input_file], [output_file], output_dir)
        
        assert len(generated) > 0
        assert generated[0].exists()

    def test_generated_test_content(self, tmp_path: Path):
        """Test content of generated test file."""
        from src.codex.verify.comparator import generate_tests
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
        
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        input_file = samples_dir / "input1.txt"
        output_file = samples_dir / "output1.txt"
        input_file.write_text("input\n", encoding="utf-8")
        output_file.write_text("output\n", encoding="utf-8")
        
        output_dir = tmp_path / "tests"
        
        generated = generate_tests(source_dir, [input_file], [output_file], output_dir)
        
        content = generated[0].read_text()
        assert "pytest" in content
        assert "TestBehaviorSnapshots" in content
        assert "def test_snapshot" in content


class TestComparisonDetail:
    """Tests for ComparisonDetail dataclass."""

    def test_comparison_detail_creation(self):
        """Test creating ComparisonDetail."""
        from src.codex.verify.comparator import ComparisonDetail, ComparisonMode
        
        detail = ComparisonDetail(
            input_ref="input.txt",
            mode=ComparisonMode.STRICT,
            result="match",
        )
        
        assert detail.input_ref == "input.txt"
        assert detail.result == "match"
        assert detail.diff is None


class TestFlakiness:
    """Tests for flakiness detection."""

    def test_flakiness_check_in_result(self, tmp_path: Path):
        """Test that flakiness check is included in result."""
        from src.codex.verify.comparator import compare, ComparisonMode
        
        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()
        
        (baseline_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("print('test')\n", encoding="utf-8")
        
        result = compare(
            baseline_dir, 
            patched_dir, 
            mode=ComparisonMode.STRICT,
            flakiness_runs=3
        )
        
        assert "runs" in result.flakiness_check
        assert "consistent" in result.flakiness_check
