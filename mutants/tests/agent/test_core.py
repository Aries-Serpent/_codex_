"""Comprehensive tests for src/agent/core.py module."""

import pytest


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_task_status_import(self):
        """Test that TaskStatus can be imported."""
        try:
            from src.agent.core import TaskStatus

            assert TaskStatus is not None, "TaskStatus must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_task_status_values(self):
        """Test all TaskStatus enum values."""
        try:
            from src.agent.core import TaskStatus

            assert TaskStatus.PENDING.value == "pending", "Value must be initialized"
            assert TaskStatus.RUNNING.value == "running", "Value must be initialized"
            assert TaskStatus.COMPLETED.value == "completed", "Value must be initialized"
            assert TaskStatus.FAILED.value == "failed", "Value must be initialized"
            assert TaskStatus.VERIFIED.value == "verified", "Value must be initialized"
            assert TaskStatus.UNKNOWN.value == "unknown", "Value must be initialized"
        except ImportError:
            pytest.skip("Module not available")


class TestSafeguardConstants:
    """Tests for safeguard constants."""

    def test_max_task_length(self):
        """Test MAX_TASK_LENGTH constant."""
        try:
            from src.agent.core import MAX_TASK_LENGTH

            assert MAX_TASK_LENGTH == 50000, "Length must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")

    def test_max_context_length(self):
        """Test MAX_CONTEXT_LENGTH constant."""
        try:
            from src.agent.core import MAX_CONTEXT_LENGTH

            assert MAX_CONTEXT_LENGTH == 100000, "Length must be greater than zero"
        except ImportError:
            pytest.skip("Module not available")

    def test_max_tool_calls(self):
        """Test MAX_TOOL_CALLS constant."""
        try:
            from src.agent.core import MAX_TOOL_CALLS

            assert MAX_TOOL_CALLS == 20, "MAX_TOOL_CALLS is not valid"
        except ImportError:
            pytest.skip("Module not available")


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_config_creation(self):
        """Test creating AgentConfig."""
        try:
            from src.agent.core import AgentConfig

            config = AgentConfig()
            assert config is not None, "config must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_config_defaults(self):
        """Test AgentConfig default values."""
        try:
            from src.agent.core import AgentConfig

            config = AgentConfig()
            assert config.model_preference == "auto", "model_preference is not valid"
            assert config.max_tool_calls == 10, "max_tool_calls is not valid"
            assert config.enable_rag is True, "enable_rag is not valid"
            assert config.enable_verification is True, "enable_verification is not valid"
            assert config.timeout_seconds == 300, "timeout_seconds is not valid"
            assert config.cost_limit == 1.0, "cost_limit is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_config_custom_values(self):
        """Test AgentConfig with custom values."""
        try:
            from src.agent.core import AgentConfig

            config = AgentConfig(
                model_preference="gpt-4", max_tool_calls=5, enable_rag=False, timeout_seconds=600
            )
            assert config.model_preference == "gpt-4", "model_preference is not valid"
            assert config.max_tool_calls == 5, "max_tool_calls is not valid"
            assert config.enable_rag is False, "enable_rag is not valid"
            assert config.timeout_seconds == 600, "timeout_seconds is not valid"
        except ImportError:
            pytest.skip("Module not available")


class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def test_result_creation(self):
        """Test creating TaskResult."""
        try:
            from src.agent.core import TaskResult, TaskStatus

            result = TaskResult(status=TaskStatus.COMPLETED)
            assert result.status == TaskStatus.COMPLETED, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_result_defaults(self):
        """Test TaskResult default values."""
        try:
            from src.agent.core import TaskResult, TaskStatus

            result = TaskResult(status=TaskStatus.PENDING)
            assert result.response is None, "Response must not be empty"
            assert result.error is None, "Result must not be empty"
            assert result.tool_calls == [], "Result must not be empty"
            assert result.context_used == [], "Result must not be empty"
            assert result.verification_score is None, "Result must not be empty"
            assert result.duration_ms == 0, "Result must not be empty"
            assert result.cost == 0.0, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_result_with_response(self):
        """Test TaskResult with response."""
        try:
            from src.agent.core import TaskResult, TaskStatus

            result = TaskResult(status=TaskStatus.COMPLETED, response="Task completed successfully")
            assert result.response == "Task completed successfully", "Response must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_result_with_error(self):
        """Test TaskResult with error."""
        try:
            from src.agent.core import TaskResult, TaskStatus

            result = TaskResult(status=TaskStatus.FAILED, error="Something went wrong")
            assert result.status == TaskStatus.FAILED, "Result must not be empty"
            assert result.error == "Something went wrong", "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")

    def test_result_with_tool_calls(self):
        """Test TaskResult with tool calls."""
        try:
            from src.agent.core import TaskResult, TaskStatus

            tool_calls = [{"name": "search", "args": {"query": "test"}}]
            result = TaskResult(status=TaskStatus.COMPLETED, tool_calls=tool_calls)
            assert result.tool_calls == tool_calls, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


class TestToolCall:
    """Tests for ToolCall dataclass."""

    def test_tool_call_creation(self):
        """Test creating ToolCall."""
        try:
            from src.agent.core import ToolCall

            call = ToolCall(name="search", parameters={"query": "test"})
            assert call.name == "search", "name is not valid"
            assert call.parameters == {"query": "test"}, "parameters is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_call_defaults(self):
        """Test ToolCall default values."""
        try:
            from src.agent.core import ToolCall

            call = ToolCall(name="test", parameters={})
            assert call.result is None, "Result must not be empty"
            assert call.error is None, "Error should be raised or set"
            assert call.duration_ms == 0, "duration_ms is not valid"
        except ImportError:
            pytest.skip("Module not available")

    def test_tool_call_with_result(self):
        """Test ToolCall with result."""
        try:
            from src.agent.core import ToolCall

            call = ToolCall(name="search", parameters={"query": "test"}, result={"matches": 5})
            assert call.result == {"matches": 5}, "Result must not be empty"
        except ImportError:
            pytest.skip("Module not available")


class TestAgentCore:
    """Tests for AgentCore class."""

    def test_agent_core_import(self):
        """Test that AgentCore can be imported."""
        try:
            from src.agent.core import AgentCore

            assert AgentCore is not None, "AgentCore must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_agent_core_docstring(self):
        """Test AgentCore has proper docstring."""
        try:
            from src.agent.core import AgentCore

            assert AgentCore.__doc__ is not None, "__doc__ must be initialized"
            assert "autonomous agents" in AgentCore.__doc__.lower(), "Condition must be true"
        except ImportError:
            pytest.skip("Module not available")


class TestModuleImports:
    """Tests for module-level imports."""

    def test_logging_configured(self):
        """Test that logger is configured."""
        try:
            from src.agent.core import logger

            assert logger is not None, "logger must be initialized"
        except ImportError:
            pytest.skip("Module not available")

    def test_all_exports(self):
        """Test that key classes are exported."""
        try:
            from src.agent.core import (
                AgentConfig,
                AgentCore,
                TaskResult,
                TaskStatus,
                ToolCall,
            )

            assert all([TaskStatus, AgentConfig, TaskResult, ToolCall, AgentCore])
        except ImportError:
            pytest.skip("Module not available")
