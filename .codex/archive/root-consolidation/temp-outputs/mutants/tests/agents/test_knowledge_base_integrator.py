"""
Tests for agents.knowledge_base_integrator module.

This module contains tests for the Zendesk knowledge base integration shim.
"""

from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if pydantic is not available (required by zendesk modules)
pydantic = pytest.importorskip("pydantic")


class TestBuildContext:
    """Tests for build_context function."""

    @patch("agents.knowledge_base_integrator.ZendeskRAGBridge")
    def test_build_context_calls_bridge(self, MockBridge):
        """Test build_context calls bridge correctly."""
        from agents.knowledge_base_integrator import build_context

        mock_bridge = MagicMock()
        mock_bridge.retrieve_ticket_context.return_value = ["ctx1", "ctx2"]
        MockBridge.return_value = mock_bridge

        tickets = [MagicMock()]
        result = build_context("query", tickets)

        MockBridge.assert_called_once()
        mock_bridge.retrieve_ticket_context.assert_called_once_with("query", tickets, top_k=5)
        assert result == ["ctx1", "ctx2"]

    @patch("agents.knowledge_base_integrator.ZendeskRAGBridge")
    def test_build_context_custom_top_k(self, MockBridge):
        """Test build_context with custom top_k."""
        from agents.knowledge_base_integrator import build_context

        mock_bridge = MagicMock()
        mock_bridge.retrieve_ticket_context.return_value = []
        MockBridge.return_value = mock_bridge

        build_context("query", [], top_k=20)

        mock_bridge.retrieve_ticket_context.assert_called_once_with("query", [], top_k=20)


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from agents.knowledge_base_integrator import __all__

        assert "build_context" in __all__, "Condition must be true"
        assert "ZendeskRAGBridge" in __all__, "Condition must be true"
