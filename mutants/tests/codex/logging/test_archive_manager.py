"""
Tests for archive management system (Phase 5).

Coverage:
- Archive session extraction and storage
- Archive retrieval and caching
- Retention policy enforcement
- Archive index management
- Data integrity verification
"""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path  # pragma: allowlist secret

import pytest  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

# Conditionally import pandas for testing
pd = None
try:
    import pandas as pd
except ImportError:
    pass


@pytest.fixture
def temp_db_dir():
    """Create temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_db(temp_db_dir):
    """Create test SQLite database with schema."""
    db_path = temp_db_dir / "test_sessions.db"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create schema
    cursor.executescript("""
        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            pr_number INTEGER,
            branch TEXT,
            timestamp TEXT,
            git_sha TEXT,
            status TEXT NOT NULL,
            archive_status TEXT DEFAULT 'active',
            archive_location TEXT,
            archive_timestamp TEXT,
            agent_name TEXT,
            duration_minutes INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE session_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id),
            UNIQUE(session_id, key)
        );

        CREATE TABLE session_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );

        CREATE TABLE session_outcomes (
            session_id TEXT PRIMARY KEY,
            ci_checks_green INTEGER DEFAULT 0,
            ci_checks_red INTEGER DEFAULT 0,
            ci_checks_total INTEGER DEFAULT 0,
            test_coverage REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );

        CREATE INDEX idx_archive_status ON sessions(archive_status);
        CREATE INDEX idx_created_at ON sessions(created_at DESC);
    """)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def archive_dir(temp_db_dir):
    """Create test archive directory."""
    archive_path = temp_db_dir / "archive" / "sessions"
    archive_path.mkdir(parents=True, exist_ok=True)
    return archive_path


@pytest.fixture
def test_session_data():
    """Create test session data."""
    return {
        "session_id": "test-session-001",
        "pr_number": 123,
        "branch": "feature/test",
        "timestamp": "2026-03-15T10:00:00Z",
        "git_sha": "abc123def456",
        "status": "complete",
        "agent_name": "test-agent",
        "duration_minutes": 30,
        "created_at": "2026-03-15T10:00:00",
    }


def insert_test_session(db_path, session_data):
    """Insert test session into database."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO sessions
        (session_id, pr_number, branch, timestamp, git_sha, status, agent_name, duration_minutes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_data["session_id"],
            session_data.get("pr_number"),
            session_data.get("branch"),
            session_data.get("timestamp"),
            session_data.get("git_sha"),
            session_data.get("status", "complete"),
            session_data.get("agent_name"),
            session_data.get("duration_minutes"),
            session_data.get("created_at"),
        ),
    )

    conn.commit()
    conn.close()


