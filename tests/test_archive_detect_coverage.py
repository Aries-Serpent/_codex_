"""
Comprehensive tests for codex.archive.detect module.

Tests cover file detection, MIME type detection, language detection,
and source lines of code (SLoC) counting.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from codex.archive.detect import (
    FileMeta,
    _sloc_of_bytes,
    detect_mime_lang,
    stat_file,
)


class TestFileMeta:
    """Test FileMeta dataclass."""

    def test_file_meta_creation(self):
        """Test creating FileMeta instance."""
        meta = FileMeta(
            path="/path/to/file.py",
            size_bytes=1024,
            mtime_epoch=1234567890.0,
            mime="text/x-python",
            lang="python",
            sloc=100,
        )
        assert meta.path == "/path/to/file.py", "path is not valid"
        assert meta.size_bytes == 1024, "size_bytes is not valid"
        assert meta.mtime_epoch == 1234567890.0, "mtime_epoch is not valid"
        assert meta.mime == "text/x-python", "mime is not valid"
        assert meta.lang == "python", "lang is not valid"
        assert meta.sloc == 100, "sloc is not valid"

    def test_file_meta_zero_size(self):
        """Test FileMeta with zero size."""
        meta = FileMeta(
            path="empty.txt",
            size_bytes=0,
            mtime_epoch=0.0,
            mime="text/plain",
            lang="text",
            sloc=0,
        )
        assert meta.size_bytes == 0, "size_bytes is not valid"

    def test_file_meta_large_file(self):
        """Test FileMeta with large file size."""
        meta = FileMeta(
            path="large.bin",
            size_bytes=1024 * 1024 * 1024,  # 1GB
            mtime_epoch=time.time(),
            mime="application/octet-stream",
            lang="binary",
            sloc=0,
        )
        assert meta.size_bytes == 1024 * 1024 * 1024, "size_bytes is not valid"

    def test_file_meta_high_sloc(self):
        """Test FileMeta with high SLoC count."""
        meta = FileMeta(
            path="huge.py",
            size_bytes=1000000,
            mtime_epoch=time.time(),
            mime="text/x-python",
            lang="python",
            sloc=100000,
        )
        assert meta.sloc == 100000, "sloc is not valid"


class TestSlocOfBytes:
    """Test _sloc_of_bytes function."""

    def test_sloc_of_bytes_empty(self):
        """Test SLoC counting for empty content."""
        result = _sloc_of_bytes(b"")
        assert result == 0, "Result must not be empty"

    def test_sloc_of_bytes_single_line(self):
        """Test SLoC counting for single line."""
        result = _sloc_of_bytes(b"print('hello')")
        assert result == 1, "Result must not be empty"

    def test_sloc_of_bytes_multiple_lines(self):
        """Test SLoC counting for multiple lines."""
        content = b"def hello():\n    print('world')\n    return 42"
        result = _sloc_of_bytes(content)
        assert result == 3, "Result must not be empty"

    def test_sloc_of_bytes_ignores_comments(self):
        """Test that comment lines are ignored."""
        content = b"# This is a comment\nprint('code')\n# Another comment"
        result = _sloc_of_bytes(content)
        assert result == 1, "Result must not be empty"

    def test_sloc_of_bytes_ignores_empty_lines(self):
        """Test that empty lines are ignored."""
        content = b"line1\n\n\nline2\n\nline3"
        result = _sloc_of_bytes(content)
        assert result == 3, "Result must not be empty"

    def test_sloc_of_bytes_whitespace_only_ignored(self):
        """Test that whitespace-only lines are ignored."""
        content = b"line1\n   \n\t\nline2"
        result = _sloc_of_bytes(content)
        assert result == 2, "Result must not be empty"

    def test_sloc_of_bytes_double_slash_comments(self):
        """Test that double-slash comments are ignored."""
        content = b"// Comment\nvar x = 5;\n// Another"
        result = _sloc_of_bytes(content)
        assert result == 1, "Result must not be empty"

    def test_sloc_of_bytes_mixed_comments(self):
        """Test with mixed hash and double-slash comments."""
        content = b"# Python comment\nprint('hi')\n// JS comment\nvar x = 1"
        result = _sloc_of_bytes(content)
        assert result == 2, "Result must not be empty"

    def test_sloc_of_bytes_unicode_content(self):
        """Test SLoC with unicode content."""
        content = "# 中文注释\nprint('世界')".encode("utf-8")
        result = _sloc_of_bytes(content)
        assert result == 1, "Result must not be empty"

    def test_sloc_of_bytes_invalid_utf8(self):
        """Test SLoC with invalid UTF-8 (uses ignore)."""
        content = b"valid\xff\xfeinvalid"
        result = _sloc_of_bytes(content)
        assert result == 1, "Result must not be empty"

    def test_sloc_of_bytes_large_content(self):
        """Test SLoC counting on large content."""
        # Create 1000 lines
        content = b"\n".join([b"line " + str(i).encode() for i in range(1000)])
        result = _sloc_of_bytes(content)
        assert result == 1000, "Result must not be empty"

    def test_sloc_of_bytes_code_with_comments(self):
        """Test realistic code with comments."""
        content = b"""# Function definition
