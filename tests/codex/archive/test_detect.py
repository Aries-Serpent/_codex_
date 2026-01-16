"""
Tests for codex.archive.detect module.

This module contains tests for file detection utilities.
"""

import pytest
from pathlib import Path


class TestFileMeta:
    """Tests for FileMeta dataclass."""

    def test_basic_creation(self):
        """Test FileMeta basic creation."""
        from codex.archive.detect import FileMeta
        
        meta = FileMeta(
            path="/path/to/file.py",
            size_bytes=1024,
            mtime_epoch=1640000000.0,
            mime="text/x-python",
            lang="python",
            sloc=50
        )
        
        assert meta.path == "/path/to/file.py"
        assert meta.size_bytes == 1024
        assert meta.mtime_epoch == 1640000000.0
        assert meta.mime == "text/x-python"
        assert meta.lang == "python"
        assert meta.sloc == 50


class TestSlocOfBytes:
    """Tests for _sloc_of_bytes function."""

    def test_simple_code(self):
        """Test SLOC counting for simple code."""
        from codex.archive.detect import _sloc_of_bytes
        
        code = b"def foo():\n    return 1\n\nprint(foo())"
        
        result = _sloc_of_bytes(code)
        
        assert result == 3  # 3 non-empty, non-comment lines

    def test_empty_bytes(self):
        """Test SLOC counting for empty input."""
        from codex.archive.detect import _sloc_of_bytes
        
        result = _sloc_of_bytes(b"")
        
        assert result == 0

    def test_only_comments(self):
        """Test SLOC counting for comment-only input."""
        from codex.archive.detect import _sloc_of_bytes
        
        code = b"# Comment 1\n# Comment 2\n# Comment 3"
        
        result = _sloc_of_bytes(code)
        
        assert result == 0

    def test_only_blank_lines(self):
        """Test SLOC counting for blank lines only."""
        from codex.archive.detect import _sloc_of_bytes
        
        code = b"\n\n   \n  \n"
        
        result = _sloc_of_bytes(code)
        
        assert result == 0

    def test_mixed_content(self):
        """Test SLOC counting for mixed content."""
        from codex.archive.detect import _sloc_of_bytes
        
        code = b"# Header\n\ndef foo():\n    # inner comment\n    pass\n\n"
        
        result = _sloc_of_bytes(code)
        
        # def foo(): and pass are the only SLOC
        assert result == 2

    def test_js_style_comments(self):
        """Test SLOC counting ignores // comments."""
        from codex.archive.detect import _sloc_of_bytes
        
        code = b"// comment\nlet x = 1;\n// another"
        
        result = _sloc_of_bytes(code)
        
        assert result == 1


class TestExtMappings:
    """Tests for extension mappings."""

    def test_ext_to_mime_python(self):
        """Test Python extension mapping."""
        from codex.archive.detect import _EXT_TO_MIME
        
        assert _EXT_TO_MIME[".py"] == "text/x-python"

    def test_ext_to_mime_json(self):
        """Test JSON extension mapping."""
        from codex.archive.detect import _EXT_TO_MIME
        
        assert _EXT_TO_MIME[".json"] == "application/json"

    def test_ext_to_lang_python(self):
        """Test Python language mapping."""
        from codex.archive.detect import _EXT_TO_LANG
        
        assert _EXT_TO_LANG[".py"] == "python"

    def test_ext_to_lang_yaml(self):
        """Test YAML extension mapping."""
        from codex.archive.detect import _EXT_TO_LANG
        
        assert _EXT_TO_LANG[".yml"] == "yaml"
        assert _EXT_TO_LANG[".yaml"] == "yaml"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.detect import logger
        
        assert logger is not None
        assert logger.name == "codex.archive.detect"
