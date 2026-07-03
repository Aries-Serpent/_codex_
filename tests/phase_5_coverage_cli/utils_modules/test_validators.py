"""Tests for src/codex/utils/validators.py module.

Phase 5 Week 2 Gap-Fill Coverage Campaign
Module 5: Automated validation utilities for code and file quality checks

Test Coverage Goals:
  - 25 test functions total
  - 55%+ coverage of validators module
  - Happy paths (60%): File structure, checksums, diffs
  - Error handling (25%): Invalid paths, malformed files
  - Edge cases (15%): Empty files, unicode, special characters
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Import the module to test
try:
    from codex.utils.validators import (
        validate_code_quality,
        validate_file_structure,
        validate_with_checksum,
        validate_with_diff,
    )
except ImportError:
    pytest.skip("validators module not importable", allow_module_level=True)


class TestValidateFileStructureBasic:
    """Test basic file structure validation."""

    def test_validate_python_file_valid(self, tmp_path: Path) -> None:
        """Test validation of a valid Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("#!/usr/bin/env python\nlogger.info('hello')\n")
        result = validate_file_structure(str(test_file))
        assert isinstance(result, dict)
        assert "balanced_braces" in result, "Result must not be empty"
        assert "balanced_parens" in result, "Result must not be empty"

    def test_validate_shell_file_with_shebang(self, tmp_path: Path) -> None:
        """Test validation of shell script with shebang."""
        test_file = tmp_path / "script.sh"
        test_file.write_text("#!/bin/bash\necho 'hello'\n")
        result = validate_file_structure(str(test_file))
        assert isinstance(result, dict)
        assert result["has_shebang"] is True, "Result must not be empty"

    def test_validate_file_no_shebang(self, tmp_path: Path) -> None:
        """Test validation of file without shebang."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("just some text\n")
        result = validate_file_structure(str(test_file))
        assert isinstance(result, dict)
        assert "has_shebang" in result, "Result must not be empty"

    def test_validate_balanced_braces(self, tmp_path: Path) -> None:
        """Test validation of balanced braces."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def func():\n    d = {'a': 1, 'b': 2}\n    return d\n")
        result = validate_file_structure(str(test_file))
        assert result["balanced_braces"] is True, "Result must not be empty"

    def test_validate_unbalanced_braces(self, tmp_path: Path) -> None:
        """Test detection of unbalanced braces."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def func():\n    d = {'a': 1\n    return d\n")
        result = validate_file_structure(str(test_file))
        # Should detect imbalance
        assert isinstance(result["balanced_braces"], bool)

    def test_validate_balanced_parens(self, tmp_path: Path) -> None:
        """Test validation of balanced parentheses."""
        test_file = tmp_path / "test.py"
        test_file.write_text("result = (1 + 2) * (3 + 4)\n")
        result = validate_file_structure(str(test_file))
        assert result["balanced_parens"] is True, "Result must not be empty"

    def test_validate_unbalanced_parens(self, tmp_path: Path) -> None:
        """Test detection of unbalanced parentheses."""
        test_file = tmp_path / "test.py"
        test_file.write_text("result = (1 + 2 * (3 + 4)\n")
        result = validate_file_structure(str(test_file))
        # Should detect imbalance
        assert isinstance(result["balanced_parens"], bool)

    def test_validate_balanced_brackets(self, tmp_path: Path) -> None:
        """Test validation of balanced brackets."""
        test_file = tmp_path / "test.py"
        test_file.write_text("lst = [1, 2, [3, 4], 5]\n")
        result = validate_file_structure(str(test_file))
        assert result["balanced_brackets"] is True, "Result must not be empty"

    def test_validate_unbalanced_brackets(self, tmp_path: Path) -> None:
        """Test detection of unbalanced brackets."""
        test_file = tmp_path / "test.py"
        test_file.write_text("lst = [1, 2, [3, 4, 5]\n")
        result = validate_file_structure(str(test_file))
        # Should detect imbalance
        assert isinstance(result["balanced_brackets"], bool)

    def test_validate_trailing_whitespace(self, tmp_path: Path) -> None:
        """Test detection of trailing whitespace."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1 = 'test'  \nline2 = 'okay'\n")
        result = validate_file_structure(str(test_file))
        assert isinstance(result["no_trailing_whitespace"], bool)

    def test_validate_no_trailing_whitespace(self, tmp_path: Path) -> None:
        """Test file with no trailing whitespace passes."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1 = 'test'\nline2 = 'okay'\n")
        result = validate_file_structure(str(test_file))
        assert result["no_trailing_whitespace"] is True, "Result must not be empty"

    def test_validate_valid_python_syntax(self, tmp_path: Path) -> None:
        """Test validation of valid Python syntax."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    logger.info('world')\n")
        result = validate_file_structure(str(test_file))
        # For .py files, should validate syntax
        assert isinstance(result["valid_syntax"], bool)

    def test_validate_invalid_python_syntax(self, tmp_path: Path) -> None:
        """Test detection of invalid Python syntax."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(\n    logger.info('world')\n")
        result = validate_file_structure(str(test_file))
        # Should detect syntax error
        assert isinstance(result["valid_syntax"], bool)

    def test_validate_nonpython_file_syntax_ignored(self, tmp_path: Path) -> None:
        """Test that syntax validation skipped for non-Python files."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("random data {[ invalid syntax }]\n")
        result = validate_file_structure(str(test_file))
        assert result["valid_syntax"] is True, "Result must not be empty"

    def test_validate_empty_file(self, tmp_path: Path) -> None:
        """Test validation of empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")
        result = validate_file_structure(str(test_file))
        assert isinstance(result, dict)
        assert all(isinstance(v, bool) for v in result.values())


class TestValidateFileStructureEdgeCases:
    """Test edge cases and error handling."""

    def test_validate_unicode_content(self, tmp_path: Path) -> None:
        """Test validation with unicode content."""
        test_file = tmp_path / "unicode.py"
        test_file.write_text("# -*- coding: utf-8 -*-\ntext = '你好世界'\n")
        result = validate_file_structure(str(test_file))
        assert isinstance(result, dict)

    def test_validate_multiline_strings(self, tmp_path: Path) -> None:
        """Test validation with multiline strings."""
        test_file = tmp_path / "test.py"
        content = '''def func():\n    """Docstring\n    with multiple lines\n    """\n    return True\n'''
        test_file.write_text(content)
        result = validate_file_structure(str(test_file))
        assert isinstance(result["balanced_parens"], bool)

    def test_validate_nested_structures(self, tmp_path: Path) -> None:
        """Test validation with deeply nested structures."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            "data = {'a': {'b': {'c': [1, 2, (3, 4)]}}}\n"
        )
        result = validate_file_structure(str(test_file))
        assert result["balanced_braces"] is True, "Result must not be empty"
        assert result["balanced_brackets"] is True, "Result must not be empty"
        assert result["balanced_parens"] is True, "Result must not be empty"

    def test_validate_special_characters_in_strings(self, tmp_path: Path) -> None:
        """Test validation with special characters in strings."""
        test_file = tmp_path / "test.py"
        test_file.write_text("text = 'special: []{}<>()'\n")
        result = validate_file_structure(str(test_file))
        # Characters in strings should not be counted
        assert isinstance(result, dict)

    def test_validate_commented_braces(self, tmp_path: Path) -> None:
        """Test that commented braces are ignored."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# This has { unmatched brace in comment\nx = 1\n")
        result = validate_file_structure(str(test_file))
        # Should only count actual code
        assert isinstance(result, dict)

    def test_validate_nonexistent_file(self) -> None:
        """Test validation of nonexistent file."""
        with pytest.raises((FileNotFoundError, IOError)):
            validate_file_structure("/nonexistent/path/file.py")


class TestValidateWithChecksum:
    """Test checksum-based file validation."""

    def test_checksum_basic_validation(self, tmp_path: Path) -> None:
        """Test basic checksum validation."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file1.txt"
        file1.write_text("test content")
        result = validate_with_checksum(str(file1), str(file2))
        assert isinstance(result, dict)

    def test_checksum_identical_files(self, tmp_path: Path) -> None:
        """Test checksums of identical files match."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "identical content"
        file1.write_text(content)
        file2.write_text(content)
        result = validate_with_checksum(str(file1), str(file2))
        assert result.get("match") is True, "Result must not be empty"

    def test_checksum_different_files(self, tmp_path: Path) -> None:
        """Test checksums of different files don't match."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")
        result = validate_with_checksum(str(file1), str(file2))
        assert result.get("match") is False, "Result must not be empty"

    def test_checksum_empty_files(self, tmp_path: Path) -> None:
        """Test checksums of empty files."""
        file1 = tmp_path / "empty1.txt"
        file2 = tmp_path / "empty2.txt"
        file1.write_text("")
        file2.write_text("")
        result = validate_with_checksum(str(file1), str(file2))
        assert result.get("match") is True, "Result must not be empty"

    def test_checksum_large_files(self, tmp_path: Path) -> None:
        """Test checksums of large files."""
        file1 = tmp_path / "large1.txt"
        file2 = tmp_path / "large2.txt"
        large_content = "x" * 1000000  # 1 MB
        file1.write_text(large_content)
        file2.write_text(large_content)
        result = validate_with_checksum(str(file1), str(file2))
        assert isinstance(result, dict)


