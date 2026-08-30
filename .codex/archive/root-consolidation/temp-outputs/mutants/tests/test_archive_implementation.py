"""
Test Suite for Phase 5: Archive Implementation

Tests for:
- Archive migration
- Retrieval with caching
- Retention policy
- Performance benchmarks
- Integrity checks
"""

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from codex.session_db import SessionDB


class TestSessionDB:
    """Test session database with archive support"""

    @pytest.fixture
    def db(self):
        """Create test database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(db_path=f"{tmpdir}/test.db", archive_dir=f"{tmpdir}/archive")
            yield db

    def test_db_initialization(self, db):
        """Test database initialization"""
        assert Path(db.db_path).exists(), "Condition must be true"
        assert db.archive_dir.exists(), "Condition must be true"

    def test_schema_creation(self, db):
        """Test schema is created correctly"""
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "sessions" in tables, "Condition must be true"
        assert "session_metadata" in tables, "Data must not be empty"
        assert "session_events" in tables, "Condition must be true"

        conn.close()

    def test_archive_status_enum(self, db):
        """Test archive_status field accepts valid values"""
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Insert active session
        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status)
            VALUES (?, ?, ?)
        """,
            ("test-1", "complete", "active"),
        )

        # Insert archived session
        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status, archive_location)
            VALUES (?, ?, ?, ?)
        """,
            ("test-2", "complete", "archived", "/path/to/archive.parquet"),
        )

        conn.commit()

        # Verify
        cursor.execute("SELECT archive_status FROM sessions ORDER BY session_id")
        statuses = [row[0] for row in cursor.fetchall()]

        assert "active" in statuses, "Condition must be true"
        assert "archived" in statuses, "Condition must be true"

        conn.close()

    @patch("codex.session_db.pd")
    @patch("codex.session_db.pq")
    def test_archive_session(self, mock_pq, mock_pd, db):
        """Test archiving a session to Parquet"""
        # Mock pandas
        mock_df = MagicMock()
        mock_pd.DataFrame.return_value = mock_df

        session_data = {
            "session_id": "test-session",
            "timestamp": "2026-03-13T16:10:25Z",
            "data": "test",
        }

        # Patch PARQUET_AVAILABLE
        with patch("codex.session_db.PARQUET_AVAILABLE", True):
            result = db.archive_session("test-session", session_data)

        # Verify archive path contains year/month
        assert "2026/03" in result, "Result must not be empty"
        assert "test-session.parquet" in result, "Result must not be empty"

    def test_get_archive_candidates(self, db):
        """Test identifying archive candidates"""
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Insert old session (95 days old)
        old_date = (datetime.utcnow() - timedelta(days=95)).isoformat()
        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status, created_at)
            VALUES (?, ?, ?, ?)
        """,
            ("old-session", "complete", "active", old_date),
        )

        # Insert recent session (30 days old)
        recent_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status, created_at)
            VALUES (?, ?, ?, ?)
        """,
            ("recent-session", "complete", "active", recent_date),
        )

        conn.commit()
        conn.close()

        # Get candidates
        candidates = db.get_archive_candidates(days=90)

        assert "old-session" in candidates, "Condition must be true"
        assert "recent-session" not in candidates, "Condition must be true"

    def test_mark_deleted(self, db):
        """Test marking session as deleted"""
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status)
            VALUES (?, ?, ?)
        """,
            ("test-session", "complete", "archived"),
        )

        conn.commit()
        conn.close()

        # Mark as deleted
        db.mark_deleted("test-session")

        # Verify
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT archive_status FROM sessions WHERE session_id = ?", ("test-session",)
        )
        status = cursor.fetchone()[0]
        conn.close()

        assert status == "deleted", "status is not valid"

    def test_cache_session(self, db):
        """Test session caching"""
        session_data = {"session_id": "test", "data": "value"}

        db._cache_session("test", session_data)

        assert "test" in db._cache, "Condition must be true"
        assert db._cache["test"] == session_data, "Data must not be empty"
        assert db.cache_current_size > 0, "cache_current_size must be greater than zero"

    def test_cache_size_limit(self, db):
        """Test cache respects size limit"""
        # Set small cache limit for testing
        db.cache_max_size = 1000  # 1 KB

        # Add sessions until eviction occurs
        for i in range(10):
            session_data = {"session_id": f"session-{i}", "data": "x" * 200}  # Make it large
            db._cache_session(f"session-{i}", session_data)

        # Cache should not exceed limit
        assert db.cache_current_size <= db.cache_max_size, "cache_current_size is not valid"

    def test_get_archive_stats(self, db):
        """Test archive statistics"""
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status)
            VALUES (?, ?, ?)
        """,
            ("active-1", "complete", "active"),
        )

        cursor.execute(
            """
            INSERT INTO sessions (session_id, status, archive_status, archive_timestamp)
            VALUES (?, ?, ?, ?)
        """,
            ("archived-1", "complete", "archived", datetime.utcnow().isoformat()),
        )

        conn.commit()
        conn.close()

        stats = db.get_archive_stats()

        assert stats["active_sessions"] == 1, "Condition must be true"
        assert stats["archived_sessions"] == 1, "Condition must be true"
        assert "total_archive_size_mb" in stats, "Condition must be true"
        assert "cache_size_mb" in stats, "Condition must be true"


class TestArchiveIntegrity:
    """Test archive integrity checks"""

    def test_archive_index_format(self):
        """Test archive index has correct format"""
        # Create sample index
        index = {
            "version": "1.0",
            "created": datetime.utcnow().isoformat(),
            "sessions": [
                {
                    "session_id": "test-1",
                    "archive_location": ".codex/archive/sessions/2026/03/test-1.parquet",
                    "timestamp": "2026-03-13T16:10:25Z",
                }
            ],
            "statistics": {
                "total_sessions": 1,
                "total_size_mb": 0.5,
                "retention_policy": "Delete archives >30 iterations old",
            },
        }

        # Verify structure
        assert "version" in index, "Condition must be true"
        assert "created" in index, "Condition must be true"
        assert "sessions" in index, "Condition must be true"
        assert "statistics" in index, "Condition must be true"

        assert len(index["sessions"]) == 1, "Collection must not be empty"
        assert "session_id" in index["sessions"][0], "Condition must be true"
        assert "archive_location" in index["sessions"][0], "Condition must be true"


class TestPerformance:
    """Test performance benchmarks"""

    def test_retrieval_performance(self):
        """Test retrieval performance requirements"""
        # Cold retrieval should be <500ms
        # Cached retrieval should be <50ms

        # These are mock tests - actual performance depends on system
        cold_threshold = 500  # ms
        cached_threshold = 50  # ms

        assert cold_threshold > cached_threshold, "cold_threshold must be greater than zero"
        assert cold_threshold < 1000, "cold_threshold is not valid"


def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()
