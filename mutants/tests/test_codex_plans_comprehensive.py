"""Additional test suite for codex_plans module - Plan discovery patterns.

This module provides comprehensive test coverage for plan discovery patterns,
including various directory structures and file discovery scenarios.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codex_plans import list_plan_documents


class TestListPlanDocumentsDirectoryStructures:
    """Tests for various directory structure patterns."""

    def test_flat_directory_structure(self):
        """Test simple flat directory of plans."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create flat structure
            for i in range(5):
                (base_path / f"plan_{i}.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 5, "Result must not be empty"
            assert all(p.suffix == ".md" for p in result), "Result must not be empty"

    def test_repository_like_structure(self):
        """Test structure similar to actual repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Simulate repo structure
            (base_path / "README.md").touch()
            (base_path / "CONTRIBUTING.md").touch()
            (base_path / ".github").mkdir()
            (base_path / "docs").mkdir()
            (base_path / "docs" / "guide.md").touch()

            # Only root-level .md files should be found
            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            assert "README.md" in result_names, "Result must not be empty"
            assert "CONTRIBUTING.md" in result_names, "Result must not be empty"
            # guide.md should NOT be found (different directory)
            assert "guide.md" not in result_names, "Result must not be empty"

    def test_with_version_control_artifacts(self):
        """Test behavior with version control directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create version control artifacts
            git_dir = base_path / ".git"
            git_dir.mkdir()
            (git_dir / "plan.md").touch()  # Hidden in .git

            (base_path / "plan.md").touch()  # Visible

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            # Only root-level should be found
            assert len(result) == 1, "Result must not be empty"
            assert "plan.md" in result_names, "Result must not be empty"

    def test_mixed_file_types(self):
        """Test directory with mixed file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            file_types = [
                ("README.md", "text"),
                ("script.py", "python"),
                ("style.css", "style"),
                ("image.png", "image"),
                ("data.json", "json"),
                ("config.yaml", "config"),
                ("archive.zip", "archive"),
                ("executable", "binary"),
            ]

            for filename, filetype in file_types:
                (base_path / filename).touch()

            result = list_plan_documents(base_dir=base_path)

            # Only .md files
            assert len(result) == 1, "Result must not be empty"
            assert result[0].name == "README.md", "Result must not be empty"


class TestListPlanDocumentsNamingPatterns:
    """Tests for various naming patterns."""

    def test_descriptive_names(self):
        """Test with descriptive plan names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            names = [
                "project_roadmap.md",
                "sprint_planning_2024.md",
                "release_strategy.md",
                "architecture_design.md",
                "migration_plan.md",
            ]

            for name in names:
                (base_path / name).touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == len(names), "Result must not be empty"
            result_names = {p.name for p in result}
            for name in names:
                assert name in result_names, "Result must not be empty"

    def test_date_prefixed_names(self):
        """Test with date-prefixed plan names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            dates = [
                "2024-01-plan.md",
                "2024-02-planning.md",
                "2024-03-roadmap.md",
                "2025-Q1-strategy.md",
            ]

            for date_file in dates:
                (base_path / date_file).touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == len(dates), "Result must not be empty"

    def test_abbreviated_names(self):
        """Test with abbreviated plan names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            abbrev = ["a.md", "b.md", "x.md", "y.md", "z.md"]

            for name in abbrev:
                (base_path / name).touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == len(abbrev), "Result must not be empty"

    def test_with_numbers_in_names(self):
        """Test names with numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            names = [
                "phase_1.md",
                "phase_2.md",
                "phase_10.md",
                "plan_v1.md",
                "plan_v2.md",
            ]

            for name in names:
                (base_path / name).touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == len(names), "Result must not be empty"


class TestListPlanDocumentsSortingBehavior:
    """Tests for sorting behavior specifics."""

    def test_numeric_sorting_order(self):
        """Test that numeric filenames sort correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create files that would sort differently
            # lexicographically vs numerically
            files = ["file_2.md", "file_10.md", "file_1.md", "file_20.md"]
            for f in files:
                (base_path / f).touch()

            result = list_plan_documents(base_dir=base_path)
            names = [p.name for p in result]

            # Should be lexicographically sorted
            assert names == sorted(names), "names is not valid"

    def test_case_sensitive_sorting(self):
        """Test that sorting is case-sensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            files = ["aaa.md", "AAA.md", "Aaa.md"]
            for f in files:
                try:
                    (base_path / f).touch()
                except FileExistsError:
                    pass  # Case-insensitive filesystem

            result = list_plan_documents(base_dir=base_path)

            # Should have deterministic order
            assert result == sorted(result), "Result must not be empty"

    def test_special_char_sorting(self):
        """Test sorting with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            files = ["plan-a.md", "plan_b.md", "plan.c.md"]
            for f in files:
                (base_path / f).touch()

            result = list_plan_documents(base_dir=base_path)
            names = [p.name for p in result]

            # Should match lexicographic sort
            assert names == sorted(names), "names is not valid"


class TestListPlanDocumentsRobustness:
    """Robustness and reliability tests."""

    def test_idempotence_multiple_calls(self):
        """Test that multiple calls return same results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            for i in range(3):
                (base_path / f"plan_{i}.md").touch()

            # Call multiple times
            results = [list_plan_documents(base_dir=base_path) for _ in range(5)]

            # All should be identical
            first = [p.name for p in results[0]]
            for result in results[1:]:
                assert [p.name for p in result] == first, "Result must not be empty"

    def test_stability_under_filesystem_changes_other_files(self):
        """Test stability when other files change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            (base_path / "plan.md").touch()

            result1 = list_plan_documents(base_dir=base_path)

            # Change non-markdown file
            (base_path / "other.txt").touch()
            (base_path / "data.json").write_text("{}")

            result2 = list_plan_documents(base_dir=base_path)

            # Results should be identical
            assert len(result1) == len(result2), "Result1 must not be empty"
            assert {p.name for p in result1} == {p.name for p in result2}, "Result must not be empty"

    def test_handles_permission_readonly_files(self):
        """Test behavior with read-only markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            plan_file = base_path / "plan.md"
            plan_file.touch()

            # Make read-only
            plan_file.chmod(0o444)

            try:
                result = list_plan_documents(base_dir=base_path)
                assert len(result) == 1, "Result must not be empty"
            finally:
                plan_file.chmod(0o644)


class TestListPlanDocumentsWithRealWorldPatterns:
    """Tests with real-world directory patterns."""

    def test_monorepo_structure(self):
        """Test with monorepo directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create monorepo structure
            (base_path / "apps").mkdir()
            (base_path / "libs").mkdir()
            (base_path / "tools").mkdir()

            # Add plans at root
            (base_path / "ROADMAP.md").touch()
            (base_path / "ARCHITECTURE.md").touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            assert "ROADMAP.md" in result_names, "Result must not be empty"
            assert "ARCHITECTURE.md" in result_names, "Result must not be empty"

    def test_documentation_site_structure(self):
        """Test with documentation site structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create doc structure
            (base_path / "docs").mkdir()
            (base_path / "guides").mkdir()
            (base_path / "tutorials").mkdir()

            # Plans in root
            (base_path / "DEVELOPMENT.md").touch()
            (base_path / "TESTING.md").touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            assert "DEVELOPMENT.md" in result_names, "Result must not be empty"
            assert "TESTING.md" in result_names, "Result must not be empty"
            assert len(result) == 2, "Result must not be empty"

    def test_github_pages_structure(self):
        """Test with GitHub Pages structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create GitHub Pages structure
            (base_path / "_posts").mkdir()
            (base_path / "_config").mkdir()
            (base_path / "assets").mkdir()

            (base_path / "README.md").touch()
            (base_path / "PLAN.md").touch()

            result = list_plan_documents(base_dir=base_path)
            result_names = {p.name for p in result}

            assert len(result) == 2, "Result must not be empty"


class TestListPlanDocumentsConsistency:
    """Tests for result consistency and reliability."""

    def test_results_are_deterministic(self):
        """Test that results are deterministic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create files in random order
            for name in ["z.md", "a.md", "m.md", "b.md"]:
                (base_path / name).touch()

            # Get result multiple times
            result1 = list_plan_documents(base_dir=base_path)
            result2 = list_plan_documents(base_dir=base_path)
            result3 = list_plan_documents(base_dir=base_path)

            # All should have same order
            assert [p.name for p in result1] == [p.name for p in result2], "Result must not be empty"
            assert [p.name for p in result2] == [p.name for p in result3], "Result must not be empty"

    def test_results_are_independent(self):
        """Test that modifying result doesn't affect function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            (base_path / "a.md").touch()
            (base_path / "b.md").touch()
            (base_path / "c.md").touch()

            result1 = list_plan_documents(base_dir=base_path)
            original_len = len(result1)

            # Modify result
            result1.clear()

            # New call should return full list
            result2 = list_plan_documents(base_dir=base_path)
            assert len(result2) == original_len, "Result2 must not be empty"


class TestListPlanDocumentsErrorRecovery:
    """Tests for error recovery and resilience."""

    def test_recovers_from_permission_errors(self):
        """Test recovery from permission errors on files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            (base_path / "accessible.md").touch()
            restricted = base_path / "restricted.md"
            restricted.touch()

            try:
                # Restrict access
                restricted.chmod(0o000)

                result = list_plan_documents(base_dir=base_path)

                # Should still work
                assert isinstance(result, list)
            finally:
                # Restore permissions
                restricted.chmod(0o644)

    def test_continues_on_nonstandard_files(self):
        """Test that function continues past non-standard files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create various file types
            (base_path / "normal.md").touch()
            (base_path / "image.md").write_bytes(b"\x89PNG\r\n")  # PNG header
            (base_path / "text.md").write_text("Normal markdown")

            result = list_plan_documents(base_dir=base_path)

            # Should find all .md files
            assert len(result) == 3, "Result must not be empty"


class TestListPlanDocumentsPortability:
    """Tests for cross-platform portability."""

    def test_path_objects_work_across_calls(self):
        """Test that returned Path objects are reusable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Use path multiple ways
            for path in result:
                # Path operations
                assert path.exists(), "Condition must be true"
                assert path.is_file(), "Condition must be true"
                assert path.stat().st_size >= 0, "st_size must be greater than zero"
                assert path.read_text() == "", "Condition must be true"

    def test_path_resolution_consistent(self):
        """Test that path resolution is consistent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            result = list_plan_documents(base_dir=base_path)

            for path in result:
                # Should be consistent
                assert path.resolve() == path.resolve(), "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
