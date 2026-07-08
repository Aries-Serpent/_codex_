"""
Unit tests for validation utilities.

Tests cover:
  - File structure validation (shebangs, balanced braces, syntax)
  - Checksum validation (SHA256 comparison)
  - Diff comparison (file differences)
  - Code quality checks (syntax, linting)
"""

import hashlib
import tempfile
from pathlib import Path

import pytest

from codex.utils.validators import (
    validate_code_quality,
    validate_file_structure,
    validate_with_checksum,
    validate_with_diff,
)


class TestFileStructureValidation:
    """Test file structure validation."""

    def test_python_file_with_shebang(self):
        """Test Python file with shebang passes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("#!/usr/bin/env python3\nprint('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is True, "Result must not be empty"
            assert result["valid_syntax"] is True, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_python_file_without_shebang(self):
        """Test Python file without shebang flags missing shebang."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_unbalanced_braces(self):
        """Test detection of unbalanced braces."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo():\n  x = { 'key': 'value'\n")  # Missing }
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_braces"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_invalid_python_syntax(self):
        """Test invalid Python syntax is detected."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def broken_func(\n    print('oops')\n")  # Unclosed parenthesis
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["valid_syntax"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_trailing_whitespace_detection(self):
        """Test detection of trailing whitespace."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("line1  \nline2\n")  # line1 has trailing spaces
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["no_trailing_whitespace"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file(self):
        """Test graceful handling of missing file."""
        result = validate_file_structure("/nonexistent/file.py")
        # Should return a dict with all checks marked as failed for missing file
        assert isinstance(result, dict)
        assert "has_shebang" in result, "Result must not be empty"
        assert "balanced_braces" in result, "Result must not be empty"
        assert "valid_syntax" in result, "Result must not be empty"
        assert result["has_shebang"] is False, "Result must not be empty"
        assert result["balanced_braces"] is False, "Result must not be empty"
        assert result["valid_syntax"] is False, "Result must not be empty"


class TestChecksumValidation:
    """Test checksum validation."""

    def test_checksum_computation(self):
        """Test SHA256 checksum computation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content\n")
            temp_path = f.name

        try:
            valid, sha = validate_with_checksum(temp_path)
            assert valid is True, "valid is not valid"
            assert len(sha) == 64, "Sha must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_checksum_match(self):
        """Test checksum matching."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content\n")
            temp_path = f.name

        try:
            _, expected_sha = validate_with_checksum(temp_path)
            valid, sha = validate_with_checksum(temp_path, expected_sha)
            assert valid is True, "valid is not valid"
            assert sha == expected_sha, "sha is not valid"
        finally:
            Path(temp_path).unlink()

    def test_checksum_mismatch(self):
        """Test checksum mismatch detection."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content\n")
            temp_path = f.name

        try:
            wrong_sha = "0" * 64
            valid, _sha = validate_with_checksum(temp_path, wrong_sha)
            assert valid is False, "valid is not valid"
            expected_sha = hashlib.sha256(b"test content\n").hexdigest()
            assert _sha == expected_sha, "_sha is not valid"
        finally:
            Path(temp_path).unlink()


class TestDiffValidation:
    """Test diff validation."""

    def test_identical_files(self):
        """Test identical files pass validation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
                f1.write("same content\n")
                f2.write("same content\n")
                path1 = f1.name
                path2 = f2.name

        try:
            identical, diff = validate_with_diff(path1, path2)
            assert identical is True, "identical is not valid"
            assert diff == "", "diff is not valid"
        finally:
            Path(path1).unlink()
            Path(path2).unlink()

    def test_different_files(self):
        """Test different files are detected."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
                f1.write("content1\n")
                f2.write("content2\n")
                path1 = f1.name
                path2 = f2.name

        try:
            identical, diff = validate_with_diff(path1, path2)
            assert identical is False, "identical is not valid"
            assert "content1" in diff or "content2" in diff, "Content must not be empty"
        finally:
            Path(path1).unlink()
            Path(path2).unlink()