@pytest.mark.skipif(pd is None, reason="pandas not installed")
class TestArchiveManager:
    """Test archive manager operations."""

    def test_identify_archive_candidates(self, test_db, archive_dir):
        """Test identifying sessions for archiving."""
        from codex.logging.archive_manager import ArchiveManager

        # Insert old session
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        insert_test_session(
            test_db,
            {
                "session_id": "old-session",
                "status": "complete",
                "created_at": old_date,
            },
        )

        # Insert recent session
        recent_date = datetime.now().isoformat()
        insert_test_session(
            test_db,
            {
                "session_id": "recent-session",
                "status": "complete",
                "created_at": recent_date,
            },
        )

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        candidates = manager.identify_archive_candidates(days=90)

        assert "old-session" in candidates, "Condition must be true"
        assert "recent-session" not in candidates, "Condition must be true"

    def test_archive_session(self, test_db, archive_dir, test_session_data):
        """Test archiving a session."""
        from codex.logging.archive_manager import ArchiveManager

        insert_test_session(test_db, test_session_data)

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        archived = manager.archive_session(test_session_data["session_id"])

        assert archived is not None, "archived must be initialized"
        assert archived.session_id == test_session_data["session_id"], "Data must not be empty"
        assert archived.file_size_bytes > 0, "file_size_bytes must be greater than zero"

        # Verify archive file exists
        archive_path = Path(archived.archive_location)
        assert archive_path.exists(), "Condition must be true"

        # Verify SQLite metadata updated
        conn = sqlite3.connect(str(test_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT archive_status, archive_location FROM sessions WHERE session_id = ?",
            (test_session_data["session_id"],),
        )
        row = cursor.fetchone()
        conn.close()

        assert row["archive_status"] == "archived", "Condition must be true"
        assert row["archive_location"] is not None, "Value must be initialized"

    def test_get_archived_session(self, test_db, archive_dir, test_session_data):
        """Test retrieving archived session."""
        from codex.logging.archive_manager import ArchiveManager

        insert_test_session(test_db, test_session_data)

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        manager.archive_session(test_session_data["session_id"])

        # Retrieve archived session
        retrieved = manager.get_archived_session(test_session_data["session_id"])

        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved["session_id"] == test_session_data["session_id"], "Data must not be empty"

    def test_cache_performance(self, test_db, archive_dir, test_session_data):
        """Test LRU caching improves retrieval performance."""
        import time

        from codex.logging.archive_manager import ArchiveManager

        insert_test_session(test_db, test_session_data)

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        manager.archive_session(test_session_data["session_id"])

        # First retrieval (cold, should load from Parquet)
        start = time.time()
        manager.get_archived_session(test_session_data["session_id"])
        cold_time = time.time() - start

        # Second retrieval (warm, should come from cache)
        start = time.time()
        manager.get_archived_session(test_session_data["session_id"])
        warm_time = time.time() - start

        # Cached retrieval should be faster
        assert warm_time < cold_time, "warm_time is not valid"

    def test_update_archive_index(self, test_db, archive_dir, test_session_data):
        """Test building archive index."""
        from codex.logging.archive_manager import ArchiveManager

        insert_test_session(test_db, test_session_data)

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        manager.archive_session(test_session_data["session_id"])

        # Update index
        index = manager.update_archive_index()

        assert index["statistics"]["total_sessions"] == 1, "Condition must be true"
        assert index["statistics"]["total_size_mb"] > 0, "Value must be greater than zero"
        assert len(index["sessions"]) == 1, "Collection must not be empty"
        assert index["sessions"][0]["session_id"] == test_session_data["session_id"], "Data must not be empty"

        # Verify index file written
        assert manager.archive_index_path.exists(), "Condition must be true"
        with open(manager.archive_index_path) as f:
            saved_index = json.load(f)
        assert saved_index["statistics"]["total_sessions"] == 1, "Condition must be true"

    def test_purge_old_archives(self, test_db, archive_dir):
        """Test retention policy enforcement."""
        from codex.logging.archive_manager import ArchiveManager

        # Create very old session (far exceeds 30-iteration threshold)
        old_date = (datetime.now() - timedelta(days=1000)).isoformat()
        insert_test_session(
            test_db,
            {
                "session_id": "very-old-session",
                "status": "complete",
                "created_at": old_date,
            },
        )

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        archived = manager.archive_session("very-old-session")

        # Manually set created_at timestamp to trigger purge
        old_ts = (datetime.now() - timedelta(days=1000)).timestamp()

        # Update archive index with old timestamp - use actual archive location
        actual_archive_location = (
            archived.archive_location
            if archived
            else str(archive_dir / "2026" / "03" / "very-old-session.parquet")
        )
        actual_file_size = archived.file_size_bytes if archived else 1000

        index_data = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "sessions": [
                {
                    "session_id": "very-old-session",
                    "archive_location": actual_archive_location,
                    "file_size_bytes": actual_file_size,
                    "timestamp": old_date + "Z",
                    "created_at": str(old_ts),
                }
            ],
            "statistics": {},
        }

        manager.archive_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manager.archive_index_path, "w") as f:
            json.dump(index_data, f)

        # Purge with 30-iteration threshold
        report = manager.purge_old_archives(iterations=30)

        assert len(report["deleted_sessions"]) == 1, "Collection must not be empty"
        # File should be deleted and freed bytes recorded
        assert report["total_bytes_freed"] == actual_file_size or report["total_bytes_freed"] > 0

    def test_archive_integrity(self, test_db, archive_dir, test_session_data):
        """Test archive integrity verification."""
        from codex.logging.archive_manager import ArchiveManager

        insert_test_session(test_db, test_session_data)

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        manager.archive_session(test_session_data["session_id"])

        # Verify archive file is valid Parquet
        archive_path = archive_dir / "2026" / "03" / f"{test_session_data['session_id']}.parquet"
        assert archive_path.exists(), "Condition must be true"

        # Should be able to read it back
        df = pd.read_parquet(str(archive_path))
        assert len(df) == 1, "Df must not be empty"
        assert df.iloc[0]["session_id"] == test_session_data["session_id"], "Data must not be empty"

    def test_non_existent_session_retrieval(self, test_db, archive_dir):
        """Test retrieving non-existent session."""
        from codex.logging.archive_manager import ArchiveManager

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        retrieved = manager.get_archived_session("non-existent-session")

        assert retrieved is None, "retrieved is not valid"

    def test_archive_multiple_sessions(self, test_db, archive_dir):
        """Test archiving multiple sessions."""
        from codex.logging.archive_manager import ArchiveManager

        # Insert multiple sessions
        for i in range(5):
            old_date = (datetime.now() - timedelta(days=100)).isoformat()
            insert_test_session(
                test_db,
                {
                    "session_id": f"session-{i}",
                    "status": "complete",
                    "created_at": old_date,
                },
            )

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))
        candidates = manager.identify_archive_candidates(days=90)

        assert len(candidates) == 5, "Candidates must not be empty"

        # Archive all
        success_count = 0
        for session_id in candidates:
            archived = manager.archive_session(session_id)
            if archived:
                success_count += 1

        assert success_count == 5, "Count must be greater than zero"

        # Verify index
        index = manager.update_archive_index()
        assert index["statistics"]["total_sessions"] == 5, "Condition must be true"


class TestArchiveIntegration:
    """Integration tests for archive system."""

    @pytest.mark.skipif(pd is None, reason="pandas not installed")
    def test_end_to_end_archive_workflow(self, test_db, archive_dir):
        """Test complete archive workflow."""
        from codex.logging.archive_manager import ArchiveManager

        # Setup
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        insert_test_session(
            test_db,
            {
                "session_id": "workflow-test",
                "status": "complete",
                "created_at": old_date,
            },
        )

        manager = ArchiveManager(db_path=str(test_db), archive_dir=str(archive_dir))

        # Step 1: Identify candidates
        candidates = manager.identify_archive_candidates(days=90)
        assert "workflow-test" in candidates, "Condition must be true"

        # Step 2: Archive
        archived = manager.archive_session("workflow-test")
        assert archived is not None, "archived must be initialized"

        # Step 3: Update index
        index = manager.update_archive_index()
        assert index["statistics"]["total_sessions"] == 1, "Condition must be true"

        # Step 4: Retrieve
        retrieved = manager.get_archived_session("workflow-test")
        assert retrieved is not None, "retrieved must be initialized"

        # Step 5: Verify in index
        assert manager.archive_index_path.exists(), "Condition must be true"
        with open(manager.archive_index_path) as f:
            saved_index = json.load(f)
        assert len(saved_index["sessions"]) == 1, "Collection must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
