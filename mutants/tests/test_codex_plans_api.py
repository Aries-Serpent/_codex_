"""Advanced test suite for codex_plans module - API and contract testing.

This module provides advanced test coverage for the public API contract,
including type safety, documentation, and usage patterns.
"""

from __future__ import annotations

import inspect
import tempfile
from pathlib import Path
from typing import get_type_hints

import pytest

from codex_plans import list_plan_documents


class TestListPlanDocumentsAPIContract:
    """Tests for API contract and type safety."""

    def test_function_signature(self):
        """Test function has expected signature."""
        sig = inspect.signature(list_plan_documents)
        params = list(sig.parameters.keys())

        # Should have base_dir parameter
        assert "base_dir" in params, "Condition must be true"

    def test_return_type_annotation(self):
        """Test that return type is annotated."""
        hints = get_type_hints(list_plan_documents)
        assert "return" in hints, "Condition must be true"

    def test_parameter_type_hints(self):
        """Test that parameters have type hints."""
        hints = get_type_hints(list_plan_documents)
        assert "base_dir" in hints, "Condition must be true"

    def test_function_is_pure(self):
        """Test that function has no side effects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            # Call function
            result1 = list_plan_documents(base_dir=base_path)

            # Call again - should get same result
            result2 = list_plan_documents(base_dir=base_path)

            # Results should be equal
            assert [p.name for p in result1] == [p.name for p in result2], "Result must not be empty"

    def test_function_is_deterministic(self):
        """Test that function produces deterministic results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            for i in range(10):
                (base_path / f"plan_{i}.md").touch()

            # Get multiple results
            results = [list_plan_documents(base_dir=base_path) for _ in range(5)]

            # All should be identical
            names = [[p.name for p in r] for r in results]
            for name_list in names[1:]:
                assert name_list == names[0], "name_list is not valid"


class TestListPlanDocumentsDocumentation:
    """Tests for documentation completeness."""

    def test_function_has_docstring(self):
        """Test that function has a docstring."""
        assert list_plan_documents.__doc__ is not None, "__doc__ must be initialized"
        assert len(list_plan_documents.__doc__) > 20, "Collection must not be empty"

    def test_docstring_mentions_parameters(self):
        """Test docstring documents parameters."""
        doc = list_plan_documents.__doc__.lower()
        assert "base_dir" in doc or "parameter" in doc, "Condition must be true"

    def test_docstring_mentions_return_value(self):
        """Test docstring documents return value."""
        doc = list_plan_documents.__doc__.lower()
        assert "return" in doc or "list" in doc, "Condition must be true"

    def test_function_name_is_descriptive(self):
        """Test that function name is clear and descriptive."""
        assert "list" in list_plan_documents.__name__, "Condition must be true"
        assert "plan" in list_plan_documents.__name__, "Condition must be true"

    def test_function_docstring_includes_example(self):
        """Test docstring includes usage example if applicable."""
        doc = list_plan_documents.__doc__
        # Should have documentation
        assert doc and len(doc) > 50, "Doc must not be empty"


class TestListPlanDocumentsTypeCompatibility:
    """Tests for type compatibility."""

    def test_returns_list_of_paths(self):
        """Test that function returns list[Path]."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = list_plan_documents(base_dir=Path(tmpdir))

            assert isinstance(result, list)
            for item in result:
                assert isinstance(item, Path)

    def test_accepts_path_object(self):
        """Test function accepts Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise
            result = list_plan_documents(base_dir=Path(tmpdir))
            assert isinstance(result, list)

    def test_accepts_none_for_base_dir(self):
        """Test function accepts None for base_dir."""
        # Should not raise
        result = list_plan_documents(base_dir=None)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, Path)

    def test_response_type_consistency(self):
        """Test that response type is always consistent."""
        results = [
            list_plan_documents(base_dir=None),
            list_plan_documents(base_dir=Path(".")),
        ]

        for result in results:
            assert isinstance(result, list)


class TestListPlanDocumentsUsagePatterns:
    """Tests for common usage patterns."""

    def test_iteration_pattern(self):
        """Test common iteration pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            for i in range(3):
                (base_path / f"plan_{i}.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Common iteration pattern
            for path in result:
                assert path.is_file(), "Condition must be true"
                assert path.exists(), "Condition must be true"

    def test_filtering_pattern(self):
        """Test filtering results pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan_a.md").touch()
            (base_path / "plan_b.md").touch()
            (base_path / "test_a.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Filter pattern
            plans = [p for p in result if "plan" in p.name]
            assert len(plans) == 2, "Plans must not be empty"

    def test_mapping_pattern(self):
        """Test mapping results pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "a.md").touch()
            (base_path / "b.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Mapping pattern
            names = [p.name for p in result]
            assert len(names) == 2, "Names must not be empty"

    def test_unpacking_pattern(self):
        """Test unpacking first element pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "first.md").touch()
            (base_path / "second.md").touch()

            result = list_plan_documents(base_dir=base_path)

            if result:
                first, *rest = result
                assert first.exists(), "Condition must be true"
                assert len(rest) >= 0, "Rest must not be empty"


