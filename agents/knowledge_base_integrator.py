"""Shim for Zendesk knowledge base integration."""

from __future__ import annotations

from src.codex.zendesk.rag import ZendeskRAGBridge


def build_context(query: str, tickets, top_k: int = 5):
    """Retrieve ticket context for a query."""
    bridge = ZendeskRAGBridge()
    return bridge.retrieve_ticket_context(query, tickets, top_k=top_k)


__all__ = ["build_context", "ZendeskRAGBridge"]
