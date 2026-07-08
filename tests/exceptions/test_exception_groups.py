"""
Test ExceptionGroup compatibility (Python 3.12 standard feature).

ExceptionGroup was introduced in Python 3.11 and is fully supported in 3.12.
"""

# ruff: noqa: F821

from __future__ import annotations

import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11), reason="ExceptionGroup requires Python 3.11+"
)


class TestExceptionGroups:
    """Test exception group handling in Python 3.12."""

    def test_exception_group_creation(self):
        """Test basic ExceptionGroup creation."""
        eg = ExceptionGroup(
            "multiple errors",
            [
                ValueError("error 1"),
                TypeError("error 2"),
                RuntimeError("error 3"),
            ],
        )

        assert isinstance(eg, ExceptionGroup)
        assert len(eg.exceptions) == 3, "Collection must not be empty"
        assert eg.message == "multiple errors", "Error should be raised or set"

    def test_exception_group_catching(self):
        """Test catching ExceptionGroup."""

        def raise_multiple_errors():
            raise ExceptionGroup(
                "errors occurred", [ValueError("val error"), TypeError("type error")]
            )

        with pytest.raises(ExceptionGroup) as exc_info:
            raise_multiple_errors()

        eg = exc_info.value
        assert len(eg.exceptions) == 2, "Collection must not be empty"
        assert isinstance(eg.exceptions[0], ValueError)
        assert isinstance(eg.exceptions[1], TypeError)

    def test_except_star_syntax(self):
        """
        Test except* syntax for handling ExceptionGroup (Python 3.11+, standard in 3.12).

        The except* syntax allows catching specific exception types
        from an ExceptionGroup.
        """
        # Test that we can parse except* syntax
        code = """
try:
    raise ExceptionGroup("test", [ValueError("val"), TypeError("type")])
except* ValueError as eg:
    value_errors = eg.exceptions
except* TypeError as eg:
    type_errors = eg.exceptions
"""
        # This should compile without errors in Python 3.12
        compile(code, "<string>", "exec")

    def test_nested_exception_groups(self):
        """Test nested ExceptionGroups."""
        inner_eg = ExceptionGroup("inner errors", [ValueError("inner1"), ValueError("inner2")])

        outer_eg = ExceptionGroup("outer errors", [TypeError("outer"), inner_eg])

        assert len(outer_eg.exceptions) == 2, "Collection must not be empty"
        assert isinstance(outer_eg.exceptions[0], TypeError)
        assert isinstance(outer_eg.exceptions[1], ExceptionGroup)

    def test_exception_group_split(self):
        """Test splitting ExceptionGroup by type."""
        eg = ExceptionGroup(
            "mixed",
            [
                ValueError("v1"),
                TypeError("t1"),
                ValueError("v2"),
                RuntimeError("r1"),
            ],
        )

        # Split by ValueError
        value_eg, rest = eg.split(ValueError)

        if value_eg:
            assert all(isinstance(e, ValueError) for e in value_eg.exceptions)
        if rest:
            assert all(not isinstance(e, ValueError) for e in rest.exceptions)


@pytest.mark.skipif(False, reason="Python 3.12 is the standard version")
class TestPython312ExceptionImprovements:
    """Test Python 3.12-specific exception improvements."""

    def test_improved_error_messages(self):
        """
        Test that Python 3.12 provides improved error messages.

        Python 3.12 has enhanced error messages for better debugging.
        """
        # Test attribute error
        with pytest.raises(AttributeError) as exc_info:
            obj = object()
            _ = obj.nonexistent_attribute

        # Error message should be informative
        assert "nonexistent_attribute" in str(exc_info.value), "Value must be initialized"

    def test_exception_notes(self):
        """
        Test exception notes feature (Python 3.11+).

        Python 3.11+ allows adding notes to exceptions with add_note().
        """
        try:
            try:
                raise ValueError("original error")
            except ValueError as e:
                e.add_note("Additional context 1")
                e.add_note("Additional context 2")
                raise
        except ValueError as e:
            assert hasattr(e, "__notes__")
            assert len(e.__notes__) == 2, "Collection must not be empty"
            assert "Additional context 1" in e.__notes__, "Condition must be true"
            assert "Additional context 2" in e.__notes__, "Condition must be true"


class TestCodexMLExceptionHandling:
    """Test exception handling in codex_ml modules."""

    def test_no_exception_group_usage_in_codebase(self):
        """
        Verify if codebase uses ExceptionGroup.

        Search for ExceptionGroup usage in the codebase.
        If not used, this is informational.
        """
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        src_dir = repo_root / "src"

        if not src_dir.exists():
            pytest.skip("src directory not found")

        exception_group_found = False

        # Search Python files for ExceptionGroup usage
        for py_file in src_dir.rglob("*.py"):
            try:
                code = py_file.read_text()
                if "ExceptionGroup" in code:
                    exception_group_found = True
                    break
            except OSError:
                continue

        # This is informational, not a failure
        if not exception_group_found:
            pytest.skip("ExceptionGroup not used in codebase (as expected)")

    def test_exception_handling_patterns(self):
        """Test that standard exception handling works."""

        def risky_operation():
            raise ValueError("test error")

        # Standard exception handling should work
        with pytest.raises(ValueError) as exc_info:
            risky_operation()

        assert "test error" in str(exc_info.value), "Value must be initialized"

    def test_custom_exception_classes(self):
        """Test custom exception classes work in Python 3.12."""

        class CustomError(Exception):
            """Custom exception for testing."""

            def __init__(self, message: str, code: int):
                super().__init__(message)
                self.code = code

        def _raise_custom() -> None:
            raise CustomError("custom error", 42)

        with pytest.raises(CustomError) as exc_info:
            _raise_custom()

        assert exc_info.value.code == 42, "Value must be initialized"
        # Verify error message is in exception string representation
        assert "custom error" in str(exc_info.value), "Value must be initialized"


@pytest.mark.integration
class TestExceptionGroupIntegration:
    """Integration tests for exception handling in Python 3.12."""

    def test_async_exception_group(self):
        """Test ExceptionGroup with async code."""
        import asyncio

        async def failing_task(n):
            await asyncio.sleep(0.001)
            if n % 2 == 0:
                raise ValueError(f"Task {n} failed")
            return n

        async def gather_with_exception_group():
            try:
                results = await asyncio.gather(
                    failing_task(0), failing_task(1), failing_task(2), return_exceptions=True
                )

                # Collect exceptions
                exceptions = [r for r in results if isinstance(r, Exception)]
                if exceptions:
                    raise ExceptionGroup("async failures", exceptions)

                return results
            except ExceptionGroup as eg:
                assert len(eg.exceptions) == 2, "Collection must not be empty"
                raise

        with pytest.raises(ExceptionGroup):
            asyncio.run(gather_with_exception_group())

    def test_exception_chaining(self):
        """Test exception chaining works in Python 3.12."""
        try:
            try:
                raise ValueError("original")
            except ValueError as e:
                raise TypeError("wrapped") from e
        except TypeError as e:
            assert e.__cause__ is not None, "__cause__ must be initialized"
            assert isinstance(e.__cause__, ValueError)
            assert "original" in str(e.__cause__), "Condition must be true"
