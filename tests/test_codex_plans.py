"""Comprehensive test suite for codex_plans module.

This test file provides unit coverage for the codex_plans package, which
manages repository planning artifacts and continuous improvement documentation.

Test coverage includes:
- list_plan_documents() function with various path scenarios
- Path handling and normalization
- Error conditions and edge cases
- Integration with pathlib.Path
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codex_plans import list_plan_documents

# ============================================================================
# UNIT TESTS: list_plan_documents() Function
# ============================================================================


class TestListPlanDocuments:
    """Test suite for list_plan_documents() function."""

    def test_returns_list_type(self):
        """Test that function returns a list."""
        result = list_plan_documents()
        assert isinstance(result, list)

    def test_returns_pathlib_paths(self):
        """Test that all returned items are pathlib.Path objects."""
        result = list_plan_documents()
        for item in result:
            assert isinstance(item, Path)

    def test_default_base_dir_returns_results(self):
        """Test that default base_dir (None) returns valid results."""
        result = list_plan_documents(base_dir=None)
        assert isinstance(result, list)
        # Verify all items are .md files
        for path in result:
            assert path.suffix == ".md", "suffix is not valid"

    def test_returns_sorted_paths(self):
        """Test that returned paths are sorted."""
        result = list_plan_documents()
        if len(result) > 1:
            # Verify sorting by comparing with sorted version
            assert result == sorted(result), "Result must not be empty"

    def test_filters_markdown_files(self):
        """Test that only .md (Markdown) files are returned."""
        result = list_plan_documents()
        for path in result:
            assert path.suffix == ".md", "suffix is not valid"
            assert path.name.endswith(".md"), "Condition must be true"

    def test_with_custom_base_dir(self):
        """Test function with custom base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create some markdown files
            (base_path / "plan_a.md").touch()
            (base_path / "plan_b.md").touch()
            (base_path / "not_a_plan.txt").touch()

            result = list_plan_documents(base_dir=base_path)

            assert len(result) == 2, "Result must not be empty"
            assert all(p.suffix == ".md" for p in result), "Result must not be empty"
            assert (base_path / "plan_a.md") in result, "Result must not be empty"
            assert (base_path / "plan_b.md") in result, "Result must not be empty"
            assert (base_path / "not_a_plan.txt") not in result, "Result must not be empty"

    def test_custom_base_dir_with_nested_paths(self):
        """Test that glob correctly handles nested directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create nested structure
            (base_path / "subdir").mkdir()
            (base_path / "plan_root.md").touch()
            (base_path / "subdir" / "plan_nested.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # glob("*.md") should only match files in root, not subdirs
            assert len(result) == 1, "Result must not be empty"
            assert result[0].name == "plan_root.md", "Result must not be empty"

    def test_empty_directory(self):
        """Test with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = list_plan_documents(base_dir=Path(tmpdir))
            assert result == [], "Result must not be empty"

    def test_directory_with_only_non_markdown_files(self):
        """Test with directory containing no markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "file1.txt").touch()
            (base_path / "file2.json").touch()
            (base_path / "file3.yaml").touch()

            result = list_plan_documents(base_dir=base_path)
            assert result == [], "Result must not be empty"

    def test_with_path_object(self):
        """Test that function accepts pathlib.Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 1, "Result must not be empty"
            assert result[0].is_absolute() or result[0].is_relative_to(base_path), "Result must not be empty"

    def test_with_string_path_object(self):
        """Test behavior with Path object created from string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            plan_file = base_path / "strategy.md"
            plan_file.touch()

            result = list_plan_documents(base_dir=base_path)
            assert plan_file in result, "Result must not be empty"

    def test_handles_special_characters_in_filenames(self):
        """Test handling of markdown files with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            special_names = [
                "plan_2024-01-15.md",
                "plan with spaces.md",
                "PLAN_UPPERCASE.MD",
                "plan-with-dashes.md",
            ]

            for name in special_names:
                (base_path / name).touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            # Should include lowercase .md files only
            assert "plan_2024-01-15.md" in result_names, "Result must not be empty"
            assert "plan with spaces.md" in result_names, "Result must not be empty"
            assert "plan-with-dashes.md" in result_names, "Result must not be empty"
            # Uppercase .MD should not match (glob is case-sensitive on Linux)

    def test_large_number_of_files(self):
        """Test performance with large number of files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 100 markdown files
            for i in range(100):
                (base_path / f"plan_{i:03d}.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 100, "Result must not be empty"
            assert result == sorted(result), "Result must not be empty"

    def test_result_is_sorted_numerically(self):
        """Test that sorting is correct for numbered filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create files in non-sequential order
            names = ["plan_10.md", "plan_2.md", "plan_1.md", "plan_20.md"]
            for name in names:
                (base_path / name).touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = [p.name for p in result]

            # Verify lexicographic sorting (Path.glob default)
            assert result_names == sorted(names), "Result must not be empty"

    def test_resolves_to_absolute_paths(self):
        """Test that returned paths work consistently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # All paths should be accessible
            for path in result:
                assert path.exists(), "Condition must be true"
                assert path.is_file(), "Condition must be true"

    def test_none_base_dir_uses_module_directory(self):
        """Test that None base_dir defaults to module directory."""
        result = list_plan_documents(base_dir=None)

        # Should work without error
        assert isinstance(result, list)
        # May or may not have files, depending on actual repo state
        for path in result:
            assert path.suffix == ".md", "suffix is not valid"
            assert isinstance(path, Path)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestListPlanDocumentsIntegration:
    """Integration tests for list_plan_documents with module initialization."""

    def test_module_import_successful(self):
        """Test that module imports correctly."""
        from codex_plans import list_plan_documents as lpd
        assert callable(lpd), "Condition must be true"

    def test_function_has_docstring(self):
        """Test that function has proper documentation."""
        assert list_plan_documents.__doc__ is not None, "__doc__ must be initialized"
        assert "plan" in list_plan_documents.__doc__.lower(), "Condition must be true"

    def test_function_has_type_hints(self):
        """Test that function has type hints."""
        hints = list_plan_documents.__annotations__
        assert "return" in hints or hints, "Condition must be true"
        # Function should have a return type hint


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestListPlanDocumentsEdgeCases:
    """Test edge cases and error conditions."""

    def test_base_dir_is_file_not_directory(self):
        """Test behavior when base_dir points to a file instead of directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            file_path = base_path / "not_a_dir.md"
            file_path.touch()

            # This should either return empty list or raise an error
            # depending on implementation
            try:
                result = list_plan_documents(base_dir=file_path)
                # If it doesn't raise, should return empty
                assert result == [], "Result must not be empty"
            except (NotADirectoryError, FileNotFoundError, TypeError):
                # Expected behavior for file input
                pass

    def test_base_dir_nonexistent(self):
        """Test behavior when base_dir doesn't exist."""
        nonexistent = Path(os.path.join(tempfile.gettempdir(), "nonexistent_test_dir_") + str(id(None)))

        try:
            result = list_plan_documents(base_dir=nonexistent)
            # Should return empty list if path doesn't exist
            assert result == [], "Result must not be empty"
        except (FileNotFoundError, OSError):
            # Also acceptable behavior
            pass

    def test_base_dir_is_symlink_to_directory(self):
        """Test handling of symbolic links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            real_dir = base_path / "real"
            real_dir.mkdir()
            (real_dir / "plan.md").touch()

            link_dir = base_path / "link"
            try:
                link_dir.symlink_to(real_dir)
                result = list_plan_documents(base_dir=link_dir)
                assert len(result) == 1, "Result must not be empty"
                assert result[0].name == "plan.md", "Result must not be empty"
            except (OSError, NotImplementedError):
                # Skip if symlinks not supported
                pytest.skip("Symlinks not supported on this platform")

    def test_returns_new_list_on_each_call(self):
        """Test that function returns a new list each time (not cached)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan1.md").touch()

            result1 = list_plan_documents(base_dir=base_path)
            result2 = list_plan_documents(base_dir=base_path)

            # Same content, but different list objects
            assert result1 == result2, "Result must not be empty"
            assert result1 is not result2, "Result must not be empty"


