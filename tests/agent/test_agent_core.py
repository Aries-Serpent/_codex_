"""Tests for Agent Core components."""

from __future__ import annotations

import pytest


class TestAgentCore:
    """Test suite for AgentCore."""

    @pytest.fixture
    def agent(self):
        """Create an agent for testing."""
        from agent.core import AgentCore

        return AgentCore()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.config is not None, "config must be initialized"
        assert agent.get_available_tools() == [], "Condition must be true"

    def test_register_tool(self, agent):
        """Test registering a tool."""

        def echo_tool(text: str) -> str:
            return text

        agent.register_tool("echo", echo_tool)

        assert "echo" in agent.get_available_tools(), "Condition must be true"

    def test_register_tool_invalid_name(self, agent):
        """Test registering tool with invalid name."""
        with pytest.raises(ValueError):
            agent.register_tool("", lambda: None)

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_empty_task(self, agent):
        """Test executing empty task."""
        result = await agent.execute("")

        assert result.status.value == "failed", "Result must not be empty"
        assert result.error is not None, "error must be initialized"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_execute_simple_task(self, agent):
        """Test executing a simple task."""
        result = await agent.execute("Test task")

        assert result.status.value in ["completed", "verified", "unknown"]
        assert result.duration_ms >= 0, "duration_ms must be greater than zero"

    def test_get_stats(self, agent):
        """Test getting agent stats."""
        agent.register_tool("test", lambda: None)

        stats = agent.get_stats()

        assert stats["registered_tools"] == 1, "Condition must be true"
        assert "config" in stats, "Condition must be true"


class TestMockAdapter:
    """Test MockAdapter for agent."""

    @pytest.fixture
    def adapter(self):
        """Create a mock adapter."""
        from agent.adapters.mock_adapter import MockAdapter

        return MockAdapter()

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_complete(self, adapter):
        """Test completion with mock adapter."""
        from agent.adapters.base_adapter import CompletionRequest

        request = CompletionRequest(prompt="Hello")
        response = await adapter.complete(request)

        assert response.content is not None, "content must be initialized"
        assert response.model is not None, "model must be initialized"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_health_check(self, adapter):
        """Test health check always returns True."""
        healthy = await adapter.health_check()
        assert healthy is True, "healthy is not valid"

    def test_provider_name(self, adapter):
        """Test provider name."""
        assert adapter.provider_name == "mock", "provider_name is not valid"
