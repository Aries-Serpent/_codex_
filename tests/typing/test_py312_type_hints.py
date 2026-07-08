"""
Validate type hints work correctly in Python 3.12.

Tests PEP 585 (list[T]), PEP 604 (X | Y), and generic types.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any, Literal, Optional, TypeVar, get_type_hints

import pytest

# Module-level TypeVar for generic tests
T = TypeVar("T")


class TestPython312TypeHints:
    """Test modern type hint syntax compatibility."""

    def test_dict_syntax_type_hints(self):
        """Test dict[str, Any] syntax works in 3.12."""

        def sample_func(config: dict[str, Any]) -> dict[str, Any]:
            return config

        hints = get_type_hints(sample_func)
        assert "config" in hints, "Condition must be true"
        assert "return" in hints, "Condition must be true"

    def test_list_syntax_type_hints(self):
        """Test list[T] syntax works in 3.12."""

        def sample_func(items: list[str]) -> list[int]:
            return [len(item) for item in items]

        hints = get_type_hints(sample_func)
        assert "items" in hints, "Item must not be empty"
        assert "return" in hints, "Condition must be true"

    def test_union_pipe_syntax(self):
        """Test X | None syntax works in 3.12."""

        def sample_func(value: str | None) -> int | None:
            return len(value) if value else None

        hints = get_type_hints(sample_func)
        assert "value" in hints, "Value must be initialized"
        assert "return" in hints, "Condition must be true"

    def test_complex_nested_types(self):
        """Test complex nested type hints."""

        def sample_func(data: dict[str, list[int | str]]) -> list[dict[str, Any]]:
            return [{"key": value} for value in data.values()]

        hints = get_type_hints(sample_func)
        assert "data" in hints, "Data must not be empty"
        assert "return" in hints, "Condition must be true"

    @pytest.mark.skipif(sys.version_info < (3, 12), reason="3.12+ only")
    def test_no_future_annotations_needed(self):
        """
        Verify __future__ annotations still work in 3.12.

        The `from __future__ import annotations` should still be
        compatible and functional in Python 3.12.
        """

        # This file uses __future__ annotations at the top
        # If it works, this test passes
        def test_func(x: str) -> str:
            return x

        hints = get_type_hints(test_func)
        assert hints == {"x": str, "return": str}


class TestCodexMLTypeHints:
    """Test type hints in actual codex_ml modules."""

    def test_evaluation_cli_type_hints(self):
        """Test type hints in evaluation CLI module."""
        try:
            from codex_ml.evaluation import cli

            # Check if module has type-hinted functions
            if hasattr(cli, "_load_training_config"):
                hints = get_type_hints(cli._load_training_config)
                assert hints, "hints is not valid"
        except ImportError:
            pytest.skip("codex_ml.evaluation.cli not available")

    def test_data_loaders_type_hints(self):
        """Test type hints in data loaders module."""
        try:
            from codex_ml.data import loaders

            # Module should be importable and have type hints
            assert loaders is not None, "loaders must be initialized"
        except ImportError:
            pytest.skip("codex_ml.data.loaders not available")

    def test_utils_toml_compat_type_hints(self):
        """Test type hints in TOML compatibility module."""
        try:
            from codex_ml.utils import toml_compat

            # Module should be importable
            assert toml_compat is not None, "toml_compat must be initialized"
        except ImportError:
            pytest.skip("codex_ml.utils.toml_compat not available")


class TestGenericTypeHints:
    """Test generic type hints work in Python 3.12."""

    def test_generic_function(self):
        """Test generic function type hints."""

        def identity(x: T) -> T:
            return x

        hints = get_type_hints(identity)
        assert "x" in hints, "Condition must be true"
        assert "return" in hints, "Condition must be true"

    def test_generic_class(self):
        """Test generic class type hints."""
        from typing import Generic

        class Container(Generic[T]):
            def __init__(self, value: T) -> None:
                self.value = value

            def get(self) -> T:
                return self.value

        hints = get_type_hints(Container.__init__)
        assert "value" in hints, "Value must be initialized"

        hints = get_type_hints(Container.get)
        assert "return" in hints, "Condition must be true"

    @pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ feature")
    def test_pep_695_type_parameter_syntax(self):
        """
        Test PEP 695 type parameter syntax (Python 3.12+).

        Python 3.12 introduces new syntax for generic types:
        def func[T](x: T) -> T: ...

        This is more concise than TypeVar.
        """
        # Note: This syntax is only available in Python 3.12+
        # We test it's at least parseable if available
        code = """
