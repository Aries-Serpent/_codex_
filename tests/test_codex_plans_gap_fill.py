"""Gap-fill tests for src/codex_plans module coverage.

This file contains deterministic tests targeting specific lines and branches
that are not covered by existing test suites.

Test Coverage Target: 30% (10+ lines out of 34 LOC)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from codex_plans import list_plan_documents


class TestListPlanDocumentsGapFill:
    """Gap-fill test suite targeting uncovered lines and branches."""

    def test_custom_base_dir_with_md_files(self):
        """Test function with custom directory containing .md files.
        
        Targets: Line 30 (glob filtering), Line 31 (sorted return)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            
            # Create test structure
            (test_dir / "plan_a.md").write_text("# Plan A")
            (test_dir / "plan_b.md").write_text("# Plan B")
            (test_dir / "not_a_plan.txt").write_text("Not a plan")
            
            result = list_plan_documents(base_dir=test_dir)
            
            assert len(result) == 2
            assert all(isinstance(p, Path) for p in result)
            assert all(p.suffix == ".md" for p in result)

    def test_custom_base_dir_empty_directory(self):
        """Test function with empty custom directory.
        
        Targets: Line 30 (glob on empty directory), Line 31 (empty sorted)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            result = list_plan_documents(base_dir=Path(tmpdir))
            assert result == []

    def test_list_plan_documents_sorted_output(self):
        """Test that output is properly sorted.
        
        Targets: Line 31 (sorted() function)
        """
        result = list_plan_documents()
        assert result == sorted(result)
        
        # Additional check: verify alphabetical ordering
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i] <= result[i + 1]

    def test_none_base_dir_equals_default(self):
        """Test that None base_dir behaves like default.
        
        Targets: Line 30 (or operator, None handling)
        """
        result_default = list_plan_documents()
        result_none = list_plan_documents(base_dir=None)
        assert result_default == result_none

    def test_returns_path_objects(self):
        """Test that all returned items are Path objects.
        
        Targets: Line 31 (return type verification)
        """
        result = list_plan_documents()
        assert isinstance(result, list)
        assert all(isinstance(item, Path) for item in result)

    def test_markdown_file_filter(self):
        """Test that only .md files are returned.
        
        Targets: Line 30 (glob pattern filtering)
        """
        result = list_plan_documents()
        assert all(str(item).endswith('.md') for item in result)

    def test_glob_integration_with_sorting(self):
        """Test that glob() is correctly applied with sorting.
        
        Targets: Lines 30-31 (glob chain and sorting)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            
            # Create mixed files in non-alphabetical order
            (test_dir / "z_plan.md").touch()
            (test_dir / "a_plan.md").touch()
            (test_dir / "m_plan.md").touch()
            (test_dir / "b_other.txt").touch()  # Should be excluded
            
            result = list_plan_documents(base_dir=test_dir)
            
            # Verify sorted order
            names = [p.name for p in result]
            assert names == sorted(names)
            assert names == ["a_plan.md", "m_plan.md", "z_plan.md"]

    def test_path_resolve_behavior(self):
        """Test that paths are resolved correctly.
        
        Targets: Line 30 (Path resolution)
        """
        # Test with default module directory
        result = list_plan_documents()
        
        # All paths should be absolute and resolvable
        for path in result:
            assert path.is_absolute()
            assert path.exists()
            assert path.is_file()
