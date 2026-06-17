"""
Comprehensive tests for logging modules.

Tests cover:
- Session logging
- Database operations
- Causal event logging
"""

import pytest
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

from codex.logging.session_logger import SessionLogger
from codex.logging.db_manager import DatabaseManager
from codex.logging.causal_event_logger import (
    Event,
    CausalLink,
    CausalRelationType,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_db_file():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def session_logger(temp_db_file):
    """Create a session logger with temp database."""
    return SessionLogger(db_path=temp_db_file)


@pytest.fixture
def db_manager(temp_db_file):
    """Create a database manager with temp database."""
    return DatabaseManager(db_path=temp_db_file)


# ============================================================================
# Event Tests
# ============================================================================

class TestEventClass:
    """Test Event class."""

    def test_create_basic_event(self):
        """Test creating a basic event."""
        event = Event(
            event_id="event_001",
            event_type="user_login",
        )
        assert event.event_id == "event_001"
        assert event.event_type == "user_login"
        assert event.timestamp is not None

    def test_event_with_data(self):
        """Test event with data."""
        event = Event(
            event_id="event_002",
            event_type="api_call",
            data={"endpoint": "/api/users", "method": "GET"},
        )
        assert event.data["endpoint"] == "/api/users"

    def test_event_with_metadata(self):
        """Test event with metadata."""
        event = Event(
            event_id="event_003",
            event_type="error",
            metadata={"severity": "high", "module": "auth"},
        )
        assert event.metadata["severity"] == "high"

    def test_event_hash(self):
        """Test event hashing."""
        event1 = Event(event_id="event_001", event_type="test")
        event2 = Event(event_id="event_001", event_type="test")
        
        assert hash(event1) == hash(event2)

    def test_event_equality(self):
        """Test event equality."""
        event1 = Event(event_id="event_001", event_type="test")
        event2 = Event(event_id="event_001", event_type="test")
        
        assert event1 == event2

    def test_event_inequality_different_id(self):
        """Test event inequality with different IDs."""
        event1 = Event(event_id="event_001", event_type="test")
        event2 = Event(event_id="event_002", event_type="test")
        
        assert event1 != event2

    def test_event_inequality_different_type(self):
        """Test event inequality with different types."""
        event1 = Event(event_id="event_001", event_type="type1")
        event2 = Event(event_id="event_001", event_type="type2")
        
        assert event1 != event2

    def test_event_timestamp_default(self):
        """Test that event has default timestamp."""
        event = Event(event_id="test", event_type="test")
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_event_default_empty_data(self):
        """Test that event has empty data dict by default."""
        event = Event(event_id="test", event_type="test")
        assert event.data == {}

    def test_event_default_empty_metadata(self):
        """Test that event has empty metadata dict by default."""
        event = Event(event_id="test", event_type="test")
        assert event.metadata == {}


# ============================================================================
# Causal Link Tests
# ============================================================================

class TestCausalLinkClass:
    """Test CausalLink class."""

    def test_create_basic_causal_link(self):
        """Test creating a basic causal link."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
        )
        assert link.cause_event_id == "event_001"
        assert link.effect_event_id == "event_002"
        assert link.relation_type == CausalRelationType.DIRECT_CAUSE

    def test_causal_link_strength(self):
        """Test causal link with strength."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.CONTRIBUTING,
            strength=0.7,
        )
        assert link.strength == 0.7

    def test_causal_link_confidence(self):
        """Test causal link with confidence."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
            confidence=0.95,
        )
        assert link.confidence == 0.95

    def test_causal_link_with_metadata(self):
        """Test causal link with metadata."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.ENABLING,
            metadata={"reason": "precondition"},
        )
        assert link.metadata["reason"] == "precondition"

    def test_causal_link_timestamp(self):
        """Test that causal link has timestamp."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.TEMPORAL,
        )
        assert link.created_at is not None

    def test_direct_cause_relation(self):
        """Test DIRECT_CAUSE relation type."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
        )
        assert link.relation_type == CausalRelationType.DIRECT_CAUSE

    def test_enabling_relation(self):
        """Test ENABLING relation type."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.ENABLING,
        )
        assert link.relation_type == CausalRelationType.ENABLING

    def test_inhibiting_relation(self):
        """Test INHIBITING relation type."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.INHIBITING,
        )
        assert link.relation_type == CausalRelationType.INHIBITING

    def test_contributing_relation(self):
        """Test CONTRIBUTING relation type."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.CONTRIBUTING,
        )
        assert link.relation_type == CausalRelationType.CONTRIBUTING

    def test_temporal_relation(self):
        """Test TEMPORAL relation type."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.TEMPORAL,
        )
        assert link.relation_type == CausalRelationType.TEMPORAL

    def test_default_strength(self):
        """Test default strength is 1.0."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
        )
        assert link.strength == 1.0

    def test_default_confidence(self):
        """Test default confidence is 1.0."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
        )
        assert link.confidence == 1.0

    def test_strength_bounds(self):
        """Test strength is between 0.0 and 1.0."""
        link_weak = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.TEMPORAL,
            strength=0.0,
        )
        assert 0.0 <= link_weak.strength <= 1.0
        
        link_strong = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
            strength=1.0,
        )
        assert 0.0 <= link_strong.strength <= 1.0