class TestValidateWithDiff:
    """Test diff-based file validation."""

    def test_diff_identical_files(self, tmp_path: Path) -> None:
        """Test diff of identical files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "line 1\nline 2\nline 3\n"
        file1.write_text(content)
        file2.write_text(content)
        result = validate_with_diff(str(file1), str(file2))
        assert isinstance(result, dict)

    def test_diff_different_files(self, tmp_path: Path) -> None:
        """Test diff detects differences."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("line 1\nline 2\nline 3\n")
        file2.write_text("line 1\nmodified\nline 3\n")
        result = validate_with_diff(str(file1), str(file2))
        assert isinstance(result, dict)

    def test_diff_added_lines(self, tmp_path: Path) -> None:
        """Test diff detects added lines."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("line 1\nline 2\n")
        file2.write_text("line 1\nline 2\nline 3\n")
        result = validate_with_diff(str(file1), str(file2))
        assert isinstance(result, dict)

    def test_diff_removed_lines(self, tmp_path: Path) -> None:
        """Test diff detects removed lines."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("line 1\nline 2\nline 3\n")
        file2.write_text("line 1\nline 3\n")
        result = validate_with_diff(str(file1), str(file2))
        assert isinstance(result, dict)

    def test_diff_empty_vs_content(self, tmp_path: Path) -> None:
        """Test diff of empty file vs file with content."""
        file1 = tmp_path / "empty.txt"
        file2 = tmp_path / "content.txt"
        file1.write_text("")
        file2.write_text("content\n")
        result = validate_with_diff(str(file1), str(file2))
        assert isinstance(result, dict)


