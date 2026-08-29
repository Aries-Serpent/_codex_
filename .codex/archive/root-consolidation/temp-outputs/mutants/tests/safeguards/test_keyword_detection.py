"""
Comprehensive test suite for safeguard keyword detection.

Tests cover keyword detection, context-aware pattern matching, false positive
filtering, and density calculations following the High Maturity Achievement Plan.
"""

import importlib.util
import types
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def _load_module(path: Path, name: str) -> types.ModuleType:
    """Load detector module dynamically."""
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / path
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "spec is not valid"
    spec.loader.exec_module(module)
    return module


def _context_index_for(paths: Iterable[Path]) -> dict[str, Any]:
    """Create context index from file paths using absolute paths."""
    return {
        "files": [{"path": str(path.resolve())} for path in paths],  # Use absolute paths
    }


class TestKeywordDetection:
    """Test individual safeguard keyword detection."""

    def test_sha256_detection(self, tmp_path: Path):
        """Test detection of sha256 keyword."""
        test_file = tmp_path / "crypto.py"
        test_file.write_text("hash = sha256(data)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "sha256" in result["found_patterns"], "Result must not be empty"
        assert result["total_hits"] >= 1, "Value must be greater than zero"

    def test_validate_detection(self, tmp_path: Path):
        """Test detection of validation keyword."""
        test_file = tmp_path / "validator.py"
        test_file.write_text("def validate(input): pass\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "validate" in result["found_patterns"], "Result must not be empty"

    def test_sanitize_detection(self, tmp_path: Path):
        """Test detection of sanitize keyword."""
        test_file = tmp_path / "security.py"
        test_file.write_text("sanitized = sanitize(user_input)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "sanitize" in result["found_patterns"], "Result must not be empty"

    def test_timeout_detection(self, tmp_path: Path):
        """Test detection of timeout keyword."""
        test_file = tmp_path / "network.py"
        test_file.write_text("response = request(url, timeout=30)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "timeout" in result["found_patterns"], "Result must not be empty"

    def test_bounds_check_detection(self, tmp_path: Path):
        """Test detection of bounded keyword."""
        test_file = tmp_path / "limits.py"
        test_file.write_text("if value > max_value: # bounded check\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "bounded" in result["found_patterns"], "Result must not be empty"

    def test_deterministic_detection(self, tmp_path: Path):
        """Test detection of deterministic keyword."""
        test_file = tmp_path / "algorithm.py"
        test_file.write_text("# deterministic algorithm\nresult = process()\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "deterministic" in result["found_patterns"], "Result must not be empty"


class TestContextAwareDetection:
    """Test context-aware pattern detection beyond keywords."""

    def test_try_except_pattern(self, tmp_path: Path):
        """Test detection of try-except error handling."""
        test_file = tmp_path / "errors.py"
        test_file.write_text(
            """
try:
    risky_operation()
except Exception as e:
    handle_error(e)
""",
            encoding="utf-8",
        )

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "try_except" in result["found_patterns"], "Result must not be empty"

    def test_null_check_pattern(self, tmp_path: Path):
        """Test detection of null checks."""
        test_file = tmp_path / "checks.py"
        test_file.write_text("if value is None:\n    return default\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "null_check" in result["found_patterns"], "Result must not be empty"

    def test_assertion_pattern(self, tmp_path: Path):
        """Test detection of assertions."""
        test_file = tmp_path / "assertions.py"
        test_file.write_text("assert value > 0, 'Value must be positive'\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "assertion" in result["found_patterns"], "Result must not be empty"

    def test_explicit_error_pattern(self, tmp_path: Path):
        """Test detection of explicit error raising."""
        test_file = tmp_path / "errors.py"
        test_file.write_text("raise ValueError('Invalid input')\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert "explicit_error" in result["found_patterns"], "Result must not be empty"


class TestFalsePositiveFiltering:
    """Test that false positives are minimized."""

    def test_no_safeguards_file(self, tmp_path: Path):
        """Test file with no safeguards returns empty evidence."""
        test_file = tmp_path / "simple.py"
        test_file.write_text("x = 1 + 2\nlogger.info(x)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert result["total_hits"] == 0, "Result must not be empty"
        assert len(result["evidence_files"]) == 0, "Collection must not be empty"

    def test_comments_vs_code(self, tmp_path: Path):
        """Test that safeguards in comments count."""
        test_file = tmp_path / "documented.py"
        test_file.write_text(
            "# This function validates input\ndef process(): pass\n", encoding="utf-8"
        )

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        # Should detect 'validates' from comment
        assert result["total_hits"] >= 1, "Value must be greater than zero"

    def test_file_type_filtering(self, tmp_path: Path):
        """Test that only allowed file types are scanned."""
        # Create binary file (not in allowed list)
        binary_file = tmp_path / "data.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([binary_file])
        result = module.detect(context_index)

        # Binary file should be skipped
        assert result["total_hits"] == 0, "Result must not be empty"


class TestMetricsCalculation:
    """Test metric calculation accuracy."""

    def test_density_calculation(self, tmp_path: Path):
        """Test safeguard density calculation."""
        # Create multiple files, some with safeguards
        files = []
        for i in range(5):
            f = tmp_path / f"file{i}.py"
            if i < 2:
                f.write_text("validate(input)\n", encoding="utf-8")
            else:
                f.write_text("x = 1\n", encoding="utf-8")
            files.append(f)

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for(files)
        result = module.detect(context_index)

        # 2 out of 5 files have safeguards
        assert result["metrics"]["files_with_safeguards"] == 2, "Result must not be empty"
        assert result["metrics"]["total_analyzed_files"] == 5, "Result must not be empty"
        assert 0.35 <= result["safeguard_density"] <= 0.45, "Result must not be empty"

    def test_multiple_safeguards_per_file(self, tmp_path: Path):
        """Test counting multiple safeguards in one file."""
        test_file = tmp_path / "secure.py"
        test_file.write_text(
            """
def secure_process(input):
    validate(input)
    sanitized = sanitize(input)
    try:
        result = process(sanitized, timeout=30)
    except (AssertionError, ValueError, TypeError, RuntimeError):  # noqa: BLE001
        rollback()
    return result
""",
            encoding="utf-8",
        )

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        # Should detect multiple keywords
        assert result["total_hits"] >= 5, "Value must be greater than zero"
        assert "validate" in result["found_patterns"], "Result must not be empty"
        assert "sanitize" in result["found_patterns"], "Result must not be empty"
        assert "timeout" in result["found_patterns"], "Result must not be empty"
        assert "rollback" in result["found_patterns"], "Result must not be empty"

    def test_average_safeguards_per_file(self, tmp_path: Path):
        """Test average safeguards per file calculation."""
        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.py"
            f.write_text("validate(x)\nsanitize(y)\n", encoding="utf-8")
            files.append(f)

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for(files)
        result = module.detect(context_index)

        # Each file has 2 keywords, average should be ~2
        avg = result["metrics"]["average_safeguards_per_file"]
        assert 1.5 <= avg <= 2.5, "5 is not valid"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file_list(self):
        """Test with no files."""
        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = {"files": []}
        result = module.detect(context_index)

        assert result["total_hits"] == 0, "Result must not be empty"
        assert result["unique_files"] == 0, "Result must not be empty"
        assert result["safeguard_density"] == 0.0, "Result must not be empty"

    def test_large_file_bounded_read(self, tmp_path: Path):
        """Test that large files are read with bounds."""
        test_file = tmp_path / "large.py"
        # Create file larger than MAX_READ_BYTES
        large_content = "# validate\n" * 50000  # Should exceed MAX_READ_BYTES
        test_file.write_text(large_content, encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        # Should still detect safeguards (in bounded portion)
        assert result["total_hits"] >= 1, "Value must be greater than zero"

    def test_unicode_handling(self, tmp_path: Path):
        """Test handling of unicode characters."""
        test_file = tmp_path / "unicode.py"
        test_file.write_text("# 验证 validation function\ndef validate(): pass\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        # Should detect English keyword
        assert "validation" in result["found_patterns"], "Result must not be empty"


class TestDetectorContract:
    """Test detector contract compliance."""

    def test_required_fields_present(self, tmp_path: Path):
        """Test that all required detector fields are present."""
        test_file = tmp_path / "test.py"
        test_file.write_text("validate(x)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        # Check required fields
        assert "id" in result, "Result must not be empty"
        assert result["id"] == "safeguards_keywords", "Result must not be empty"
        assert "evidence_files" in result, "Result must not be empty"
        assert "found_patterns" in result, "Result must not be empty"
        assert "required_patterns" in result, "Result must not be empty"
        assert "docs_keywords" in result, "Result must not be empty"
        assert "meta" in result, "Result must not be empty"

    def test_metadata_correctness(self, tmp_path: Path):
        """Test metadata fields are correct."""
        test_file = tmp_path / "test.py"
        test_file.write_text("validate(x)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        assert result["meta"]["detection_method"] == "keyword_and_pattern", "Result must not be empty"
        assert result["meta"]["context_aware"] is True, "Result must not be empty"
        assert result["meta"]["deterministic"] is True, "Result must not be empty"
        assert result["meta"]["offline"] is True, "Result must not be empty"

    def test_docs_keywords_present(self, tmp_path: Path):
        """Test that documentation keywords are provided."""
        test_file = tmp_path / "test.py"
        test_file.write_text("validate(x)\n", encoding="utf-8")

        detector_path = Path("scripts/space_traversal/detectors/detector_safeguards.py")
        module = _load_module(detector_path, "detector_safeguards")
        context_index = _context_index_for([test_file])
        result = module.detect(context_index)

        expected_keywords = ["safeguard", "validation", "security", "defensive", "robust"]
        for keyword in expected_keywords:
            assert keyword in result["docs_keywords"], "Result must not be empty"