def calculate(x, y):
    # Add two numbers
    # This is a description
    return x + y

# Main code
result = calculate(5, 3)
"""
        result = _sloc_of_bytes(content)
        # count: def, return, result = calculate
        assert result == 3, "Result must not be empty"

    def test_sloc_of_bytes_only_comments(self):
        """Test content with only comments."""
        content = b"# Comment 1\n# Comment 2\n# Comment 3"
        result = _sloc_of_bytes(content)
        assert result == 0, "Result must not be empty"

    def test_sloc_of_bytes_only_empty_lines(self):
        """Test content with only empty lines."""
        content = b"\n\n\n   \n\t\n"
        result = _sloc_of_bytes(content)
        assert result == 0, "Result must not be empty"


class TestDetectMimeLang:
    """Test detect_mime_lang function."""

    def test_detect_mime_lang_python(self):
        """Test MIME/lang detection for Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            path.write_text("code")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/x-python", "mime is not valid"
            assert lang == "python", "lang is not valid"

    def test_detect_mime_lang_markdown(self):
        """Test MIME/lang detection for Markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "readme.md"
            path.write_text("# Title")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/markdown", "mime is not valid"
            assert lang == "markdown", "lang is not valid"

    def test_detect_mime_lang_json(self):
        """Test MIME/lang detection for JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text("{}")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/json", "mime is not valid"
            assert lang == "json", "lang is not valid"

    def test_detect_mime_lang_yaml(self):
        """Test MIME/lang detection for YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            path.write_text("key: value")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/yaml", "mime is not valid"
            assert lang == "yaml", "lang is not valid"

    def test_detect_mime_lang_yml_alias(self):
        """Test MIME/lang detection for .yml extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yml"
            path.write_text("key: value")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/yaml", "mime is not valid"
            assert lang == "yaml", "lang is not valid"

    def test_detect_mime_lang_javascript(self):
        """Test MIME/lang detection for JavaScript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "script.js"
            path.write_text("console.log('hi')")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/javascript", "mime is not valid"
            assert lang == "javascript", "lang is not valid"

    def test_detect_mime_lang_typescript(self):
        """Test MIME/lang detection for TypeScript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "script.ts"
            path.write_text("function hi(): void {}")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/typescript", "mime is not valid"
            assert lang == "typescript", "lang is not valid"

    def test_detect_mime_lang_shell(self):
        """Test MIME/lang detection for Shell script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "script.sh"
            path.write_text("#!/bin/bash")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/x-shellscript", "mime is not valid"
            assert lang == "shell", "lang is not valid"

    def test_detect_mime_lang_csv(self):
        """Test MIME/lang detection for CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.csv"
            path.write_text("a,b,c")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/csv", "mime is not valid"
            assert lang == "csv", "lang is not valid"

    def test_detect_mime_lang_sql(self):
        """Test MIME/lang detection for SQL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "query.sql"
            path.write_text("SELECT * FROM users")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/sql", "mime is not valid"
            assert lang == "sql", "lang is not valid"

    def test_detect_mime_lang_txt(self):
        """Test MIME/lang detection for text file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "readme.txt"
            path.write_text("Text content")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/plain", "mime is not valid"
            assert lang == "text", "lang is not valid"

    def test_detect_mime_lang_unknown_extension(self):
        """Test MIME/lang detection for unknown extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "file.xyz"
            path.write_text("content")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/octet-stream", "mime is not valid"
            assert lang == "binary", "lang is not valid"

    def test_detect_mime_lang_no_extension(self):
        """Test MIME/lang detection for file without extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "Makefile"
            path.write_text("all:")
            mime, lang = detect_mime_lang(path)
            assert mime == "application/octet-stream", "mime is not valid"
            assert lang == "binary", "lang is not valid"

    def test_detect_mime_lang_case_insensitive(self):
        """Test MIME/lang detection is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.PY"
            path.write_text("code")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/x-python", "mime is not valid"
            assert lang == "python", "lang is not valid"

    def test_detect_mime_lang_uppercase_yaml(self):
        """Test MIME/lang detection for uppercase YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.YAML"
            path.write_text("key: value")
            mime, lang = detect_mime_lang(path)
            assert mime == "text/yaml", "mime is not valid"
            assert lang == "yaml", "lang is not valid"


