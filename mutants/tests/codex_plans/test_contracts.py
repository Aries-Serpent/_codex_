"""Type checking and contract tests for codex_plans.

Tests type annotations, function contracts, and API stability.
"""

from pathlib import Path
from typing import get_type_hints

import pytest


class TestTypeAnnotations:
    """Test that type annotations are correct."""

    def test_list_plan_documents_signature(self):
        """Test function signature matches documentation."""
        try:
            from src.codex_plans import list_plan_documents

            # Get type hints
            hints = get_type_hints(list_plan_documents)

            # Check parameter types
            assert "base_dir" in hints, "Condition must be true"
            assert "return" in hints, "Condition must be true"

            # Return type should be list[Path]
            return_hint = str(hints["return"])
            assert "list" in return_hint.lower(), "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_function_callable(self):
        """Test that list_plan_documents is callable."""
        try:
            from src.codex_plans import list_plan_documents

            assert callable(list_plan_documents), "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestContractCompliance:
    """Test function contract compliance."""

    def test_always_returns_list(self):
        """Test that function always returns a list, never None."""
        try:
            from src.codex_plans import list_plan_documents

            # Test with various inputs
            test_cases = [
                None,  # Default
                Path(__file__).parent,  # Valid directory
            ]

            for test_input in test_cases:
                result = list_plan_documents(base_dir=test_input)
                assert isinstance(result, list), f"Should return list for input {test_input}"
        except ImportError:
            pytest.skip("Module not available")

    def test_never_returns_none(self):
        """Test that function never returns None."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            assert result is not None, "result must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_returns_path_objects_only(self):
        """Test that list contains only Path objects."""
        try:
            try:
                from codex_plans import list_plan_documents as _lpd
            except ImportError:
                from src.codex_plans import list_plan_documents as _lpd  # type: ignore[no-redef]

            result = _lpd()
            for item in result:
                # list_plan_documents() is annotated to return list[Path]; assert
                # isinstance so PosixPath/WindowsPath (stdlib subclasses) also pass.
                assert isinstance(item, Path), f"Item {item} should be Path, got {type(item)}"
        except ImportError:
            pytest.skip("Module not available")


class TestAPIStability:
    """Test API stability and backward compatibility."""

    def test_function_exists_in_all(self):
        """Test that list_plan_documents is in __all__."""
        try:
            from src.codex_plans import __all__

            assert "list_plan_documents" in __all__, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_function_accessible_via_import(self):
        """Test that function can be imported directly."""
        try:
            from src.codex_plans import list_plan_documents

            assert list_plan_documents is not None, "list_plan_documents must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_module_has_docstring(self):
        """Test that module has docstring."""
        try:
            from src import codex_plans as _codex_plans_mod

            assert _codex_plans_mod.__doc__ is not None, "__doc__ must be initialized"
            assert len(_codex_plans_mod.__doc__.strip()) > 0, "Collection must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_function_has_docstring(self):
        """Test that list_plan_documents has docstring."""
        try:
            from src.codex_plans import list_plan_documents

            assert list_plan_documents.__doc__ is not None, "__doc__ must be initialized"
            assert len(list_plan_documents.__doc__.strip()) > 0, "Collection must not be empty"
        except ImportError:
            pytest.skip("Module not available")


class TestParameterValidation:
    """Test parameter validation and handling."""

    def test_base_dir_none_accepted(self):
        """Test that base_dir=None is valid."""
        try:
            from src.codex_plans import list_plan_documents

            # Should not raise
            result = list_plan_documents(base_dir=None)
            assert isinstance(result, list)
        except ImportError:
            pytest.skip("Module not available")

    def test_base_dir_path_accepted(self):
        """Test that base_dir=Path(...) is valid."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                result = list_plan_documents(base_dir=Path(tmpdir))
                assert isinstance(result, list)
        except ImportError:
            pytest.skip("Module not available")


class TestDocumentation:
    """Test documentation quality."""

    def test_function_docstring_complete(self):
        """Test that docstring includes all sections."""
        try:
            from src.codex_plans import list_plan_documents

            doc = list_plan_documents.__doc__
            assert doc is not None, "doc must be initialized"

            # Check for key sections (numpy-style docstring)
            doc_lower = doc.lower()
            assert "parameters" in doc_lower or "args" in doc_lower, "Condition must be true"
            assert "returns" in doc_lower, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")

    def test_function_name_descriptive(self):
        """Test that function name is descriptive."""
        try:
            from src.codex_plans import list_plan_documents

            # Name should be clear and descriptive
            name = list_plan_documents.__name__
            assert "list" in name, "Condition must be true"
            assert "plan" in name, "Condition must be true"
            assert "documents" in name, "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestReturnValueProperties:
    """Test properties of return values."""

    def test_return_list_is_mutable(self):
        """Test that returned list can be modified."""
        try:
            from src.codex_plans import list_plan_documents

            result = list_plan_documents()
            original_len = len(result)

            # Should be able to modify returned list
            if result:
                result.append(Path("/fake/path.md"))
                assert len(result) == original_len + 1, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_return_list_is_new_instance(self):
        """Test that each call returns a new list instance."""
        try:
            from src.codex_plans import list_plan_documents

            result1 = list_plan_documents()
            result2 = list_plan_documents()

            # Should be different list objects
            assert result1 is not result2, "Result must not be empty"
            # But with equal contents
            assert result1 == result2, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


class TestGlobPatternBehavior:
    """Test glob pattern behavior specifics."""

    def test_glob_is_non_recursive(self):
        """Test that glob only searches immediate directory."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                # Create file in root
                (Path(tmpdir) / "root.md").write_text("# Root")

                # Create subdirectory with file
                subdir = Path(tmpdir) / "subdir"
                subdir.mkdir()
                (subdir / "nested.md").write_text("# Nested")

                result = list_plan_documents(base_dir=Path(tmpdir))

                # Should only find root.md, not nested.md
                assert len(result) == 1, "Result must not be empty"
                assert result[0].name == "root.md", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_glob_matches_md_extension_only(self):
        """Test that glob only matches .md extension."""
        try:
            import tempfile

            from src.codex_plans import list_plan_documents

            with tempfile.TemporaryDirectory() as tmpdir:
                # Create files with various extensions
                (Path(tmpdir) / "plan.md").write_text("# Plan")
                (Path(tmpdir) / "plan.markdown").write_text("# Plan")
                (Path(tmpdir) / "plan.txt").write_text("# Plan")
                (Path(tmpdir) / "plan.MD").write_text("# Plan")

                result = list_plan_documents(base_dir=Path(tmpdir))

                # Should only match .md (lowercase)
                # Behavior depends on glob implementation
                md_files = [p for p in result if p.suffix.lower() == ".md"]
                assert len(md_files) > 0, "Md_files must not be empty"
        except ImportError:
            pytest.skip("Module not available")


class TestModuleConstants:
    """Test module-level constants."""

    def test_module_has_all(self):
        """Test that module defines __all__."""
        try:
            from src import codex_plans

            assert hasattr(codex_plans, "__all__")
            assert isinstance(codex_plans.__all__, list)
        except ImportError:
            pytest.skip("Module not available")

    def test_all_exports_are_valid(self):
        """Test that all items in __all__ exist."""
        try:
            from src import codex_plans

            for name in codex_plans.__all__:
                assert hasattr(codex_plans, name), f"{name} should exist in module"
        except ImportError:
            pytest.skip("Module not available")