class TestCodeQualityValidation:
    """Test code quality validation."""

    def test_valid_python_syntax(self):
        """Test valid Python syntax passes."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo():\n    return 42\n")
            temp_path = f.name

        try:
            result = validate_code_quality(temp_path)
            assert result["syntax_valid"] is True, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_invalid_python_syntax(self):
        """Test invalid Python syntax is detected."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(\n    return 42\n")  # Missing closing paren
            temp_path = f.name

        try:
            result = validate_code_quality(temp_path)
            assert result["syntax_valid"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()


# ============================================================================
# MUTATION KILLING TESTS - DAY 2 REFINEMENT
# ============================================================================


class TestValidatorsBoundaryConditions:
    """Boundary condition tests to kill comparison operator mutations."""

    def test_exact_brace_count_equality(self):
        """Kill: 'open_braces != close_braces' mutations.

        Ensures validator requires exact equality.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo():\n    d = {'a': 1}\n    return d\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_braces"] is True, "Result must not be empty"
            content = Path(temp_path).read_text()
            assert content.count("{") == content.count("}"), "Content must not be empty"
        finally:
            Path(temp_path).unlink()

    def test_off_by_one_brace_detection(self):
        """Kill: off-by-one mutations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = {1, 2, 3\n")  # Missing close brace
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_braces"] is False, "Result must not be empty"
        finally:
            Path(temp_path).unlink()


class TestValidatorsExactValues:
    """Tests to verify exact values and kill return value mutations."""

    def test_valid_structure_returns_all_true(self):
        """Kill: return value mutations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("def foo():\n")
            f.write("    x = {'a': 1}\n")
            f.write("    return x\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is True, "Result must not be empty"
            assert result["balanced_braces"] is True, "Result must not be empty"
            assert result["balanced_parens"] is True, "Result must not be empty"
            assert result["balanced_brackets"] is True, "Result must not be empty"
            assert result["no_trailing_whitespace"] is True, "Result must not be empty"
            assert result["valid_syntax"] is True, "Result must not be empty"
        finally:
            Path(temp_path).unlink()


# ============================================================================
# MUTATION-KILLING TESTS FOR VALIDATORS
# ============================================================================
# Tests specifically designed to kill surviving mutations from Day 2


class TestValidatorsBoundaryMutations:
    """Kill boundary mutations (!=, ==, etc)."""

    def test_balanced_braces_exact_equality(self):
        """Kill: != vs == mutation in brace counting.

        If code has: if open_braces != close_braces: issues['balanced_braces'] = False
        Mutation would change != to ==
        """
        # Test UNBALANCED braces (1 open, 0 close)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = {\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            # MUST detect unbalanced braces
            assert result["balanced_braces"] is False, "MUST detect unbalanced braces"
        finally:
            Path(temp_path).unlink()

        # Test BALANCED braces (1 open, 1 close)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = {1}\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            # MUST detect balanced braces
            assert result["balanced_braces"] is True, "MUST detect balanced braces"
        finally:
            Path(temp_path).unlink()

    def test_balanced_parens_exact_equality(self):
        """Kill: != vs == mutation in paren counting."""
        # Unbalanced
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(a, b:\n    pass\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_parens"] is False, "MUST detect unbalanced parens"
        finally:
            Path(temp_path).unlink()

        # Balanced
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(a, b):\n    pass\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_parens"] is True, "MUST detect balanced parens"
        finally:
            Path(temp_path).unlink()

    def test_balanced_brackets_exact_equality(self):
        """Kill: != vs == mutation in bracket counting."""
        # Unbalanced
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = [1, 2\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_brackets"] is False, "MUST detect unbalanced brackets"
        finally:
            Path(temp_path).unlink()

        # Balanced
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = [1, 2]\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_brackets"] is True, "MUST detect balanced brackets"
        finally:
            Path(temp_path).unlink()


class TestValidatorsReturnValueMutations:
    """Kill return value mutations."""

    def test_validate_structure_returns_dict_with_exact_keys(self):
        """Kill: Return dict key mutations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("#!/usr/bin/env python3\nprint('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)

            # Exact dict structure verification
            assert isinstance(result, dict), "MUST return dict"
            expected_keys = {
                "has_shebang",
                "balanced_braces",
                "balanced_parens",
                "balanced_brackets",
                "no_trailing_whitespace",
                "valid_syntax",
            }
            assert set(result.keys()) == expected_keys, "MUST have exact keys"

            # All values must be boolean
            for key, value in result.items():
                assert isinstance(value, bool), f"Key {key} MUST be bool, got {type(value)}"
        finally:
            Path(temp_path).unlink()

    def test_shebang_detection_exact_bool(self):
        """Kill: Shebang detection return mutations."""
        # With shebang
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("#!/usr/bin/env python3\nprint('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is True, "MUST detect shebang"
            assert type(result["has_shebang"]) is bool, "Result must not be empty"
        finally:
            Path(temp_path).unlink()

        # Without shebang
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is False, "MUST NOT detect shebang"
            assert type(result["has_shebang"]) is bool, "Result must not be empty"
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
