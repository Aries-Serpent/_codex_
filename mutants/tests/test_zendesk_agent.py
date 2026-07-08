"""Comprehensive test suite for zendesk agent module."""

from unittest.mock import Mock, patch

from src.codex.zendesk.agent import ZendeskAgentCore


class TestZendeskAgentCoreInitialization:
    """Test suite for ZendeskAgentCore initialization."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_init_default_config(self, mock_get_registry, mock_agent_core):
        """Test initialization with default config."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        assert agent is not None, "agent must be initialized"
        assert agent.core is not None, "core must be initialized"
        assert agent.tool_registry is not None, "tool_registry must be initialized"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_init_with_config(self, mock_get_registry, mock_agent_core):
        """Test initialization with custom config."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry
        mock_config = Mock()

        agent = ZendeskAgentCore(config=mock_config)
        assert agent is not None, "agent must be initialized"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_init_with_tool_registry(self, mock_get_registry, mock_agent_core):
        """Test initialization with custom tool registry."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []

        agent = ZendeskAgentCore(tool_registry=mock_registry)
        assert agent.tool_registry is mock_registry, "tool_registry is not valid"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_init_both_config_and_registry(self, mock_get_registry, mock_agent_core):
        """Test initialization with both config and registry."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_config = Mock()

        agent = ZendeskAgentCore(config=mock_config, tool_registry=mock_registry)
        assert agent.core is not None, "core must be initialized"
        assert agent.tool_registry is mock_registry, "tool_registry is not valid"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_init_syncs_tools(self, mock_get_registry, mock_agent_core):
        """Test that initialization syncs tools."""
        mock_tool1 = Mock()
        mock_tool1.name = "tool1"
        mock_tool1.handler = lambda: "tool1_result"

        mock_registry = Mock()
        mock_registry.list_tools.return_value = [mock_tool1]
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        # Verify _sync_tools was called indirectly
        assert agent.core.register_tool.called, "Condition must be true"


class TestZendeskAgentCoreSyncTools:
    """Test suite for _sync_tools method."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_sync_tools_empty(self, mock_get_registry, mock_agent_core):
        """Test syncing with no tools."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        ZendeskAgentCore()
        # Should not raise

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_sync_tools_single(self, mock_get_registry, mock_agent_core):
        """Test syncing with single tool."""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.handler = lambda: "result"

        mock_registry = Mock()
        mock_registry.list_tools.return_value = [mock_tool]
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        assert agent.core.register_tool.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_sync_tools_multiple(self, mock_get_registry, mock_agent_core):
        """Test syncing with multiple tools."""
        tools = []
        for i in range(5):
            tool = Mock()
            tool.name = f"tool_{i}"
            tool.handler = lambda x=i: f"result_{x}"
            tools.append(tool)

        mock_registry = Mock()
        mock_registry.list_tools.return_value = tools
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        assert agent.core.register_tool.call_count >= 5, "call_count must be positive"


class TestZendeskAgentCoreRegisterTool:
    """Test suite for register_tool method."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_register_tool_basic(self, mock_get_registry, mock_agent_core):
        """Test registering a tool."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        def handler():
            return "result"
        agent.register_tool("test_tool", handler)

        # Verify tool was registered in registry
        assert mock_registry.register.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_register_tool_registers_in_core(self, mock_get_registry, mock_agent_core):
        """Test that register_tool registers in core agent."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        def handler():
            return "result"
        agent.register_tool("test_tool", handler)

        # Verify tool was registered in core
        assert agent.core.register_tool.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_register_tool_registers_in_registry(self, mock_get_registry, mock_agent_core):
        """Test that register_tool registers in registry."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        def handler():
            return "result"
        agent.register_tool("test_tool", handler)

        # Verify tool was registered in registry
        assert mock_registry.register.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_register_multiple_tools(self, mock_get_registry, mock_agent_core):
        """Test registering multiple tools."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        for i in range(5):
            def handler(x=i):
                return f"result_{x}"
            agent.register_tool(f"tool_{i}", handler)

        # All tools should be registered
        assert agent.core.register_tool.call_count >= 5, "call_count must be positive"


