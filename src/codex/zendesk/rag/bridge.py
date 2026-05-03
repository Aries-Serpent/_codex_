"""Zendesk RAG bridge for quantum-enhanced retrieval."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass

from codex.zendesk.quantum import ZendeskTicket
from rag.pipelines.chunking import Chunk, ChunkingPipeline
from rag.pipelines.quantum_retrieval import QuantumEnhancedRetrieval

logger = logging.getLogger(__name__)


@dataclass
class TicketContext:
    """Context snippet derived from a Zendesk ticket."""

    ticket_id: int
    content: str
    score: float


class ZendeskRAGBridge:
    """Bridge Zendesk tickets into the quantum-enhanced RAG pipeline."""

    def __init__(
        self,
        *,
        retriever: QuantumEnhancedRetrieval | None = None,
        chunker: ChunkingPipeline | None = None,
    ) -> None:
        self.retriever = retriever or QuantumEnhancedRetrieval()
        self.chunker = chunker or ChunkingPipeline()
        logger.info("ZendeskRAGBridge initialized")

    def build_ticket_text(self, ticket: ZendeskTicket) -> str:
        """Compose a searchable text representation of a ticket."""
        return (
            f"Ticket {ticket.ticket_id}: {ticket.subject}\n"
            f"Priority: {ticket.priority}\n"
            f"SLA (hours): {ticket.sla_deadline}\n"
            f"Complexity: {ticket.complexity}\n"
        )

    def build_chunks(self, tickets: Iterable[ZendeskTicket]) -> list[Chunk]:
        """Create chunks for all tickets."""
        chunks: list[Chunk] = []
        for ticket in tickets:
            text = self.build_ticket_text(ticket)
            ticket_chunks = self.chunker.chunk_text(
                text,
                metadata={"ticket_id": ticket.ticket_id, "subject": ticket.subject},
            )
            chunks.extend(ticket_chunks)
        return chunks

    def retrieve_ticket_context(
        self,
        query: str,
        tickets: Iterable[ZendeskTicket],
        *,
        top_k: int = 5,
    ) -> list[TicketContext]:
        """Retrieve relevant ticket contexts for a query."""
        ticket_list = list(tickets)
        if not ticket_list:
            return []

        chunks = self.build_chunks(ticket_list)
        results = self.retriever.retrieve_from_chunks(query, chunks, top_k=top_k)

        contexts = [
            TicketContext(
                ticket_id=result.metadata.get("ticket_id", -1),
                content=result.content,
                score=result.score,
            )
            for result in results
        ]
        contexts.sort(key=lambda item: (-item.score, item.ticket_id))
        return contexts


__all__ = ["TicketContext", "ZendeskRAGBridge"]