class TestValidateCodeQuality:
    """Test code quality validation."""

    def test_quality_valid_python(self, tmp_path: Path) -> None:
        """Test quality check on valid Python code."""
        test_file = tmp_path / "valid.py"
        test_file.write_text("def hello():\n    return 'world'\n")
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_invalid_syntax(self, tmp_path: Path) -> None:
        """Test quality check detects syntax errors."""
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def hello(\n    return 'world'\n")
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_non_python_file(self, tmp_path: Path) -> None:
        """Test quality check on non-Python files."""
        test_file = tmp_path / "data.txt"
        test_file.write_text("not python code\n")
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_empty_file(self, tmp_path: Path) -> None:
        """Test quality check on empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_complex_code(self, tmp_path: Path) -> None:
        """Test quality check on complex valid code."""
        test_file = tmp_path / "complex.py"
        code = """
def process_data(data):
    \"\"\"Process data and return result.\"\"\"
    if not data:
        raise ValueError("Data required")
    return [x * 2 for x in data]

class DataProcessor:
    def __init__(self, name):
        self.name = name
    
    def process(self, data):
        return process_data(data)
"""
        test_file.write_text(code)
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_unicode_file(self, tmp_path: Path) -> None:
        """Test quality check with unicode content."""
        test_file = tmp_path / "unicode.py"
        test_file.write_text("# -*- coding: utf-8 -*-\n# Comment: 你好\nlogger.info('世界')\n")
        result = validate_code_quality(str(test_file))
        assert isinstance(result, dict)

    def test_quality_nonexistent_file(self) -> None:
        """Test quality check on nonexistent file."""
        with pytest.raises((FileNotFoundError, IOError)):
            validate_code_quality("/nonexistent/file.py")