# ============================================================================
# PERFORMANCE AND REGRESSION TESTS
# ============================================================================


class TestListPlanDocumentsPerformance:
    """Performance and regression tests."""

    def test_consistent_ordering_across_calls(self):
        """Test that function returns consistent ordering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            for name in ["zebra.md", "alpha.md", "beta.md"]:
                (base_path / name).touch()

            result1 = list_plan_documents(base_dir=base_path)
            result2 = list_plan_documents(base_dir=base_path)

            assert [p.name for p in result1] == [p.name for p in result2], "Result must not be empty"

    def test_all_returned_paths_are_files(self):
        """Test that all returned paths are files, not directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            (base_path / "file.md").touch()
            (base_path / "subdir").mkdir()

            result = list_plan_documents(base_dir=base_path)

            for path in result:
                assert path.is_file(), "Condition must be true"
                assert not path.is_dir(), "Condition must be true"

    def test_result_immutability_after_filesystem_change(self):
        """Test that returned list doesn't update when filesystem changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan1.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 1, "Result must not be empty"

            # Add another file
            (base_path / "plan2.md").touch()

            # Result should not change
            assert len(result) == 1, "Result must not be empty"


# ============================================================================
# MODULE-LEVEL TESTS
# ============================================================================


class TestCodexPlansModuleExports:
    """Test module exports and public API."""

    def test_all_export_defined(self):
        """Test that __all__ is defined in module."""
        from codex_plans import __all__
        assert isinstance(__all__, list)
        assert "list_plan_documents" in __all__, "Condition must be true"

    def test_public_api_accessible(self):
        """Test that all exported items are accessible."""
        import codex_plans
        from codex_plans import __all__

        for name in __all__:
            assert hasattr(codex_plans, name)

    def test_list_plan_documents_in_all(self):
        """Test that list_plan_documents is in __all__."""
        from codex_plans import __all__
        assert "list_plan_documents" in __all__, "Condition must be true"

    def test_no_unexpected_exports(self):
        """Test that module doesn't export private items."""
        import codex_plans

        for attr in dir(codex_plans):
            if not attr.startswith("_"):
                # Public attributes should be in __all__ or be module internals
                if attr not in ["__all__"]:
                    # Skip known module attributes
                    if not attr.startswith("__"):
                        assert attr in codex_plans.__all__ or attr == "list_plan_documents", "attr is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
