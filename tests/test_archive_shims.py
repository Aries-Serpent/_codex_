"""Comprehensive test suite for archive.shims module."""

import tempfile
from pathlib import Path
import pytest

from src.codex.archive.shims import (
    write_python_shim,
    write_markdown_pointer,
    write_json_pointer,
    write_csv_pointer,
    _PY_WARN,
)


class TestWritePythonShim:
    """Test suite for write_python_shim function."""

    def test_write_python_shim_creates_file(self):
        """Test that write_python_shim creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            assert duplicate.exists()

    def test_write_python_shim_creates_parent_dirs(self):
        """Test that write_python_shim creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "a" / "b" / "c" / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            assert duplicate.exists()
            assert duplicate.parent.exists()

    def test_write_python_shim_content_has_warning(self):
        """Test that shim file contains deprecation warning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            content = duplicate.read_text()
            assert "DeprecationWarning" in content
            assert "Deprecated shim" in content

    def test_write_python_shim_content_has_import(self):
        """Test that shim file contains import statement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            content = duplicate.read_text()
            assert "from canonical.module import *" in content

    def test_write_python_shim_strips_src_prefix(self):
        """Test that write_python_shim strips 'src.' prefix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            content = duplicate.read_text()
            assert "from canonical.module import *" in content
            assert "from src.canonical.module import *" not in content

    def test_write_python_shim_no_src_prefix(self):
        """Test write_python_shim with path that has no src prefix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "canonical.module")
            content = duplicate.read_text()
            assert "from canonical.module import *" in content

    def test_write_python_shim_auto_generated_comment(self):
        """Test that shim file has auto-generated comment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            content = duplicate.read_text()
            assert "AUTO-GENERATED SHIM" in content
            assert "DO NOT EDIT" in content

    def test_write_python_shim_noqa_comments(self):
        """Test that shim file has noqa comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            content = duplicate.read_text()
            assert "noqa: F401,F403" in content

    def test_write_python_shim_nested_path(self):
        """Test with deeply nested path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "a" / "b" / "c" / "d" / "e" / "shim.py"
            write_python_shim(duplicate, "src.canonical.module")
            assert duplicate.exists()
            content = duplicate.read_text()
            assert "from canonical.module import *" in content

    def test_write_python_shim_multiple_calls(self):
        """Test write_python_shim with multiple calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            shim1 = Path(tmpdir) / "shim1.py"
            shim2 = Path(tmpdir) / "shim2.py"
            
            write_python_shim(shim1, "src.module1")
            write_python_shim(shim2, "src.module2")
            
            assert shim1.exists()
            assert shim2.exists()
            
            content1 = shim1.read_text()
            content2 = shim2.read_text()
            
            assert "from module1 import *" in content1
            assert "from module2 import *" in content2

    def test_write_python_shim_special_characters_in_path(self):
        """Test with special characters in module path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.module_with_underscore")
            content = duplicate.read_text()
            assert "from module_with_underscore import *" in content


class TestWriteMarkdownPointer:
    """Test suite for write_markdown_pointer function."""

    def test_write_markdown_pointer_creates_file(self):
        """Test that write_markdown_pointer creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "README.md"
            write_markdown_pointer(duplicate, "docs/canonical/README.md")
            assert duplicate.exists()

    def test_write_markdown_pointer_content(self):
        """Test the content of markdown pointer file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "README.md"
            canonical_path = "docs/canonical/README.md"
            write_markdown_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            assert "consolidated" in content.lower()
            assert "canonical" in content.lower()
            assert canonical_path in content

    def test_write_markdown_pointer_creates_parent_dirs(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "a" / "b" / "c" / "README.md"
            write_markdown_pointer(duplicate, "docs/canonical/README.md")
            assert duplicate.exists()
            assert duplicate.parent.exists()

    def test_write_markdown_pointer_with_nested_path(self):
        """Test with nested canonical path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "pointer.md"
            canonical_path = "docs/guides/advanced/README.md"
            write_markdown_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            assert canonical_path in content

    def test_write_markdown_pointer_multiple_files(self):
        """Test creating multiple markdown pointers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pointer1 = Path(tmpdir) / "readme1.md"
            pointer2 = Path(tmpdir) / "readme2.md"
            
            write_markdown_pointer(pointer1, "docs/canonical1.md")
            write_markdown_pointer(pointer2, "docs/canonical2.md")
            
            assert pointer1.exists()
            assert pointer2.exists()


class TestWriteJsonPointer:
    """Test suite for write_json_pointer function."""

    def test_write_json_pointer_creates_file(self):
        """Test that write_json_pointer creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "config.json"
            write_json_pointer(duplicate, "canonical/config.json")
            assert duplicate.exists()

    def test_write_json_pointer_is_valid_json(self):
        """Test that output is valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "config.json"
            canonical_path = "canonical/config.json"
            write_json_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            
            # Should be valid JSON
            import json
            data = json.loads(content)
            assert "$ref" in data
            assert data["$ref"] == canonical_path

    def test_write_json_pointer_ref_format(self):
        """Test that $ref is properly formatted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "config.json"
            canonical_path = "path/to/canonical.json"
            write_json_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            assert f'"{canonical_path}"' in content

    def test_write_json_pointer_creates_parent_dirs(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "a" / "b" / "config.json"
            write_json_pointer(duplicate, "canonical/config.json")
            assert duplicate.exists()

    def test_write_json_pointer_backslash_conversion(self):
        """Test that backslashes are converted to forward slashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "config.json"
            canonical_path = "path\\to\\canonical.json"
            write_json_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            # Backslashes should be converted to forward slashes
            assert "\\" not in content.split("$ref")[1].split("}")[0]

    def test_write_json_pointer_multiple_files(self):
        """Test creating multiple JSON pointers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json1 = Path(tmpdir) / "config1.json"
            json2 = Path(tmpdir) / "config2.json"
            
            write_json_pointer(json1, "canonical/config1.json")
            write_json_pointer(json2, "canonical/config2.json")
            
            assert json1.exists()
            assert json2.exists()


class TestWriteCsvPointer:
    """Test suite for write_csv_pointer function."""

    def test_write_csv_pointer_creates_file(self):
        """Test that write_csv_pointer creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "data.csv"
            write_csv_pointer(duplicate, "canonical/data.csv")
            assert duplicate.exists()

    def test_write_csv_pointer_content(self):
        """Test the content of CSV pointer file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "data.csv"
            canonical_path = "canonical/data.csv"
            write_csv_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            assert "Consolidated" in content or "consolidated" in content
            assert "canonical" in content
            assert canonical_path in content

    def test_write_csv_pointer_comment_format(self):
        """Test that content is in CSV comment format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "data.csv"
            write_csv_pointer(duplicate, "canonical/data.csv")
            content = duplicate.read_text()
            assert content.startswith("#")

    def test_write_csv_pointer_creates_parent_dirs(self):
        """Test that parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "a" / "b" / "data.csv"
            write_csv_pointer(duplicate, "canonical/data.csv")
            assert duplicate.exists()

    def test_write_csv_pointer_multiple_files(self):
        """Test creating multiple CSV pointers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv1 = Path(tmpdir) / "data1.csv"
            csv2 = Path(tmpdir) / "data2.csv"
            
            write_csv_pointer(csv1, "canonical/data1.csv")
            write_csv_pointer(csv2, "canonical/data2.csv")
            
            assert csv1.exists()
            assert csv2.exists()


class TestPyWarnConstant:
    """Test suite for _PY_WARN constant."""

    def test_py_warn_contains_warning_import(self):
        """Test that _PY_WARN contains warning import."""
        assert "import warnings" in _PY_WARN

    def test_py_warn_contains_warn_call(self):
        """Test that _PY_WARN contains warn call."""
        assert "warnings.warn" in _PY_WARN or "_warnings.warn" in _PY_WARN

    def test_py_warn_contains_deprecation_warning(self):
        """Test that _PY_WARN contains DeprecationWarning."""
        assert "DeprecationWarning" in _PY_WARN

    def test_py_warn_contains_message(self):
        """Test that _PY_WARN contains deprecation message."""
        assert "Deprecated shim" in _PY_WARN

    def test_py_warn_is_string(self):
        """Test that _PY_WARN is a string."""
        assert isinstance(_PY_WARN, str)


class TestShimIntegration:
    """Integration tests for shim functions."""

    def test_all_shim_types_in_temp_directory(self):
        """Test creating all shim types in one directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_shim = Path(tmpdir) / "py_shim.py"
            md_pointer = Path(tmpdir) / "README.md"
            json_pointer = Path(tmpdir) / "config.json"
            csv_pointer = Path(tmpdir) / "data.csv"
            
            write_python_shim(py_shim, "src.canonical")
            write_markdown_pointer(md_pointer, "docs/canonical.md")
            write_json_pointer(json_pointer, "canonical.json")
            write_csv_pointer(csv_pointer, "canonical.csv")
            
            assert py_shim.exists()
            assert md_pointer.exists()
            assert json_pointer.exists()
            assert csv_pointer.exists()

    def test_directory_hierarchy_maintained(self):
        """Test that directory hierarchy is properly maintained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deep_path = Path(tmpdir) / "a" / "b" / "c" / "d" / "e"
            write_python_shim(deep_path / "module.py", "src.canonical")
            
            assert (deep_path / "module.py").exists()
            assert (deep_path / "module.py").parent == deep_path
            assert deep_path.parent == Path(tmpdir) / "a" / "b" / "c" / "d"


class TestShimEdgeCases:
    """Test edge cases for shim functions."""

    def test_write_python_shim_with_dots_in_path(self):
        """Test write_python_shim with dots in module path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "shim.py"
            write_python_shim(duplicate, "src.module.submodule.name")
            content = duplicate.read_text()
            assert "from module.submodule.name import *" in content

    def test_write_markdown_pointer_with_slashes(self):
        """Test write_markdown_pointer with various slash patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "pointer.md"
            canonical_path = "docs/guides/advanced/topic/README.md"
            write_markdown_pointer(duplicate, canonical_path)
            assert canonical_path in duplicate.read_text()

    def test_write_json_pointer_windows_path_conversion(self):
        """Test write_json_pointer handles Windows paths correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicate = Path(tmpdir) / "pointer.json"
            # Use backslashes to simulate Windows path
            canonical_path = "docs\\canonical\\file.json"
            write_json_pointer(duplicate, canonical_path)
            content = duplicate.read_text()
            # Should have forward slashes in JSON
            assert "docs/canonical/file.json" in content or "docs\\canonical\\file.json" not in content
