"""Unit tests for Zendesk Ticket model."""

import pytest

from src.codex.zendesk.model.ticket import (
    Ticket,
    TicketComment,
    TicketCustomField,
)


class TestTicketComment:
    """Test TicketComment model."""
    
    def test_create_comment(self):
        """Test creating a basic comment."""
        comment = TicketComment(
            author_id=12345,
            body="This is a test comment",
            public=True,
        )
        assert comment.author_id == 12345
        assert comment.body == "This is a test comment"
        assert comment.public is True


class TestTicket:
    """Test Ticket model."""
    
    def test_create_minimal_ticket(self):
        """Test creating a ticket with minimal required fields."""
        ticket = Ticket(
            subject="Test ticket",
            description="Test description",
            requester_id=12345,
        )
        assert ticket.subject == "Test ticket"
        assert ticket.description == "Test description"
        assert ticket.requester_id == 12345
        assert ticket.status == "new"  # Default value
    
    def test_ticket_with_all_fields(self):
        """Test creating a ticket with all fields populated."""
        comment = TicketComment(
            author_id=12345,
            body="Initial comment",
            public=True,
        )
        
        custom_field = TicketCustomField(
            id=123,
            value="custom_value",
        )
        
        ticket = Ticket(
            id=99999,
            subject="Full test ticket",
            description="Full description",
            requester_id=12345,
            assignee_id=67890,
            group_id=111,
            status="open",
            priority="high",
            tags=["test", "urgent"],
            custom_fields=[custom_field],
            comment=comment,
        )
        
        assert ticket.id == 99999
        assert ticket.status == "open"
        assert ticket.priority == "high"
        assert len(ticket.tags) == 2
        assert len(ticket.custom_fields) == 1
        assert ticket.comment.body == "Initial comment"
    
    def test_to_api_payload_create(self):
        """Test API payload generation for ticket creation."""
        comment = TicketComment(
            author_id=12345,
            body="Creating a ticket",
            public=True,
        )
        
        ticket = Ticket(
            subject="New ticket",
            description="Ticket description",
            requester_id=12345,
            priority="high",
            tags=["api", "test"],
            comment=comment,
        )
        
        payload = ticket.to_api_payload(for_create=True)
        
        assert "ticket" in payload
        assert payload["ticket"]["subject"] == "New ticket"
        assert payload["ticket"]["priority"] == "high"
        assert "comment" in payload["ticket"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