class TestZendeskAgentCoreGetToolNames:
    """Test suite for get_tool_names method."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_get_tool_names_empty(self, mock_get_registry, mock_agent_core):
        """Test getting tool names with no tools."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_registry.get_tool_names.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        names = agent.get_tool_names()
        assert names == [], "names is not valid"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_get_tool_names_single(self, mock_get_registry, mock_agent_core):
        """Test getting single tool name."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_registry.get_tool_names.return_value = ["tool1"]
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        names = agent.get_tool_names()
        assert "tool1" in names, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_get_tool_names_multiple(self, mock_get_registry, mock_agent_core):
        """Test getting multiple tool names."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        tool_names = ["tool1", "tool2", "tool3"]
        mock_registry.get_tool_names.return_value = tool_names
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        names = agent.get_tool_names()
        assert len(names) == 3, "Names must not be empty"
        for name in tool_names:
            assert name in names, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_get_tool_names_is_list(self, mock_get_registry, mock_agent_core):
        """Test that get_tool_names returns a list."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_registry.get_tool_names.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        names = agent.get_tool_names()
        assert isinstance(names, list)


class TestZendeskAgentCoreToolRegistry:
    """Test suite for tool registry interaction."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_tool_registry_attribute(self, mock_get_registry, mock_agent_core):
        """Test that tool_registry attribute is set."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        assert hasattr(agent, "tool_registry")
        assert agent.tool_registry is mock_registry, "tool_registry is not valid"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_tool_registry_get_registry_called(self, mock_get_registry, mock_agent_core):
        """Test that get_registry is called during init."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        ZendeskAgentCore()
        assert mock_get_registry.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_tool_registry_custom_provided(self, mock_get_registry, mock_agent_core):
        """Test custom registry is used when provided."""
        custom_registry = Mock()
        custom_registry.list_tools.return_value = []

        agent = ZendeskAgentCore(tool_registry=custom_registry)
        assert agent.tool_registry is custom_registry, "tool_registry is not valid"
        # get_registry should not be called if custom registry provided
        assert not mock_get_registry.called, "Condition must be true"


class TestZendeskAgentCoreAgentCore:
    """Test suite for AgentCore interaction."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_agent_core_attribute(self, mock_get_registry, mock_agent_core):
        """Test that core attribute is set."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        assert hasattr(agent, "core")
        assert agent.core is not None, "core must be initialized"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_agent_core_created_with_config(self, mock_get_registry, mock_agent_core):
        """Test that AgentCore is created with config."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry
        mock_config = Mock()

        ZendeskAgentCore(config=mock_config)
        mock_agent_core.assert_called_with(config=mock_config)

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_agent_core_tools_synced(self, mock_get_registry, mock_agent_core):
        """Test that tools are synced to AgentCore."""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.handler = Mock()

        mock_registry = Mock()
        mock_registry.list_tools.return_value = [mock_tool]
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        # register_tool should have been called
        assert agent.core.register_tool.called, "Condition must be true"


class TestZendeskAgentCoreIntegration:
    """Integration tests for ZendeskAgentCore."""

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_create_and_register_tool(self, mock_get_registry, mock_agent_core):
        """Test creating agent and registering a tool."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        agent.register_tool("custom_tool", lambda: "custom_result")

        # Verify tool was registered
        assert agent.core.register_tool.called, "Condition must be true"
        assert mock_registry.register.called, "Condition must be true"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_get_tools_after_register(self, mock_get_registry, mock_agent_core):
        """Test getting tool names after registration."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_registry.get_tool_names.return_value = ["tool1", "tool2"]
        mock_get_registry.return_value = mock_registry

        agent = ZendeskAgentCore()
        agent.register_tool("tool1", lambda: "result1")

        names = agent.get_tool_names()
        assert len(names) >= 1, "Names must not be empty"

    @patch("src.codex.zendesk.agent.AgentCore")
    @patch("src.codex.zendesk.agent.get_registry")
    def test_multiple_agent_instances(self, mock_get_registry, mock_agent_core):
        """Test creating multiple agent instances."""
        mock_registry = Mock()
        mock_registry.list_tools.return_value = []
        mock_get_registry.return_value = mock_registry

        agent1 = ZendeskAgentCore()
        agent2 = ZendeskAgentCore()

        assert agent1 is not agent2, "agent1 is not valid"
        assert agent1.core is not agent2.core, "core is not valid"


class TestZendeskAgentCoreExports:
    """Test suite for module exports."""

    def test_agent_config_exported(self):
        """Test that AgentConfig is exported."""
        from src.codex.zendesk.agent import AgentConfig

        assert AgentConfig is not None, "AgentConfig must be initialized"

    def test_agent_core_exported(self):
        """Test that AgentCore is exported."""
        from src.codex.zendesk.agent import AgentCore

        assert AgentCore is not None, "AgentCore must be initialized"

    def test_zendesk_agent_core_exported(self):
        """Test that ZendeskAgentCore is exported."""
        from src.codex.zendesk.agent import ZendeskAgentCore

        assert ZendeskAgentCore is not None, "ZendeskAgentCore must be initialized"

    def test_all_exports(self):
        """Test that __all__ includes expected exports."""
        from src.codex.zendesk import agent

        if hasattr(agent, "__all__"):
            all_exports = agent.__all__
            assert "ZendeskAgentCore" in all_exports, "Condition must be true"
