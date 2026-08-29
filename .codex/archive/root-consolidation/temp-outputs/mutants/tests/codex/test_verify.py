"""
Comprehensive tests for the Codex Verify module.

Tests cover:
- Behavior comparison
- Comparison modes (strict, fuzzy, semantic)
- Flakiness detection
- Test generation
"""

import json
from pathlib import Path


class TestBehaviorComparator:
    """Tests for behavior comparison functionality."""

    def test_compare_identical_outputs(self, tmp_path: Path):
        """Test comparison of identical outputs."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        # Create identical scripts
        script = "logger.info('hello')\n"
        (baseline_dir / "main.py").write_text(script, encoding="utf-8")
        (patched_dir / "main.py").write_text(script, encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)

        assert result.result == "pass", "Result must not be empty"
        assert len(result.comparisons) > 0, "Collection must not be empty"

    def test_compare_different_outputs(self, tmp_path: Path):
        """Test comparison of different outputs."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        (baseline_dir / "main.py").write_text("logger.info('hello')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("logger.info('world')\n", encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)

        assert result.result == "fail", "Result must not be empty"

    def test_compare_fuzzy_mode(self, tmp_path: Path):
        """Test fuzzy comparison mode."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        # Scripts with different whitespace but same content
        (baseline_dir / "main.py").write_text("logger.info('a')\nprint('b')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("logger.info('b')\nprint('a')\n", encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.FUZZY)

        # Fuzzy mode should pass (same lines, different order)
        assert result.result == "pass", "Result must not be empty"

    def test_compare_no_entry_point(self, tmp_path: Path):
        """Test comparison when no entry point is found."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        # Empty directories

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)

        assert result.result == "warn", "Result must not be empty"
        assert any(c.result == "error" for c in result.comparisons), "Result must not be empty"

    def test_comparison_result_to_dict(self, tmp_path: Path):
        """Test ComparisonResult serialization."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        (baseline_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)
        data = result.to_dict()

        assert "result" in data, "Result must not be empty"
        assert "baseline_hash" in data, "Data must not be empty"
        assert "patched_hash" in data, "Data must not be empty"
        assert "comparisons" in data, "Data must not be empty"
        assert "flakiness_check" in data, "Data must not be empty"

    def test_comparison_result_save(self, tmp_path: Path):
        """Test saving ComparisonResult to file."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        (baseline_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT)

        output_path = tmp_path / "diff.json"
        result.save(output_path)

        assert output_path.exists(), "Condition must be true"
        with output_path.open() as f:
            data = json.load(f)
        assert data["result"] in ["pass", "fail", "warn"]


class TestOutputNormalization:
    """Tests for output normalization."""

    def test_normalize_strict(self):
        """Test strict mode normalization (no changes)."""
        from codex.verify.comparator import ComparisonMode, _normalize_output

        output = "  line1  \n  line2  \n"
        result = _normalize_output(output, ComparisonMode.STRICT)

        assert result == output, "Result must not be empty"

    def test_normalize_fuzzy(self):
        """Test fuzzy mode normalization."""
        from codex.verify.comparator import ComparisonMode, _normalize_output

        output = "  line2  \n  line1  \n  "
        result = _normalize_output(output, ComparisonMode.FUZZY)

        # Should be stripped, sorted
        assert "line1" in result, "Result must not be empty"
        assert "line2" in result, "Result must not be empty"

    def test_normalize_semantic(self):
        """Test semantic mode normalization."""
        from codex.verify.comparator import ComparisonMode, _normalize_output

        output = "Timestamp: 2025-12-17T12:00:00 ID: abc12345-1234-1234-1234-123456789012"
        result = _normalize_output(output, ComparisonMode.SEMANTIC)

        assert "<TIMESTAMP>" in result, "Result must not be empty"
        assert "<UUID>" in result, "Result must not be empty"


