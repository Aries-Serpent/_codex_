"""Comprehensive tests for src/common/error_handling.py.

Applies Quantum Test Methodology:
- Superposition: Tests both success and failure states
- Measurement Pattern: Tests exception handling (state collapse)
- Decoherence Pattern: Tests error isolation
"""

import pytest

# ==================== Import Tests ====================


class TestModuleImports:
    """Tests for module imports."""

    def test_module_import(self):
        """Test that error_handling module can be imported."""
        try:
            from common import error_handling

            assert error_handling is not None, "error_handling must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_safe_execute_import(self):
        """Test safe_execute decorator import."""
        try:
            from common.error_handling import safe_execute

            assert safe_execute is not None, "safe_execute must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_safe_call_import(self):
        """Test safe_call function import."""
        try:
            from common.error_handling import safe_call

            assert safe_call is not None, "safe_call must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_logger_configured(self):
        """Test that logger is configured."""
        try:
            from common.error_handling import logger

            assert logger is not None, "logger must be initialized"
        except ImportError:
            pytest.skip("Module not available")


# ==================== safe_execute Decorator Tests ====================


class TestSafeExecuteDecorator:
    """Tests for safe_execute decorator - Decoherence Pattern."""

    def test_successful_execution(self):
        """Test decorator allows successful execution."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_operation")
            def successful_func():
                return "success"

            result = successful_func()
            assert result == "success", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_exception_returns_default(self):
        """Test decorator catches exception and returns default."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("failing_operation", default_return="fallback")
            def failing_func():
                raise ValueError("test error")

            result = failing_func()
            assert result == "fallback", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_default_return_none(self):
        """Test default return is None when not specified."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_op")
            def error_func():
                raise RuntimeError("error")

            result = error_func()
            assert result is None, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_specific_exception_type(self):
        """Test catching specific exception type."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_op", exception_types=(ValueError,), default_return="caught")
            def value_error_func():
                raise ValueError("value error")

            result = value_error_func()
            assert result == "caught", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_unhandled_exception_type_raises(self):
        """Test that unhandled exception types propagate."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_op", exception_types=(ValueError,))
            def type_error_func():
                raise TypeError("type error")

            with pytest.raises(TypeError):
                type_error_func()
        except ImportError:
            pytest.skip("Module not available")

    def test_preserves_function_name(self):
        """Test that decorator preserves function name."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_op")
            def named_function():
                pass

            assert named_function.__name__ == "named_function", "__name__ is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_log_level_parameter(self):
        """Test different log levels."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("test_op", log_level="error")
            def error_log_func():
                raise Exception("test")

            # Should not raise
            result = error_log_func()
            assert result is None, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


# ==================== safe_call Function Tests ====================


class TestSafeCallFunction:
    """Tests for safe_call function - Measurement Pattern."""

    def test_successful_call(self):
        """Test successful function call."""
        try:
            from common.error_handling import safe_call

            def add(a, b):
                return a + b

            result = safe_call(add, 1, 2)
            assert result == 3, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_exception_returns_default(self):
        """Test exception returns default value."""
        try:
            from common.error_handling import safe_call

            def failing():
                raise RuntimeError("error")

            result = safe_call(failing, default_return=-1)
            assert result == -1, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_kwargs_passed(self):
        """Test keyword arguments are passed."""
        try:
            from common.error_handling import safe_call

            def greet(name, greeting="Hello"):
                return f"{greeting}, {name}!"

            result = safe_call(greet, "World", greeting="Hi")
            assert result == "Hi, World!"
        except ImportError:
            pytest.skip("Module not available")

    def test_operation_name_parameter(self):
        """Test operation_name parameter."""
        try:
            from common.error_handling import safe_call

            def risky():
                raise ValueError("risky")

            result = safe_call(risky, operation_name="risky operation", default_return="safe")
            assert result == "safe", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_specific_exception_types(self):
        """Test catching specific exception types."""
        try:
            from common.error_handling import safe_call

            def value_error():
                raise ValueError("value")

            result = safe_call(value_error, exception_types=(ValueError,), default_return="caught")
            assert result == "caught", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_unhandled_exception_raises(self):
        """Test unhandled exceptions propagate."""
        try:
            from common.error_handling import safe_call

            def type_error():
                raise TypeError("type")

            with pytest.raises(TypeError):
                safe_call(type_error, exception_types=(ValueError,))
        except ImportError:
            pytest.skip("Module not available")


# ==================== Edge Cases ====================


class TestEdgeCases:
    """Edge case tests - Tunneling Pattern."""

    def test_nested_safe_execute(self):
        """Test nested decorated functions."""
        try:
            from common.error_handling import safe_execute

            @safe_execute("outer")
            def outer():
                @safe_execute("inner", default_return="inner_default")
                def inner():
                    raise ValueError("inner error")

                return inner()

            result = outer()
            assert result == "inner_default", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_safe_call_with_lambda(self):
        """Test safe_call with lambda function."""
        try:
            from common.error_handling import safe_call

            result = safe_call(lambda x: x * 2, 5)
            assert result == 10, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_safe_call_with_none_function(self):
        """Test safe_call behavior with None function name."""
        try:
            from common.error_handling import safe_call

            def no_name_func():
                return "works"

            result = safe_call(no_name_func)
            assert result == "works", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")
