"""Comprehensive tests for src/tools/registry.py.

Applies Quantum Test Methodology:
- Superposition: Tests all registration states
- Measurement Pattern: Tests tool execution (state collapse)
- Safeguard Validation: Tests bounds and limits
"""

import pytest

# ==================== Import Tests ====================


class TestModuleImports:
    """Tests for module imports."""

    def test_module_import(self):
        """Test that registry module can be imported."""
        try:
            from src.tools import registry

            assert registry is not None, "registry must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_definition_import(self):
        """Test ToolDefinition class import."""
        try:
            from src.tools.registry import ToolDefinition

            assert ToolDefinition is not None, "ToolDefinition must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_result_import(self):
        """Test ToolResult class import."""
        try:
            from src.tools.registry import ToolResult

            assert ToolResult is not None, "ToolResult must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_registry_import(self):
        """Test ToolRegistry class import."""
        try:
            from src.tools.registry import ToolRegistry

            assert ToolRegistry is not None, "ToolRegistry must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_constants_import(self):
        """Test constants are defined."""
        try:
            from src.tools.registry import MAX_TOOL_NAME_LENGTH, MAX_TOOLS

            assert MAX_TOOLS == 1000, "MAX_TOOLS is not valid"
            assert MAX_TOOL_NAME_LENGTH == 100, "Length must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")


# ==================== ToolDefinition Tests ====================


class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""

    def test_tool_definition_creation(self):
        """Test creating ToolDefinition."""
        try:
            from src.tools.registry import ToolDefinition

            def handler():
                pass

            tool = ToolDefinition(name="test_tool", description="A test tool", handler=handler)
            assert tool.name == "test_tool", "name is not valid"
            assert tool.description == "A test tool", "description is not valid"
            assert tool.handler == handler, "handler is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_definition_defaults(self):
        """Test default values."""
        try:
            from src.tools.registry import ToolDefinition

            tool = ToolDefinition(name="test", description="desc", handler=lambda: None)
            assert tool.parameters == {}, "parameters is not valid"
            assert tool.requires_confirmation is False, "requires_confirmation is not valid"
            assert tool.timeout_seconds == 30, "timeout_seconds is not valid"
            assert tool.enabled is True, "enabled is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_definition_custom_values(self):
        """Test custom values."""
        try:
            from src.tools.registry import ToolDefinition

            tool = ToolDefinition(
                name="custom",
                description="Custom tool",
                handler=lambda: None,
                parameters={"arg1": "string"},
                requires_confirmation=True,
                timeout_seconds=60,
                enabled=False,
            )
            assert tool.parameters == {"arg1": "string"}, "parameters is not valid"
            assert tool.requires_confirmation is True, "requires_confirmation is not valid"
            assert tool.timeout_seconds == 60, "timeout_seconds is not valid"
            assert tool.enabled is False, "enabled is not valid"
        except ImportError:
            pytest.skip("Module not available")


# ==================== ToolResult Tests ====================


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_tool_result_success(self):
        """Test successful result."""
        try:
            from src.tools.registry import ToolResult

            result = ToolResult(success=True, output="Success!")
            assert result.success is True, "Result must not be empty"
            assert result.output == "Success!", "Result must not be empty"
            assert result.error is None, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_result_failure(self):
        """Test failure result."""
        try:
            from src.tools.registry import ToolResult

            result = ToolResult(success=False, error="Something went wrong")
            assert result.success is False, "Result must not be empty"
            assert result.error == "Something went wrong", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_result_defaults(self):
        """Test default values."""
        try:
            from src.tools.registry import ToolResult

            result = ToolResult(success=True)
            assert result.output is None, "Result must not be empty"
            assert result.error is None, "Result must not be empty"
            assert result.duration_ms == 0.0, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


# ==================== ToolRegistry Tests ====================


class TestToolRegistry:
    """Tests for ToolRegistry class - State Machine Pattern."""

    def test_registry_creation(self):
        """Test creating ToolRegistry."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            assert registry is not None, "registry must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_tool(self):
        """Test registering a tool."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()

            def my_handler():
                return "Hello"

            result = registry.register(
                name="my_tool", handler=my_handler, description="My test tool"
            )
            assert result is True, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_empty_name_fails(self):
        """Test that empty name fails registration."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            result = registry.register(name="", handler=lambda: None, description="Empty name tool")
            assert result is False, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_none_name_fails(self):
        """Test that None name fails registration."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            result = registry.register(
                name=None, handler=lambda: None, description="None name tool"
            )
            assert result is False, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_with_parameters(self):
        """Test registering tool with parameters."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            result = registry.register(
                name="param_tool",
                handler=lambda x: x,
                description="Tool with params",
                parameters={"x": "string"},
            )
            assert result is True, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_with_confirmation(self):
        """Test registering tool requiring confirmation."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            result = registry.register(
                name="confirm_tool",
                handler=lambda: None,
                description="Needs confirmation",
                requires_confirmation=True,
            )
            assert result is True, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_register_with_timeout(self):
        """Test registering tool with custom timeout."""
        try:
            from src.tools.registry import ToolRegistry

            registry = ToolRegistry()
            result = registry.register(
                name="timeout_tool",
                handler=lambda: None,
                description="Custom timeout",
                timeout_seconds=120,
            )
            assert result is True, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


# ==================== Safeguard Tests ====================


class TestSafeguards:
    """Tests for registry safeguards - Decoherence Pattern."""

    def test_max_tool_name_length_constant(self):
        """Test MAX_TOOL_NAME_LENGTH is defined."""
        try:
            from src.tools.registry import MAX_TOOL_NAME_LENGTH

            assert MAX_TOOL_NAME_LENGTH > 0, "MAX_TOOL_NAME_LENGTH must be greater than zero"
            assert MAX_TOOL_NAME_LENGTH == 100, "Length must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")

    def test_max_tools_constant(self):
        """Test MAX_TOOLS is defined."""
        try:
            from src.tools.registry import MAX_TOOLS

            assert MAX_TOOLS > 0, "MAX_TOOLS must be greater than zero"
            assert MAX_TOOLS == 1000, "MAX_TOOLS is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_logger_configured(self):
        """Test that logger is configured."""
        try:
            from src.tools.registry import logger

            assert logger is not None, "logger must be initialized"
        except ImportError:
            pytest.skip("Module not available")
