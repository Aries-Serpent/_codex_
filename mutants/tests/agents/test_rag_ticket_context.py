"""
Tests for agents.rag_ticket_context module.

This module contains tests for the Zendesk RAG ticket context shim.
"""

from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if pydantic is not available (required by zendesk modules)
pydantic = pytest.importorskip("pydantic")


class TestZendeskRAGBridge:
    """Tests for ZendeskRAGBridge shim class."""

    @patch("agents.rag_ticket_context.CoreZendeskRAGBridge")
    def test_init_creates_bridge(self, MockCoreBridge):
        """Test __init__ creates core bridge."""
        from agents.rag_ticket_context import ZendeskRAGBridge

        MockCoreBridge.return_value = MagicMock()

        bridge = ZendeskRAGBridge()

        MockCoreBridge.assert_called_once()
        assert bridge._bridge is not None, "_bridge must be initialized"

    @patch("agents.rag_ticket_context.CoreZendeskRAGBridge")
    def test_retrieve_ticket_context(self, MockCoreBridge):
        """Test retrieve_ticket_context delegates to core bridge."""
        from agents.rag_ticket_context import ZendeskRAGBridge

        mock_core = MagicMock()
        mock_core.retrieve_ticket_context.return_value = ["context1"]
        MockCoreBridge.return_value = mock_core

        bridge = ZendeskRAGBridge()
        tickets = [MagicMock()]
        result = bridge.retrieve_ticket_context("query", tickets, top_k=3)

        mock_core.retrieve_ticket_context.assert_called_once_with("query", tickets, top_k=3)
        assert result == ["context1"], "Result must not be empty"


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from agents.rag_ticket_context import __all__

        assert "ZendeskRAGBridge" in __all__, "Condition must be true"
        assert "ZendeskTicket" in __all__, "Condition must be true"
