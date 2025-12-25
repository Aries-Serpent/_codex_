"""Shim for Zendesk semantic ticket search."""

from __future__ import annotations

from codex.zendesk.rag import ZendeskRAGBridge


def semantic_search(query: str, tickets, top_k: int = 5):
    """Run semantic search over Zendesk tickets."""
    bridge = ZendeskRAGBridge()
    return bridge.retrieve_ticket_context(query, tickets, top_k=top_k)


__all__ = ["semantic_search", "ZendeskRAGBridge"]