class TestOutputComparison:
    """Tests for output comparison logic."""

    def test_compare_outputs_match(self):
        """Test comparing matching outputs."""
        from codex.verify.comparator import ComparisonMode, _compare_outputs

        match, diff = _compare_outputs("hello", "hello", ComparisonMode.STRICT)

        assert match is True, "match is not valid"
        assert diff is None, "diff is not valid"

    def test_compare_outputs_mismatch(self):
        """Test comparing mismatched outputs."""
        from codex.verify.comparator import ComparisonMode, _compare_outputs

        match, diff = _compare_outputs("hello", "world", ComparisonMode.STRICT)

        assert match is False, "match is not valid"
        assert diff is not None, "diff must be initialized"
        assert "-hello" in diff or "+world" in diff, "Condition must be true"

    def test_compare_outputs_fuzzy_whitespace(self):
        """Test fuzzy comparison ignores whitespace."""
        from codex.verify.comparator import ComparisonMode, _compare_outputs

        match, _diff = _compare_outputs("  hello  ", "hello", ComparisonMode.FUZZY)

        assert match is True, "match is not valid"


class TestHashOutput:
    """Tests for output hashing."""

    def test_hash_output_deterministic(self):
        """Test that output hashing is deterministic."""
        from codex.verify.comparator import _hash_output

        output = "test output"
        hash1 = _hash_output(output)
        hash2 = _hash_output(output)

        assert hash1 == hash2, "hash1 is not valid"
        assert len(hash1) == 64, "Hash1 must not be empty"

    def test_hash_output_different(self):
        """Test that different outputs have different hashes."""
        from codex.verify.comparator import _hash_output

        hash1 = _hash_output("output1")
        hash2 = _hash_output("output2")

        assert hash1 != hash2, "hash1 is not valid"


class TestTestGeneration:
    """Tests for test generation functionality."""

    def test_generate_tests_creates_file(self, tmp_path: Path):
        """Test that test generation creates test file."""
        from codex.verify.comparator import generate_tests

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("logger.info('hello')\n", encoding="utf-8")

        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        input_file = samples_dir / "input1.txt"
        output_file = samples_dir / "output1.txt"
        input_file.write_text("test input\n", encoding="utf-8")
        output_file.write_text("test output\n", encoding="utf-8")

        output_dir = tmp_path / "tests"

        generated = generate_tests(source_dir, [input_file], [output_file], output_dir)

        assert len(generated) > 0, "Generated must not be empty"
        assert generated[0].exists(), "Condition must be true"

    def test_generated_test_content(self, tmp_path: Path):
        """Test content of generated test file."""
        from codex.verify.comparator import generate_tests

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("logger.info('hello')\n", encoding="utf-8")

        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        input_file = samples_dir / "input1.txt"
        output_file = samples_dir / "output1.txt"
        input_file.write_text("input\n", encoding="utf-8")
        output_file.write_text("output\n", encoding="utf-8")

        output_dir = tmp_path / "tests"

        generated = generate_tests(source_dir, [input_file], [output_file], output_dir)

        content = generated[0].read_text()
        assert "pytest" in content, "Content must not be empty"
        assert "TestBehaviorSnapshots" in content, "Content must not be empty"
        assert "def test_snapshot" in content, "Content must not be empty"


class TestComparisonDetail:
    """Tests for ComparisonDetail dataclass."""

    def test_comparison_detail_creation(self):
        """Test creating ComparisonDetail."""
        from codex.verify.comparator import ComparisonDetail, ComparisonMode

        detail = ComparisonDetail(
            input_ref="input.txt",
            mode=ComparisonMode.STRICT,
            result="match",
        )

        assert detail.input_ref == "input.txt", "input_ref is not valid"
        assert detail.result == "match", "Result must not be empty"
        assert detail.diff is None, "diff is not valid"


class TestFlakiness:
    """Tests for flakiness detection."""

    def test_flakiness_check_in_result(self, tmp_path: Path):
        """Test that flakiness check is included in result."""
        from codex.verify.comparator import ComparisonMode, compare

        baseline_dir = tmp_path / "baseline"
        patched_dir = tmp_path / "patched"
        baseline_dir.mkdir()
        patched_dir.mkdir()

        (baseline_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")
        (patched_dir / "main.py").write_text("logger.info('test')\n", encoding="utf-8")

        result = compare(baseline_dir, patched_dir, mode=ComparisonMode.STRICT, flakiness_runs=3)

        assert "runs" in result.flakiness_check, "Result must not be empty"
        assert "consistent" in result.flakiness_check, "Result must not be empty"
