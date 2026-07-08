"""
Tests for codex.archive.detect module.

This module contains tests for file detection utilities.
"""
import pytest
        from codex.archive.detect import FileMeta
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _sloc_of_bytes
        from codex.archive.detect import _EXT_TO_MIME
        from codex.archive.detect import _EXT_TO_MIME
        from codex.archive.detect import _EXT_TO_LANG
        from codex.archive.detect import _EXT_TO_LANG
        from codex.archive.detect import logger


class TestFileMeta:
    """Tests for FileMeta dataclass."""

    def test_basic_creation(self):
        """Test FileMeta basic creation."""

        meta = FileMeta(
            path="/path/to/file.py",
            size_bytes=1024,
            mtime_epoch=1640000000.0,
            mime="text/x-python",
            lang="python",
            sloc=50,
        )

        assert meta.path == "/path/to/file.py", "path is not valid"
        assert meta.size_bytes == 1024, "size_bytes is not valid"
        assert meta.mtime_epoch == 1640000000.0, "mtime_epoch is not valid"
        assert meta.mime == "text/x-python", "mime is not valid"
        assert meta.lang == "python", "lang is not valid"
        assert meta.sloc == 50, "sloc is not valid"


class TestSlocOfBytes:
    """Tests for _sloc_of_bytes function."""

    def test_simple_code(self):
        """Test SLOC counting for simple code."""

        code = b"def foo():\n    return 1\n\nlogger.info(foo())"

        result = _sloc_of_bytes(code)

        assert result == 3, "Result must not be empty"

    def test_empty_bytes(self):
        """Test SLOC counting for empty input."""

        result = _sloc_of_bytes(b"")

        assert result == 0, "Result must not be empty"

    def test_only_comments(self):
        """Test SLOC counting for comment-only input."""

        code = b"# Comment 1\n# Comment 2\n# Comment 3"

        result = _sloc_of_bytes(code)

        assert result == 0, "Result must not be empty"

    def test_only_blank_lines(self):
        """Test SLOC counting for blank lines only."""

        code = b"\n\n   \n  \n"

        result = _sloc_of_bytes(code)

        assert result == 0, "Result must not be empty"

    def test_mixed_content(self):
        """Test SLOC counting for mixed content."""

        code = b"# Header\n\ndef foo():\n    # inner comment\n    pass\n\n"

        result = _sloc_of_bytes(code)

        # def foo(): and pass are the only SLOC
        assert result == 2, "Result must not be empty"

    def test_js_style_comments(self):
        """Test SLOC counting ignores // comments."""

        code = b"// comment\nlet x = 1;\n// another"

        result = _sloc_of_bytes(code)

        assert result == 1, "Result must not be empty"


class TestExtMappings:
    """Tests for extension mappings."""

    def test_ext_to_mime_python(self):
        """Test Python extension mapping."""

        assert _EXT_TO_MIME[".py"] == "text/x-python", "Condition must be true"

    def test_ext_to_mime_json(self):
        """Test JSON extension mapping."""

        assert _EXT_TO_MIME[".json"] == "application/json", "Condition must be true"

    def test_ext_to_lang_python(self):
        """Test Python language mapping."""

        assert _EXT_TO_LANG[".py"] == "python", "Condition must be true"

    def test_ext_to_lang_yaml(self):
        """Test YAML extension mapping."""

        assert _EXT_TO_LANG[".yml"] == "yaml", "Condition must be true"
        assert _EXT_TO_LANG[".yaml"] == "yaml", "Condition must be true"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.detect", "name is not valid"