def process[T](items: list[T]) -> T:
    return items[0]
"""
        try:
            compile(code, "<string>", "exec")
        except SyntaxError:
            if sys.version_info >= (3, 12):
                pytest.fail("PEP 695 syntax should be available in Python 3.12+")
            else:
                pytest.skip("PEP 695 syntax not available in this Python version")


class TestTypeHintCompatibility:
    """Test type hint backward compatibility."""

    def test_optional_style_variations(self):
        """Test different ways to express Optional."""

        # Optional is already imported at module level
        # Old style
        def func1(x: Optional[str]) -> Optional[int]:
            return len(x) if x else None

        # New style (Python 3.10+)
        def func2(x: str | None) -> int | None:
            return len(x) if x else None

        hints1 = get_type_hints(func1)
        hints2 = get_type_hints(func2)

        # Both should work
        assert "x" in hints1, "Condition must be true"
        assert "x" in hints2, "Condition must be true"

    def test_union_style_variations(self):
        """Test different ways to express Union."""

        # Union is already imported at module level
        # Old style
        def func1(x: str | int) -> str | None:
            return str(x) if isinstance(x, int) else x

        # New style (Python 3.10+)
        def func2(x: str | int) -> str | None:
            return str(x) if isinstance(x, int) else x

        hints1 = get_type_hints(func1)
        hints2 = get_type_hints(func2)

        # Both should work
        assert "x" in hints1, "Condition must be true"
        assert "x" in hints2, "Condition must be true"


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ tests")
class TestPython312SpecificFeatures:
    """Test Python 3.12-specific type hint features."""

    def test_improved_error_messages(self):
        """
        Test that Python 3.12 provides better type error messages.

        This is more of a demonstration than a functional test.
        """

        def typed_func(x: int) -> str:
            return str(x)

        # Should work fine
        result = typed_func(42)
        assert result == "42", "Result must not be empty"

    def test_typing_extensions_compatibility(self):
        """Test that typing_extensions works with Python 3.12."""
        try:
            from typing_extensions import TypedDict

            config: TypedDict(
                "ConfigDict",
                {"name": str, "version": str, "debug": bool},
            ) = {
                "name": "test",
                "version": "1.0",
                "debug": True,
            }

            assert config["name"] == "test", "Condition must be true"
            assert config["version"] == "1.0", "Condition must be true"
            assert config["debug"] is True, "Condition must be true"
        except ImportError:
            pytest.skip("typing_extensions not available")

    def test_literal_types(self):
        """Test Literal types work in Python 3.12."""

        # Literal is already imported at module level
        def set_mode(mode: Literal["train", "eval", "test"]) -> str:
            return f"Mode: {mode}"

        result = set_mode("train")
        assert result == "Mode: train", "Result must not be empty"

        hints = get_type_hints(set_mode)
        assert "mode" in hints, "Condition must be true"


class TestRealWorldTypeHints:
    """Test type hints in real-world scenarios."""

    def test_callable_type_hints(self):
        """Test Callable type hints."""

        def higher_order(func: Callable[[int], str]) -> Callable[[str], int]:
            def wrapper(s: str) -> int:
                return len(func(int(s)))

            return wrapper

        hints = get_type_hints(higher_order)
        assert "func" in hints, "Condition must be true"
        assert "return" in hints, "Condition must be true"

    def test_async_type_hints(self):
        """Test type hints on async functions."""
        import asyncio

        async def async_func(x: int) -> str:
            await asyncio.sleep(0.001)
            return str(x)

        hints = get_type_hints(async_func)
        assert "x" in hints, "Condition must be true"
        assert "return" in hints, "Condition must be true"

    def test_decorator_with_type_hints(self):
        """Test that decorators preserve type hints."""
        from collections.abc import Callable
        from functools import wraps
        from typing import TypeVar

        F = TypeVar("F", bound=Callable[..., Any])

        def my_decorator(func: F) -> F:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper  # type: ignore

        @my_decorator
        def decorated_func(x: int) -> str:
            return str(x)

        # Type hints should be preserved (via @wraps)
        assert hasattr(decorated_func, "__annotations__")
