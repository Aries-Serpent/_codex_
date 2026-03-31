"""Shim for Zendesk RAG ticket context retrieval."""

from __future__ import annotations

from codex.zendesk.quantum import ZendeskTicket
from codex.zendesk.rag import ZendeskRAGBridge as CoreZendeskRAGBridge


class ZendeskRAGBridge:
    """Compatibility shim around the core Zendesk RAG bridge."""

    def __init__(self) -> None:
        self._bridge = CoreZendeskRAGBridge()

    def retrieve_ticket_context(self, query: str, tickets: list[ZendeskTicket], top_k: int = 5):
        return self._bridge.retrieve_ticket_context(query, tickets, top_k=top_k)


__all__ = ["ZendeskRAGBridge", "ZendeskTicket"]
