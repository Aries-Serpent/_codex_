"""
Tests for agents.semantic_ticket_search module.

This module contains tests for the Zendesk semantic ticket search shim.
"""

from unittest.mock import MagicMock, patch

import pytest

# Skip all tests if pydantic is not available (required by zendesk modules)
pydantic = pytest.importorskip("pydantic")


class TestSemanticSearch:
    """Tests for semantic_search function."""

    @patch("agents.semantic_ticket_search.ZendeskRAGBridge")
    def test_semantic_search_calls_bridge(self, MockBridge):
        """Test semantic_search calls bridge correctly."""
        from agents.semantic_ticket_search import semantic_search

        mock_bridge = MagicMock()
        mock_bridge.retrieve_ticket_context.return_value = ["result1", "result2"]
        MockBridge.return_value = mock_bridge

        tickets = [MagicMock(), MagicMock()]
        result = semantic_search("test query", tickets)

        MockBridge.assert_called_once()
        mock_bridge.retrieve_ticket_context.assert_called_once_with("test query", tickets, top_k=5)
        assert result == ["result1", "result2"]

    @patch("agents.semantic_ticket_search.ZendeskRAGBridge")
    def test_semantic_search_custom_top_k(self, MockBridge):
        """Test semantic_search with custom top_k."""
        from agents.semantic_ticket_search import semantic_search

        mock_bridge = MagicMock()
        mock_bridge.retrieve_ticket_context.return_value = []
        MockBridge.return_value = mock_bridge

        semantic_search("query", [], top_k=10)

        mock_bridge.retrieve_ticket_context.assert_called_once_with("query", [], top_k=10)


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from agents.semantic_ticket_search import __all__

        assert "semantic_search" in __all__, "Condition must be true"
        assert "ZendeskRAGBridge" in __all__, "Condition must be true"