class TestStatFile:
    """Test stat_file function."""

    def test_stat_file_basic(self):
        """Test basic file stat functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            content = "print('hello')"
            path.write_text(content)

            result = stat_file(path)

            assert result.path == path.as_posix(), "Result must not be empty"
            assert result.size_bytes == len(content.encode()), "Size_bytes must not be empty"
            assert result.mime == "text/x-python", "Result must not be empty"
            assert result.lang == "python", "Result must not be empty"
            assert result.sloc == 1, "Result must not be empty"

    def test_stat_file_empty(self):
        """Test stat_file on empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.txt"
            path.write_text("")

            result = stat_file(path)

            assert result.size_bytes == 0, "Result must not be empty"
            assert result.sloc == 0, "Result must not be empty"
            assert result.mime == "text/plain", "Result must not be empty"

    def test_stat_file_multiline(self):
        """Test stat_file on multiline file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            content = "def hello():\n    print('world')\n    return 42"
            path.write_text(content)

            result = stat_file(path)

            assert result.size_bytes == len(content.encode()), "Size_bytes must not be empty"
            assert result.sloc == 3, "Result must not be empty"
            assert result.lang == "python", "Result must not be empty"

    def test_stat_file_with_comments(self):
        """Test stat_file with comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            content = "# Comment\ncode = 1\n# Comment 2"
            path.write_text(content)

            result = stat_file(path)

            assert result.sloc == 1, "Result must not be empty"

    def test_stat_file_mtime_populated(self):
        """Test that mtime is populated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("content")

            result = stat_file(path)

            assert result.mtime_epoch > 0, "mtime_epoch must be greater than zero"
            assert result.mtime_epoch <= time.time(), "Result must not be empty"

    def test_stat_file_path_posix_format(self):
        """Test that path is in POSIX format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("content")

            result = stat_file(path)

            assert "/" in result.path or result.path.startswith("test.txt"), "Result must not be empty"

    def test_stat_file_size_accuracy(self):
        """Test that size matches actual file size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.bin"
            content = b"0123456789" * 10  # 100 bytes
            path.write_bytes(content)

            result = stat_file(path)

            assert result.size_bytes == 100, "Result must not be empty"

    def test_stat_file_binary_file(self):
        """Test stat_file on binary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.bin"
            path.write_bytes(b"\x00\x01\x02\x03")

            result = stat_file(path)

            assert result.size_bytes == 4, "Result must not be empty"
            assert result.mime == "application/octet-stream", "Result must not be empty"
            assert result.lang == "binary", "Result must not be empty"

    def test_stat_file_permission_error_handled(self):
        """Test that permission errors are handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("content")

            with patch("pathlib.Path.read_bytes", side_effect=PermissionError):
                # Should not raise, just return 0 sloc
                result = stat_file(path)
                assert result.sloc == 0, "Result must not be empty"

    def test_stat_file_nonexistent_raises(self):
        """Test that stat_file raises on nonexistent file."""
        nonexistent = Path("/nonexistent/file.txt")
        with pytest.raises(FileNotFoundError):
            stat_file(nonexistent)

    def test_stat_file_unicode_content(self):
        """Test stat_file with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "unicode.py"
            content = "# 中文注释\nprint('你好')"
            path.write_text(content, encoding="utf-8")

            result = stat_file(path)

            # Should handle unicode correctly
            assert result.size_bytes > 0, "size_bytes must be greater than zero"
            assert result.sloc == 1, "Result must not be empty"


class TestDetectIntegration:
    """Integration tests for detection module."""

    def test_stat_file_all_supported_types(self):
        """Test stat_file on all supported file types."""
        supported_extensions = [
            ".py",
            ".md",
            ".txt",
            ".json",
            ".csv",
            ".yml",
            ".yaml",
            ".sql",
            ".js",
            ".ts",
            ".sh",
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            for ext in supported_extensions:
                path = Path(tmpdir) / f"test{ext}"
                path.write_text("content")

                result = stat_file(path)

                assert result.path is not None, "path must be initialized"
                assert result.mime != "application/octet-stream" or ext == ".unknown", "Result must not be empty"
                assert result.lang != "binary" or ext == ".unknown", "Result must not be empty"

    def test_detect_multiple_files_in_directory(self):
        """Test detecting multiple files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            files = ["test.py", "readme.md", "config.json"]

            for filename in files:
                (tmppath / filename).write_text("content")

            results = []
            for filename in files:
                result = stat_file(tmppath / filename)
                results.append(result)

            assert len(results) == 3, "Results must not be empty"
            assert all(r.size_bytes > 0 for r in results), "size_bytes must be greater than zero"

    def test_stat_file_consistency(self):
        """Test that stat_file is consistent for same file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.py"
            path.write_text("code = 1")

            result1 = stat_file(path)
            result2 = stat_file(path)

            assert result1.path == result2.path, "Result must not be empty"
            assert result1.size_bytes == result2.size_bytes, "Result must not be empty"
            assert result1.mime == result2.mime, "Result must not be empty"
            assert result1.lang == result2.lang, "Result must not be empty"
            assert result1.sloc == result2.sloc, "Result must not be empty"
