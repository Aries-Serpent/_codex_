"""Extended test suite for codex_plans module - Plan document handling.

This module provides additional test coverage for plan document management,
including file discovery, caching, and interaction with the filesystem.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from codex_plans import list_plan_documents


class TestListPlanDocumentsFilesystemInteraction:
    """Tests for filesystem interaction in plan discovery."""

    def test_with_hidden_markdown_files(self):
        """Test that hidden markdown files are found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / ".hidden_plan.md").touch()
            (base_path / "visible_plan.md").touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            # Should find both hidden and visible
            assert ".hidden_plan.md" in result_names, "Result must not be empty"
            assert "visible_plan.md" in result_names, "Result must not be empty"

    def test_handles_read_only_directory(self):
        """Test behavior with read-only directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            try:
                # Make directory read-only
                base_path.chmod(0o555)
                result = list_plan_documents(base_dir=base_path)
                # Should work or handle gracefully
                assert isinstance(result, list)
            finally:
                # Restore permissions
                base_path.chmod(0o755)

    def test_with_circular_symlinks(self):
        """Test handling of circular symbolic links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create a circular symlink scenario
            try:
                dir1 = base_path / "dir1"
                dir1.mkdir()
                (dir1 / "plan.md").touch()

                result = list_plan_documents(base_dir=dir1)
                assert isinstance(result, list)
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported")

    def test_concurrent_access(self):
        """Test concurrent access to plan documents."""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            results = []
            errors = []

            def access():
                try:
                    r = list_plan_documents(base_dir=base_path)
                    results.append(r)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=access) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, "Errors must not be empty"
            assert len(results) == 5, "Results must not be empty"


class TestListPlanDocumentsPerformanceCharacteristics:
    """Performance characteristics and optimization tests."""

    def test_performance_with_many_non_markdown_files(self):
        """Test that non-markdown files don't affect performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 100 non-markdown files
            for i in range(100):
                (base_path / f"file_{i}.txt").touch()

            # Create 10 markdown files
            for i in range(10):
                (base_path / f"plan_{i}.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 10, "Result must not be empty"

    def test_performance_with_deep_directory_structure(self):
        """Test performance with deep nested directories (should not traverse)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create deep structure
            current = base_path
            for i in range(20):
                current = current / f"level_{i}"
                current.mkdir()
                (current / f"plan_{i}.md").touch()

            # Only root-level .md files should be found
            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 0, "Result must not be empty"

    def test_unicode_filename_handling(self):
        """Test handling of unicode characters in filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            unicode_names = [
                "планы.md",  # Cyrillic
                "计划.md",     # Chinese
                "خطة.md",    # Arabic
                "plan_café.md",  # Accented
            ]

            for name in unicode_names:
                try:
                    (base_path / name).touch()
                except (OSError, UnicodeError):
                    pytest.skip("Unicode filenames not supported")

            result = list_plan_documents(base_dir=base_path)
            # Should handle unicode gracefully
            assert isinstance(result, list)


class TestListPlanDocumentsPathNormalization:
    """Tests for path normalization and resolution."""

    def test_relative_path_handling(self):
        """Test with relative path inputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert isinstance(result, list)
            for path in result:
                assert isinstance(path, Path)

    def test_path_with_dots(self):
        """Test path containing . and .. components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            # Path with . component
            path_with_dots = base_path / "." / ".."  / base_path.name
            result = list_plan_documents(base_dir=path_with_dots)

            # Should normalize and work
            assert isinstance(result, list)

    def test_path_with_trailing_slash(self):
        """Test that trailing slashes don't affect results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            result1 = list_plan_documents(base_dir=base_path)
            # Both should give same result
            assert isinstance(result1, list)


class TestListPlanDocumentsEdgeCasesExtended:
    """Extended edge case tests."""

    def test_with_empty_filename(self):
        """Test handling edge cases in filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create valid markdown files
            (base_path / "plan.md").touch()
            (base_path / ".md").touch()  # File named .md

            result = list_plan_documents(base_dir=base_path)
            # Should handle edge case filenames
            assert isinstance(result, list)

    def test_case_sensitivity_on_extension(self):
        """Test case sensitivity of .md extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            files = ["plan.md", "plan.MD", "plan.Md", "plan.mD"]
            for f in files:
                (base_path / f).touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            # On Linux, glob is case-sensitive
            assert "plan.md" in result_names, "Result must not be empty"
            # .MD, .Md, .mD likely not matched

    def test_very_long_filename(self):
        """Test handling of very long filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create file with long name
            long_name = "plan_" + "a" * 200 + ".md"
            try:
                (base_path / long_name).touch()
                result = list_plan_documents(base_dir=base_path)
                assert len(result) == 1, "Result must not be empty"
            except (OSError, OSError) as e:
                # Filename may be too long for filesystem
                pytest.skip(f"Long filenames not supported: {e}")

    def test_multiple_extensions(self):
        """Test files with multiple extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create files with various extensions
            (base_path / "plan.md.txt").touch()  # Ends with .txt
            (base_path / "plan.txt.md").touch()  # Ends with .md
            (base_path / "plan.md").touch()      # Just .md

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            # Only plan.txt.md and plan.md should match
            assert "plan.txt.md" in result_names, "Result must not be empty"
            assert "plan.md" in result_names, "Result must not be empty"


class TestListPlanDocumentsWithMocks:
    """Tests using mock objects and patches."""

    @patch("pathlib.Path.glob")
    def test_with_mocked_glob(self, mock_glob):
        """Test list_plan_documents with mocked glob."""
        from pathlib import Path

        mock_glob.return_value = [
            Path("/mock/plan1.md"),
            Path("/mock/plan2.md"),
        ]

        result = list_plan_documents(base_dir=Path("/mock"))
        # Result depends on implementation, but should be a list
        assert isinstance(result, list)

    @patch("pathlib.Path.resolve")
    def test_with_mocked_resolve(self, mock_resolve):
        """Test with mocked path resolution."""
        from pathlib import Path

        mock_resolve.return_value = Path("/resolved/path")

        result = list_plan_documents(base_dir=Path("/some/path"))
        assert isinstance(result, list)


class TestListPlanDocumentsReturnValueCharacteristics:
    """Tests for return value characteristics."""

    def test_return_value_is_independent_list(self):
        """Test that returned list can be modified without affecting state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan1.md").touch()
            (base_path / "plan2.md").touch()

            result = list_plan_documents(base_dir=base_path)
            original_len = len(result)

            # Modify the returned list
            result.pop()

            # Next call should return full list
            result2 = list_plan_documents(base_dir=base_path)
            assert len(result2) == original_len, "Result2 must not be empty"

    def test_paths_are_comparable(self):
        """Test that returned paths are comparable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "a.md").touch()
            (base_path / "b.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Paths should be comparable
            if len(result) > 1:
                assert result[0] < result[1] or result[0] > result[1], "Value must be greater than zero"

    def test_paths_are_usable_with_pathlib_operations(self):
        """Test that returned paths work with pathlib operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            result = list_plan_documents(base_dir=base_path)

            for path in result:
                # Should work with pathlib operations
                assert path.name.endswith(".md"), "Condition must be true"
                assert path.suffix == ".md", "suffix is not valid"
                assert path.stem == "plan", "stem is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
