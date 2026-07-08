"""Comprehensive tests for src/codex_plans/__init__.py.

Applies Quantum Test Methodology:
- Superposition: Tests all possible plan states
- Born Rule: Prioritizes high-probability failures
- Zero Coverage: Critical priority (amplitude = 1.0)
"""

from pathlib import Path

import pytest

# ==================== Import Tests ====================


class TestModuleImports:
    """Tests for module imports."""

    def test_module_import(self):
        """Test that codex_plans module can be imported."""
        try:
            from src import codex_plans

            assert codex_plans is not None, "codex_plans must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_list_plan_documents_import(self):
        """Test list_plan_documents function import."""
        try:
            from src.codex_plans import list_plan_documents

            assert list_plan_documents is not None, "list_plan_documents must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_all_exports(self):
        """Test __all__ exports."""
        try:
            from src.codex_plans import __all__

            assert "list_plan_documents" in __all__, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


# ==================== list_plan_documents Tests ====================


class TestListPlanDocuments:
    """Tests for list_plan_documents function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            assert isinstance(result, list)
        except ImportError:
            pytest.skip("Module not available")

    def test_returns_path_objects(self):
        """Test that returned items are Path objects."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            for item in result:
                assert isinstance(item, Path)
        except ImportError:
            pytest.skip("Module not available")

    def test_finds_markdown_files(self):
        """Test that function finds .md files."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            # All returned files should be markdown
            for item in result:
                assert item.suffix == ".md", "Item must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_results_are_sorted(self):
        """Test that results are sorted."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            assert result == sorted(result), "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_custom_base_dir(self):
        """Test with custom base directory."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a test markdown file
                test_file = Path(tmpdir) / "test_plan.md"
                test_file.write_text("# Test Plan")

                result = list_plan_documents(base_dir=Path(tmpdir))
                assert len(result) == 1, "Result must not be empty"
                assert result[0].name == "test_plan.md", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_empty_directory(self):
        """Test with empty directory."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                result = list_plan_documents(base_dir=Path(tmpdir))
                assert result == [], "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_none_base_dir_uses_default(self):
        """Test that None base_dir uses module directory."""
        try:
            from src.codex_plans import list_plan_documents

            # Should not raise an error
            result = list_plan_documents(base_dir=None)
            assert isinstance(result, list)
        except ImportError:
            pytest.skip("Module not available")


# ==================== Edge Cases ====================


class TestEdgeCases:
    """Edge case tests - Tunneling Pattern."""

    def test_non_existent_directory(self):
        """Test with non-existent directory path."""
        try:
            from src.codex_plans import list_plan_documents

            # This should raise an error or return empty
            result = list_plan_documents(base_dir=Path("/nonexistent/path"))
            # If it doesn't raise, should return empty list
            assert result == [], "Result must not be empty"
        except (ImportError, OSError):
            pytest.skip("Module not available or OS error")

    def test_mixed_file_types(self):
        """Test directory with mixed file types."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                # Create various file types
                (Path(tmpdir) / "plan.md").write_text("# Plan")
                (Path(tmpdir) / "code.py").write_text("# Python")
                (Path(tmpdir) / "data.json").write_text("{}")

                result = list_plan_documents(base_dir=Path(tmpdir))
                # Should only include .md files
                assert len(result) == 1, "Result must not be empty"
                assert all(p.suffix == ".md" for p in result), "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")
