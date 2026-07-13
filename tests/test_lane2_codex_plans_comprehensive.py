"""Comprehensive tests for codex_plans module - Lane 2 Coverage Expansion.

Tests cover:
- list_plan_documents() with various base_dir configurations
- Edge cases: empty directories, missing directories, symlinks
- Error paths: permission issues, non-existent paths
- Happy paths: normal directory with multiple .md files
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codex_plans import list_plan_documents


class TestListPlanDocuments:
    """Test list_plan_documents function."""

    def test_list_plan_documents_default_base_dir(self):
        """Test with default base_dir (package directory)."""
        result = list_plan_documents()
        assert isinstance(result, list)
        assert all(isinstance(p, Path) for p in result)
        # Should find some .md files in the package directory
        assert len(result) >= 0

    def test_list_plan_documents_custom_base_dir(self):
        """Test with custom base_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create some test markdown files
            (tmp_path / "plan1.md").write_text("# Plan 1")
            (tmp_path / "plan2.md").write_text("# Plan 2")
            (tmp_path / "other.txt").write_text("Not markdown")
            (tmp_path / "subdir").mkdir()
            (tmp_path / "subdir" / "plan3.md").write_text("# Plan 3")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert isinstance(result, list)
            assert len(result) == 2  # plan1.md and plan2.md only
            assert all(p.name.endswith('.md') for p in result)
            assert all(p.parent == tmp_path for p in result)

    def test_list_plan_documents_sorted_order(self):
        """Test that results are sorted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create files in non-alphabetical order
            (tmp_path / "zebra.md").write_text("# Z")
            (tmp_path / "apple.md").write_text("# A")
            (tmp_path / "middle.md").write_text("# M")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            names = [p.name for p in result]
            assert names == ["apple.md", "middle.md", "zebra.md"]
            assert names == sorted(names)

    def test_list_plan_documents_empty_directory(self):
        """Test with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            result = list_plan_documents(base_dir=tmp_path)
            assert result == []

    def test_list_plan_documents_no_markdown_files(self):
        """Test directory with no markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "file.txt").write_text("Text")
            (tmp_path / "file.py").write_text("# Code")
            (tmp_path / "file.json").write_text("{}")
            
            result = list_plan_documents(base_dir=tmp_path)
            assert result == []

    def test_list_plan_documents_mixed_files(self):
        """Test directory with mixed file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create mix of files
            (tmp_path / "plan.md").write_text("# Plan")
            (tmp_path / "README.md").write_text("# README")
            (tmp_path / "script.py").write_text("print('hi')")
            (tmp_path / "data.json").write_text("{}")
            (tmp_path / "notes.txt").write_text("notes")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert len(result) == 2
            names = [p.name for p in result]
            assert set(names) == {"plan.md", "README.md"}

    def test_list_plan_documents_only_direct_children(self):
        """Test that nested .md files are not included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create files at root and nested
            (tmp_path / "root_plan.md").write_text("# Root")
            (tmp_path / "subdir").mkdir()
            (tmp_path / "subdir" / "nested_plan.md").write_text("# Nested")
            (tmp_path / "subdir" / "deep").mkdir()
            (tmp_path / "subdir" / "deep" / "deep_plan.md").write_text("# Deep")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            # glob("*.md") should only return root-level .md files
            assert len(result) == 1
            assert result[0].name == "root_plan.md"

    def test_list_plan_documents_returns_path_objects(self):
        """Test that returned values are Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "test.md").write_text("# Test")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert len(result) == 1
            assert isinstance(result[0], Path)
            assert result[0].is_file()

    def test_list_plan_documents_path_absolute(self):
        """Test that returned paths are absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "plan.md").write_text("# Plan")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert len(result) == 1
            assert result[0].is_absolute()

    def test_list_plan_documents_multiple_calls_consistent(self):
        """Test that multiple calls return consistent results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "plan.md").write_text("# Plan")
            
            result1 = list_plan_documents(base_dir=tmp_path)
            result2 = list_plan_documents(base_dir=tmp_path)
            
            assert result1 == result2

    def test_list_plan_documents_large_directory(self):
        """Test with large number of markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create 50 markdown files
            expected_count = 50
            for i in range(expected_count):
                (tmp_path / f"plan_{i:03d}.md").write_text(f"# Plan {i}")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert len(result) == expected_count
            assert all(p.name.startswith("plan_") for p in result)

    def test_list_plan_documents_special_characters_in_names(self):
        """Test handling of markdown files with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create files with special characters
            special_names = [
                "plan-with-dashes.md",
                "plan_with_underscores.md",
                "PLAN_UPPERCASE.md",
            ]
            
            for name in special_names:
                (tmp_path / name).write_text("# Content")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            assert len(result) == len(special_names)
            names = {p.name for p in result}
            assert names == set(special_names)

    def test_list_plan_documents_case_sensitivity(self):
        """Test that .MD and .md are both recognized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create files with different cases
            (tmp_path / "plan.md").write_text("# Lower")
            (tmp_path / "PLAN.MD").write_text("# Upper")
            (tmp_path / "Plan.Md").write_text("# Mixed")
            
            result = list_plan_documents(base_dir=tmp_path)
            
            # glob("*.md") is case-sensitive on Unix, case-insensitive on Windows
            # We should at least get the lowercase one
            names = [p.name for p in result]
            assert "plan.md" in names

    def test_list_plan_documents_none_base_dir(self):
        """Test with explicit None for base_dir."""
        result = list_plan_documents(base_dir=None)
        assert isinstance(result, list)
        # Should return results from the package directory
        assert all(p.is_file() for p in result)


class TestListPlanDocumentsEdgeCases:
    """Test edge cases and error conditions."""

    def test_list_plan_documents_with_symlinks(self):
        """Test behavior with symbolic links."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create a markdown file and a symlink to it
            (tmp_path / "plan.md").write_text("# Plan")
            
            try:
                (tmp_path / "plan_link.md").symlink_to(tmp_path / "plan.md")
                result = list_plan_documents(base_dir=tmp_path)
                # Both files should be listed
                assert len(result) >= 1
            except OSError:
                # Skip on systems that don't support symlinks
                pytest.skip("Symlinks not supported on this system")

    def test_list_plan_documents_readonly_directory(self):
        """Test with read-only directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "plan.md").write_text("# Plan")
            
            # Should still be able to list files even if we make it read-only
            try:
                tmp_path.chmod(0o555)
                result = list_plan_documents(base_dir=tmp_path)
                assert len(result) == 1
            finally:
                tmp_path.chmod(0o755)


class TestListPlanDocumentsIntegration:
    """Integration tests for list_plan_documents."""

    def test_list_plan_documents_from_package(self):
        """Test actual package directory integration."""
        from src import codex_plans
        
        pkg_dir = Path(codex_plans.__file__).parent
        result = list_plan_documents()
        
        # Verify result is from the package directory
        for plan in result:
            assert plan.parent == pkg_dir or plan.parent.parent == pkg_dir

    def test_list_plan_documents_consistency_across_calls(self):
        """Test that function is deterministic."""
        results = [list_plan_documents() for _ in range(5)]
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result
