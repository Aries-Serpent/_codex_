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
            assert result["has_shebang"] is True
            assert result["valid_syntax"] is True
        finally:
            Path(temp_path).unlink()

    def test_python_file_without_shebang(self):
        """Test Python file without shebang flags missing shebang."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')\n")
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["has_shebang"] is False
        finally:
            Path(temp_path).unlink()

    def test_unbalanced_braces(self):
        """Test detection of unbalanced braces."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo():\n  x = { 'key': 'value'\n")  # Missing }
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["balanced_braces"] is False
        finally:
            Path(temp_path).unlink()

    def test_invalid_python_syntax(self):
        """Test invalid Python syntax is detected."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def broken_func(\n    print('oops')\n")  # Unclosed parenthesis
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["valid_syntax"] is False
        finally:
            Path(temp_path).unlink()

    def test_trailing_whitespace_detection(self):
        """Test detection of trailing whitespace."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("line1  \nline2\n")  # line1 has trailing spaces
            temp_path = f.name

        try:
            result = validate_file_structure(temp_path)
            assert result["no_trailing_whitespace"] is False
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file(self):
        """Test graceful handling of missing file."""
        result = validate_file_structure("/nonexistent/file.py")
        # Should return a dict with all checks marked as failed for missing file
        assert isinstance(result, dict)
        assert "has_shebang" in result
        assert "balanced_braces" in result
        assert "valid_syntax" in result
        assert result["has_shebang"] is False
        assert result["balanced_braces"] is False
        assert result["valid_syntax"] is False


class TestChecksumValidation:
    """Test checksum validation."""

    def test_checksum_computation(self):
        """Test SHA256 checksum computation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content\n")
            temp_path = f.name

        try:
            valid, sha = validate_with_checksum(temp_path)
            assert valid is True
            assert len(sha) == 64  # SHA256 is 64 hex characters
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
            assert valid is True
            assert sha == expected_sha
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
            assert valid is False
            expected_sha = hashlib.sha256(b"test content\n").hexdigest()
            assert _sha == expected_sha
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
            assert identical is True
            assert diff == ""
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
            assert identical is False
            assert "content1" in diff or "content2" in diff
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
            assert result["syntax_valid"] is True
        finally:
            Path(temp_path).unlink()

    def test_invalid_python_syntax(self):
        """Test invalid Python syntax is detected."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def foo(\n    return 42\n")  # Missing closing paren
            temp_path = f.name

        try:
            result = validate_code_quality(temp_path)
            assert result["syntax_valid"] is False
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