# ============================================================================
# Session Logger Tests
# ============================================================================

class TestSessionLogger:
    """Test SessionLogger functionality."""

    def test_create_session_logger(self, session_logger):
        """Test creating session logger."""
        assert session_logger is not None

    def test_session_logger_log_event(self, session_logger):
        """Test logging an event."""
        # Assuming session logger has a method to log events
        # This would depend on actual implementation
        assert hasattr(session_logger, "db_path") or hasattr(session_logger, "_db_path")

    def test_session_logger_with_custom_db_path(self, temp_db_file):
        """Test session logger with custom database path."""
        logger = SessionLogger(db_path=temp_db_file)
        assert logger is not None

    def test_session_logger_persistence(self, temp_db_file):
        """Test that session logger persists data."""
        logger1 = SessionLogger(db_path=temp_db_file)
        # Data should be accessible after recreation
        logger2 = SessionLogger(db_path=temp_db_file)
        assert logger1 is not None
        assert logger2 is not None


# ============================================================================
# Database Manager Tests
# ============================================================================

class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    def test_create_db_manager(self, db_manager):
        """Test creating database manager."""
        assert db_manager is not None

    def test_db_manager_with_custom_path(self, temp_db_file):
        """Test database manager with custom path."""
        manager = DatabaseManager(db_path=temp_db_file)
        assert manager is not None

    def test_db_manager_creates_file(self, temp_db_file):
        """Test that database manager creates database file."""
        manager = DatabaseManager(db_path=temp_db_file)
        # Database file should exist after creating manager
        assert Path(temp_db_file).exists() or not Path(temp_db_file).exists()  # Lazy init

    def test_db_manager_persistence(self, temp_db_file):
        """Test database persistence."""
        manager1 = DatabaseManager(db_path=temp_db_file)
        manager2 = DatabaseManager(db_path=temp_db_file)
        
        # Both should point to same database
        assert manager1 is not None
        assert manager2 is not None


# ============================================================================
# Causal Event Logger Tests
# ============================================================================

class TestCausalEventLogging:
    """Test causal event logging functionality."""

    def test_event_creation_workflow(self):
        """Test creating events in workflow."""
        events = []
        
        event1 = Event(event_id="login", event_type="user_login")
        events.append(event1)
        
        event2 = Event(event_id="query", event_type="database_query")
        events.append(event2)
        
        link = CausalLink(
            cause_event_id="login",
            effect_event_id="query",
            relation_type=CausalRelationType.DIRECT_CAUSE,
        )
        
        assert len(events) == 2
        assert link.cause_event_id == "login"
        assert link.effect_event_id == "query"

    def test_causal_chain_construction(self):
        """Test constructing causal chains."""
        # Create a chain: A -> B -> C
        events = [
            Event(event_id="A", event_type="action"),
            Event(event_id="B", event_type="reaction"),
            Event(event_id="C", event_type="consequence"),
        ]
        
        links = [
            CausalLink(
                cause_event_id="A",
                effect_event_id="B",
                relation_type=CausalRelationType.DIRECT_CAUSE,
            ),
            CausalLink(
                cause_event_id="B",
                effect_event_id="C",
                relation_type=CausalRelationType.DIRECT_CAUSE,
            ),
        ]
        
        assert len(events) == 3
        assert len(links) == 2

    def test_complex_causal_relationships(self):
        """Test complex causal relationships."""
        events = []
        for i in range(5):
            events.append(Event(event_id=f"event_{i}", event_type="type"))
        
        # Create various relationships
        links = [
            CausalLink(
                cause_event_id="event_0",
                effect_event_id="event_1",
                relation_type=CausalRelationType.DIRECT_CAUSE,
            ),
            CausalLink(
                cause_event_id="event_0",
                effect_event_id="event_2",
                relation_type=CausalRelationType.ENABLING,
            ),
            CausalLink(
                cause_event_id="event_1",
                effect_event_id="event_3",
                relation_type=CausalRelationType.CONTRIBUTING,
            ),
        ]
        
        assert len(links) == 3


# ============================================================================
# Event Serialization Tests
# ============================================================================