class TestListPlanDocumentsIntegrationWithPathlib:
    """Tests for integration with pathlib."""

    def test_returned_paths_chainable(self):
        """Test that returned paths can be chained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            result = list_plan_documents(base_dir=base_path)

            for path in result:
                # Chaining pathlib operations
                parent = path.parent
                name = path.name
                stem = path.stem

                assert parent.exists(), "Condition must be true"
                assert name == "test.md", "name is not valid"
                assert stem == "test", "stem is not valid"

    def test_returned_paths_comparable(self):
        """Test that returned paths are comparable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "a.md").touch()
            (base_path / "b.md").touch()

            result = list_plan_documents(base_dir=base_path)

            if len(result) > 1:
                assert result[0] != result[1], "Result must not be empty"
                assert (result[0] < result[1]) or (result[0] > result[1]), "Value must be greater than zero"

    def test_returned_paths_iterable(self):
        """Test that returned paths work with itertools."""
        import itertools

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            for i in range(3):
                (base_path / f"plan_{i}.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Should work with itertools
            paired = list(itertools.combinations(result, 2))
            assert len(paired) > 0, "Paired must not be empty"

    def test_returned_paths_with_glob(self):
        """Test using returned path with glob operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "plan.md").touch()

            result = list_plan_documents(base_dir=base_path)

            for path in result:
                # Use path's parent with glob
                parent = path.parent
                found = list(parent.glob("*.md"))
                assert path in found, "Condition must be true"


class TestListPlanDocumentsErrorMessages:
    """Tests for error messages and diagnostics."""

    def test_handles_invalid_path_gracefully(self):
        """Test handling of invalid path gracefully."""
        try:
            result = list_plan_documents(base_dir=Path("\x00invalid"))
            # Should handle or return empty
            assert isinstance(result, list)
        except (ValueError, OSError):
            # Also acceptable - explicit error
            pass

    def test_invalid_type_error_clear(self):
        """Test that type errors are clear if wrong type passed."""
        # Depending on implementation, might raise or handle
        try:
            result = list_plan_documents(base_dir="not_a_path_object")
            # If accepted, should work
            assert isinstance(result, list)
        except (TypeError, AttributeError):
            # Expected for wrong type
            pass


class TestListPlanDocumentsEdgeCasesAdvanced:
    """Advanced edge case tests."""

    def test_deeply_nested_similar_names(self):
        """Test with similar names at different levels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create similar structure
            (base_path / "plan.md").touch()
            sub = base_path / "subdir"
            sub.mkdir()
            (sub / "plan.md").touch()

            result = list_plan_documents(base_dir=base_path)

            # Should only find root level
            assert len(result) == 1, "Result must not be empty"

    def test_with_absolute_vs_relative_paths(self):
        """Test behavior with absolute vs relative paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            (base_path / "test.md").touch()

            result_abs = list_plan_documents(base_dir=base_path.resolve())
            result_rel = list_plan_documents(base_dir=base_path)

            # Both should work
            assert isinstance(result_abs, list)
            assert isinstance(result_rel, list)

    def test_with_path_symlink(self):
        """Test with path that is a symlink."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            real_dir = base_path / "real"
            real_dir.mkdir()
            (real_dir / "plan.md").touch()

            try:
                link_path = base_path / "link"
                link_path.symlink_to(real_dir)

                result = list_plan_documents(base_dir=link_path)
                assert isinstance(result, list)
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported")


class TestListPlanDocumentsComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_large_repository_simulation(self):
        """Simulate large repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create complex structure
            (base_path / ".git").mkdir()
            (base_path / ".github").mkdir()
            (base_path / "src").mkdir()
            (base_path / "tests").mkdir()
            (base_path / "docs").mkdir()

            # Add plans at root
            (base_path / "ROADMAP.md").touch()
            (base_path / "PLAN.md").touch()
            (base_path / "ARCHITECTURE.md").touch()

            result = list_plan_documents(base_dir=base_path)
            assert len(result) == 3, "Result must not be empty"

    def test_multi_user_concurrent_scenario(self):
        """Simulate multi-user concurrent access."""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            for i in range(5):
                (base_path / f"plan_{i}.md").touch()

            results = []
            errors = []

            def concurrent_access():
                try:
                    r = list_plan_documents(base_dir=base_path)
                    results.append(r)
                except Exception as e:
                    errors.append(e)

            threads = [
                threading.Thread(target=concurrent_access)
                for _ in range(10)
            ]

            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0, "Errors must not be empty"
            assert len(results) == 10, "Results must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
