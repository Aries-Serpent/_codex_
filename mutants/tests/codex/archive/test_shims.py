"""
Tests for codex.archive.shims module.

This module contains tests for writing consolidation shims and pointers.
"""


class TestWritePythonShim:
    """Tests for write_python_shim function."""

    def test_creates_file(self, tmp_path):
        """Test write_python_shim creates file."""
        from codex.archive.shims import write_python_shim

        shim_path = tmp_path / "module.py"

        write_python_shim(shim_path, "canonical.module")

        assert shim_path.exists(), "Condition must be true"

    def test_file_content(self, tmp_path):
        """Test write_python_shim file content."""
        from codex.archive.shims import write_python_shim

        shim_path = tmp_path / "shim.py"

        write_python_shim(shim_path, "src.canonical.module")

        content = shim_path.read_text()

        assert "AUTO-GENERATED SHIM" in content, "Content must not be empty"
        assert "from canonical.module import *" in content, "Content must not be empty"
        assert "DeprecationWarning" in content, "Content must not be empty"

    def test_creates_parent_dirs(self, tmp_path):
        """Test write_python_shim creates parent directories."""
        from codex.archive.shims import write_python_shim

        shim_path = tmp_path / "nested" / "deep" / "module.py"

        write_python_shim(shim_path, "canonical.module")

        assert shim_path.exists(), "Condition must be true"
        assert shim_path.parent.exists(), "Condition must be true"


class TestWriteMarkdownPointer:
    """Tests for write_markdown_pointer function."""

    def test_creates_file(self, tmp_path):
        """Test write_markdown_pointer creates file."""
        from codex.archive.shims import write_markdown_pointer

        pointer_path = tmp_path / "README.md"

        write_markdown_pointer(pointer_path, "docs/canonical/README.md")

        assert pointer_path.exists(), "Condition must be true"

    def test_file_content(self, tmp_path):
        """Test write_markdown_pointer file content."""
        from codex.archive.shims import write_markdown_pointer

        pointer_path = tmp_path / "doc.md"

        write_markdown_pointer(pointer_path, "canonical/doc.md")

        content = pointer_path.read_text()

        assert "consolidated" in content.lower(), "Content must not be empty"
        assert "canonical/doc.md" in content, "Content must not be empty"


class TestWriteJsonPointer:
    """Tests for write_json_pointer function."""

    def test_creates_file(self, tmp_path):
        """Test write_json_pointer creates file."""
        from codex.archive.shims import write_json_pointer

        pointer_path = tmp_path / "config.json"

        write_json_pointer(pointer_path, "canonical/config.json")

        assert pointer_path.exists(), "Condition must be true"

    def test_file_content(self, tmp_path):
        """Test write_json_pointer file content."""
        from codex.archive.shims import write_json_pointer

        pointer_path = tmp_path / "data.json"

        write_json_pointer(pointer_path, "canonical/data.json")

        content = pointer_path.read_text()

        assert "$ref" in content, "Content must not be empty"
        assert "canonical/data.json" in content, "Data must not be empty"


class TestWriteCsvPointer:
    """Tests for write_csv_pointer function."""

    def test_creates_file(self, tmp_path):
        """Test write_csv_pointer creates file."""
        from codex.archive.shims import write_csv_pointer

        pointer_path = tmp_path / "data.csv"

        write_csv_pointer(pointer_path, "canonical/data.csv")

        assert pointer_path.exists(), "Condition must be true"

    def test_file_content(self, tmp_path):
        """Test write_csv_pointer file content."""
        from codex.archive.shims import write_csv_pointer

        pointer_path = tmp_path / "table.csv"

        write_csv_pointer(pointer_path, "canonical/table.csv")

        content = pointer_path.read_text()

        assert "Consolidated" in content, "Content must not be empty"
        assert "canonical/table.csv" in content, "Content must not be empty"


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_py_warn_constant(self):
        """Test _PY_WARN constant."""
        from codex.archive.shims import _PY_WARN

        assert "DeprecationWarning" in _PY_WARN, "Condition must be true"
        assert "warnings" in _PY_WARN, "Condition must be true"