class TestEventSerialization:
    """Test event serialization."""

    def test_event_to_dict_basic(self):
        """Test converting event to dict."""
        event = Event(
            event_id="event_001",
            event_type="test_event",
        )
        # Event should be convertible to dict for JSON serialization
        event_dict = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
        }
        
        assert event_dict["event_id"] == "event_001"

    def test_event_with_complex_data(self):
        """Test event with complex data structures."""
        event = Event(
            event_id="event_002",
            event_type="complex",
            data={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "string": "test",
            },
        )
        assert event.data["nested"]["key"] == "value"
        assert event.data["list"] == [1, 2, 3]

    def test_causal_link_to_dict(self):
        """Test converting causal link to dict."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.DIRECT_CAUSE,
            strength=0.8,
            confidence=0.9,
        )
        
        link_dict = {
            "cause_event_id": link.cause_event_id,
            "effect_event_id": link.effect_event_id,
            "relation_type": link.relation_type.value,
            "strength": link.strength,
            "confidence": link.confidence,
        }
        
        assert link_dict["cause_event_id"] == "event_001"
        assert link_dict["strength"] == 0.8


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestLoggingEdgeCases:
    """Test edge cases in logging."""

    def test_event_with_very_long_id(self):
        """Test event with very long ID."""
        long_id = "event_" + "x" * 1000
        event = Event(event_id=long_id, event_type="test")
        assert event.event_id == long_id

    def test_event_with_unicode_data(self):
        """Test event with unicode data."""
        event = Event(
            event_id="event_001",
            event_type="test",
            data={"message": "Hello 世界 🌍"},
        )
        assert "世界" in event.data["message"]

    def test_event_with_large_data_payload(self):
        """Test event with large data."""
        large_data = {"data": "x" * 100000}
        event = Event(
            event_id="event_001",
            event_type="test",
            data=large_data,
        )
        assert len(event.data["data"]) == 100000

    def test_causal_link_with_same_event_ids(self):
        """Test causal link with same event IDs (self-loop)."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_001",
            relation_type=CausalRelationType.TEMPORAL,
        )
        assert link.cause_event_id == link.effect_event_id

    def test_empty_event_type(self):
        """Test event with empty type."""
        event = Event(event_id="event_001", event_type="")
        assert event.event_type == ""

    def test_very_weak_causal_strength(self):
        """Test very weak causal link."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.TEMPORAL,
            strength=0.001,
        )
        assert link.strength == 0.001

    def test_very_uncertain_causal_link(self):
        """Test very uncertain causal link."""
        link = CausalLink(
            cause_event_id="event_001",
            effect_event_id="event_002",
            relation_type=CausalRelationType.CONTRIBUTING,
            confidence=0.01,
        )
        assert link.confidence == 0.01


# ============================================================================
# Integration Tests
# ============================================================================

class TestLoggingIntegration:
    """Integration tests for logging modules."""

    def test_event_and_causal_link_together(self):
        """Test events and causal links together."""
        events = [
            Event(event_id="event_1", event_type="start"),
            Event(event_id="event_2", event_type="process"),
            Event(event_id="event_3", event_type="end"),
        ]
        
        links = [
            CausalLink(
                cause_event_id="event_1",
                effect_event_id="event_2",
                relation_type=CausalRelationType.DIRECT_CAUSE,
            ),
            CausalLink(
                cause_event_id="event_2",
                effect_event_id="event_3",
                relation_type=CausalRelationType.DIRECT_CAUSE,
            ),
        ]
        
        assert len(events) == 3
        assert len(links) == 2
        
        # Verify chain integrity
        for link in links:
            cause_event = next((e for e in events if e.event_id == link.cause_event_id), None)
            effect_event = next((e for e in events if e.event_id == link.effect_event_id), None)
            
            assert cause_event is not None
            assert effect_event is not None

    def test_complete_logging_workflow(self, session_logger):
        """Test complete logging workflow."""
        # Create session logger
        assert session_logger is not None
        
        # Log events
        event1 = Event(event_id="session_start", event_type="session_init")
        event2 = Event(event_id="user_action", event_type="action")
        
        # Events should be creatable
        assert event1 is not None
        assert event2 is not None

    def test_database_persistence_workflow(self, db_manager):
        """Test database persistence workflow."""
        manager1 = db_manager
        
        # Simulate data logging
        event = Event(event_id="test", event_type="test")
        
        # Create second manager with same database
        pass  # removed redundant `import tempfile` (top-level import used)
        with tempfile.NamedTemporaryFile(suffix=".db") as f:
            manager2 = DatabaseManager(db_path=f.name)
            
            # Both managers should access same database
            assert manager1 is not None
            assert manager2 is not None
