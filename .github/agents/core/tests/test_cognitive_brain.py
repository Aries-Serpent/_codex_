"""
Tests for CognitiveBrain.
"""
import pytest
import tempfile
from pathlib import Path
from ..cognitive_brain import CognitiveBrain


@pytest.fixture
def temp_brain():
    """Create temporary brain for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_brain.db"
        yield CognitiveBrain(db_path)


def test_brain_initialization(temp_brain):
    """Test brain initialization and schema creation."""
    assert temp_brain.db_path.exists()
    
    # Check that tables exist
    with temp_brain._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        tables = {row["name"] for row in cursor.fetchall()}
        
        assert "sessions" in tables
        assert "patterns" in tables
        assert "lessons" in tables
        assert "decisions" in tables


def test_session_lifecycle(temp_brain):
    """Test session start and end."""
    temp_brain.start_session(
        session_id="test-001",
        agent_name="test-agent",
        agent_version="1.0.0",
        task_type="test"
    )
    
    temp_brain.end_session(
        session_id="test-001",
        status="success",
        metrics={"metric1": 100}
    )
    
    # Verify session exists
    history = temp_brain.get_session_history(agent_name="test-agent", limit=1)
    assert len(history) == 1
    assert history[0]["session_id"] == "test-001"
    assert history[0]["status"] == "success"
    assert history[0]["metrics"]["metric1"] == 100


def test_pattern_recording(temp_brain):
    """Test pattern recording and retrieval."""
    temp_brain.start_session(
        "test-001", "test-agent", "1.0.0", "test"
    )
    
    # Record pattern
    pattern_id = temp_brain.record_pattern(
        session_id="test-001",
        pattern_name="test_pattern",
        pattern_type="test",
        description="Test pattern description"
    )
    
    assert pattern_id > 0
    
    # Record same pattern again (should increment count)
    pattern_id2 = temp_brain.record_pattern(
        session_id="test-001",
        pattern_name="test_pattern",
        pattern_type="test"
    )
    
    assert pattern_id2 == pattern_id
    
    # Get similar patterns
    patterns = temp_brain.get_similar_patterns("test", limit=10)
    assert len(patterns) > 0
    assert patterns[0]["pattern_name"] == "test_pattern"
    assert patterns[0]["occurrences"] == 2


def test_lesson_recording(temp_brain):
    """Test lesson recording and retrieval."""
    temp_brain.start_session(
        "test-001", "test-agent", "1.0.0", "test"
    )
    
    lesson_id = temp_brain.record_lesson(
        session_id="test-001",
        lesson_text="Test lesson",
        category="testing",
        confidence=0.9
    )
    
    assert lesson_id > 0
    
    # Get recent lessons
    lessons = temp_brain.get_recent_lessons(category="testing", limit=10)
    assert len(lessons) > 0
    assert lessons[0]["lesson_text"] == "Test lesson"
    assert lessons[0]["confidence"] == 0.9


def test_decision_recording(temp_brain):
    """Test decision recording."""
    temp_brain.start_session(
        "test-001", "test-agent", "1.0.0", "test"
    )
    
    decision_id = temp_brain.record_decision(
        session_id="test-001",
        context={"input": "data"},
        decision={"action": "test"},
        rationale="Test rationale",
        outcome={"result": "success"},
        success=True
    )
    
    assert decision_id > 0


def test_brain_stats(temp_brain):
    """Test brain statistics."""
    # Add some data
    temp_brain.start_session(
        "test-001", "test-agent", "1.0.0", "test"
    )
    temp_brain.record_pattern(
        "test-001", "pattern1", "type1"
    )
    temp_brain.record_lesson(
        "test-001", "lesson1", "category1"
    )
    temp_brain.end_session("test-001", "success")
    
    stats = temp_brain.get_stats()
    
    assert stats["total_sessions"] >= 1
    assert stats["total_patterns"] >= 1
    assert stats["total_lessons"] >= 1
    assert "database_path" in stats
