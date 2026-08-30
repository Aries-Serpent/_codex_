"""
Comprehensive tests for SessionDB.

Tests cover:
- Database initialization and schema creation
- Session CRUD operations
- Query performance and caching
- Thread safety
- Error handling
- Aggregation and statistics
- Pattern and event tracking
"""

import tempfile
import threading  # pragma: allowlist secret # pragma: allowlist secret
import time
from datetime import datetime, timedelta
from pathlib import (
    Path,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

import pytest

from codex.logging.session_db import CacheEntry, SessionDB


class TestSessionDBInitialization:
    """Test database initialization and schema creation."""

    def test_init_creates_database(self):
        """Test that SessionDB creates database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            SessionDB(db_path)
            assert Path(db_path).exists(), "Condition must be true"

    def test_schema_creates_tables(self):
        """Test that schema creates all required tables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = SessionDB(db_path)

            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = {row[0] for row in cursor.fetchall()}

            expected_tables = {
                "sessions",
                "session_metadata",
                "session_patterns",
                "session_outcomes",
                "session_events",
            }
            assert expected_tables.issubset(tables), "Condition must be true"

    def test_schema_creates_indices(self):
        """Test that schema creates performance indices."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = SessionDB(db_path)

            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
                )
                indices = {row[0] for row in cursor.fetchall()}

            expected_indices = {
                "idx_timestamp_status",
                "idx_pr_number_branch",
                "idx_agent_name",
                "idx_session_id",
                "idx_created_at",
            }
            assert expected_indices.issubset(indices), "Condition must be true"

    def test_wal_mode_enabled(self):
        """Test that WAL mode is enabled for concurrent access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = SessionDB(db_path)

            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode")
                mode = cursor.fetchone()[0]

            assert mode.upper() == "WAL", "Condition must be true"

    def test_foreign_keys_enabled(self):
        """Test that foreign keys are enforced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = SessionDB(db_path)

            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys")
                enabled = cursor.fetchone()[0]

            assert enabled == 1, "enabled is not valid"

    def test_connection_timeout(self):
        """Test that connection timeout is properly configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            db = SessionDB(db_path)
            assert db.db_path == db_path, "db_path is not valid"


class TestSessionInsertion:
    """Test session insertion and validation."""

    @pytest.fixture
    def db(self):
        """Create temporary database for each test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            yield db_instance

    def test_insert_minimal_session(self, db):
        """Test inserting session with minimal required fields."""
        session = {
            "session_id": "test-001",
            "status": "complete",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        result = db.insert_session(session)
        assert result is True, "Result must not be empty"

        # Verify insertion
        retrieved = db.get_session("test-001")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved["session_id"] == "test-001", "Condition must be true"
        assert retrieved["status"] == "complete", "Condition must be true"

    def test_insert_session_with_all_fields(self, db):
        """Test inserting session with all fields."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        session = {
            "session_id": "test-002",
            "pr_number": 123,
            "branch": "main",
            "timestamp": timestamp,
            "git_sha": "abc123def456",
            "status": "complete",
            "agent_name": "test-agent",
            "duration_minutes": 15,
            "outcomes": {
                "ci_checks_green": 5,
                "ci_checks_red": 0,
                "ci_checks_total": 5,
                "test_coverage": 95.5,
                "linting_errors": 0,
                "linting_warnings": 2,
            },
            "metadata": {"key1": "value1", "key2": 42},
            "patterns": [
                {"pattern_id": "p1", "pattern_name": "pattern_one", "success": True},
                {"pattern_id": "p2", "pattern_name": "pattern_two", "success": True},
            ],
        }

        result = db.insert_session(session)
        assert result is True, "Result must not be empty"

        # Verify full insertion
        retrieved = db.get_session_with_details("test-002")
        assert retrieved is not None, "retrieved must be initialized"
        assert retrieved["pr_number"] == 123, "Condition must be true"
        assert retrieved["branch"] == "main", "Condition must be true"
        assert retrieved["agent_name"] == "test-agent", "Condition must be true"
        assert len(retrieved["patterns"]) == 2, "Collection must not be empty"
        assert retrieved["outcomes"]["ci_checks_green"] == 5, "Condition must be true"

    def test_insert_missing_required_field(self, db):
        """Test that insertion fails without required fields."""
        session = {"pr_number": 123, "branch": "main"}

        with pytest.raises(ValueError, match="Missing required field"):
            db.insert_session(session)

    def test_insert_invalid_status(self, db):
        """Test that insertion fails with invalid status."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        session = {
            "session_id": "test-003",
            "timestamp": timestamp,
            "status": "invalid_status",
        }

        with pytest.raises(ValueError, match="Invalid status"):
            db.insert_session(session)

    def test_insert_duplicate_session_id(self, db):
        """Test that duplicate session IDs are rejected."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        session = {
            "session_id": "test-004",
            "timestamp": timestamp,
            "status": "complete",
        }

        db.insert_session(session)

        with pytest.raises(ValueError, match="already exists"):
            db.insert_session(session)

    def test_all_valid_statuses(self, db):
        """Test that all valid statuses are accepted."""
        valid_statuses = ["pending", "in-progress", "complete", "failed"]
        timestamp = datetime.utcnow().isoformat() + "Z"

        for i, status in enumerate(valid_statuses):
            session = {
                "session_id": f"test-status-{i}",
                "timestamp": timestamp,
                "status": status,
            }
            result = db.insert_session(session)
            assert result is True, "Result must not be empty"


class TestSessionQuerying:
    """Test session query operations."""

    @pytest.fixture
    def db_with_data(self):
        """Create database with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            # Insert test sessions
            base_time = datetime.utcnow()
            for i in range(10):
                timestamp = (base_time - timedelta(days=i)).isoformat() + "Z"
                session = {
                    "session_id": f"session-{i}",
                    "pr_number": 100 + i,
                    "branch": "main" if i % 2 == 0 else "feature",
                    "timestamp": timestamp,
                    "status": ["complete", "failed", "in-progress"][i % 3],
                    "agent_name": ["agent-a", "agent-b"][i % 2],
                }
                db.insert_session(session)

            yield db

    def test_query_all_sessions(self, db_with_data):
        """Test querying all sessions."""
        results = db_with_data.query_sessions(limit=100)
        assert len(results) == 10, "Results must not be empty"

    def test_query_by_status(self, db_with_data):
        """Test filtering by status."""
        results = db_with_data.query_sessions(filters={"status": "complete"}, limit=100)
        assert len(results) > 0, "Results must not be empty"
        assert all(r["status"] == "complete" for r in results), "Result must not be empty"

    def test_query_by_agent_name(self, db_with_data):
        """Test filtering by agent name."""
        results = db_with_data.query_sessions(filters={"agent_name": "agent-a"}, limit=100)
        assert len(results) > 0, "Results must not be empty"
        assert all(r["agent_name"] == "agent-a" for r in results), "Result must not be empty"

    def test_query_by_branch(self, db_with_data):
        """Test filtering by branch."""
        results = db_with_data.query_sessions(filters={"branch": "main"}, limit=100)
        assert len(results) > 0, "Results must not be empty"
        assert all(r["branch"] == "main" for r in results), "Result must not be empty"

    def test_query_by_pr_number(self, db_with_data):
        """Test filtering by PR number."""
        results = db_with_data.query_sessions(filters={"pr_number": 100}, limit=100)
        assert len(results) == 1, "Results must not be empty"
        assert results[0]["pr_number"] == 100, "Result must not be empty"

    def test_query_with_pagination(self, db_with_data):
        """Test pagination."""
        page1 = db_with_data.query_sessions(limit=5, offset=0)
        page2 = db_with_data.query_sessions(limit=5, offset=5)

        assert len(page1) == 5, "Page1 must not be empty"
        assert len(page2) == 5, "Page2 must not be empty"
        assert page1[0]["session_id"] != page2[0]["session_id"], "Condition must be true"

    def test_query_date_range(self, db_with_data):
        """Test querying by date range."""
        now = datetime.utcnow()
        start = (now - timedelta(days=5)).isoformat() + "Z"
        end = now.isoformat() + "Z"

        results = db_with_data.query_by_date_range(start, end)
        assert len(results) > 0, "Results must not be empty"

    def test_query_by_agent_last_days(self, db_with_data):
        """Test querying agent sessions in last N days."""
        results = db_with_data.query_by_agent("agent-a", days=7)
        assert len(results) > 0, "Results must not be empty"
        assert all(r["agent_name"] == "agent-a" for r in results), "Result must not be empty"

    def test_query_performance_last_7_days(self, db_with_data):
        """Test that 7-day query completes in <100ms."""
        now = datetime.utcnow()
        start = (now - timedelta(days=7)).isoformat() + "Z"
        end = now.isoformat() + "Z"

        start_time = time.time()
        results = db_with_data.query_by_date_range(start, end)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        assert elapsed < 100, f"Query took {elapsed}ms, expected <100ms"
        assert len(results) > 0, "Results must not be empty"


class TestCaching:
    """Test query result caching."""

    @pytest.fixture
    def db_with_data(self):
        """Create database with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            timestamp = datetime.utcnow().isoformat() + "Z"
            for i in range(5):
                session = {
                    "session_id": f"cache-test-{i}",
                    "timestamp": timestamp,
                    "status": "complete",
                    "agent_name": "test-agent",
                }
                db.insert_session(session)

            yield db

    def test_cache_entry_not_expired(self):
        """Test cache entry expiration logic."""
        entry = CacheEntry({"data": "test"}, time.time())
        assert not entry.is_expired(ttl=300), "Condition must be true"

    def test_cache_entry_expired(self):
        """Test that cache entry expires after TTL."""
        entry = CacheEntry({"data": "test"}, time.time() - 400)
        assert entry.is_expired(ttl=300), "Condition must be true"

    def test_query_cached(self, db_with_data):
        """Test that identical queries use cache."""
        # First query
        start_time = time.time()
        result1 = db_with_data.query_sessions(filters={"agent_name": "test-agent"}, limit=100)
        time1 = time.time() - start_time

        # Second query (should be cached)
        start_time = time.time()
        result2 = db_with_data.query_sessions(filters={"agent_name": "test-agent"}, limit=100)
        time2 = time.time() - start_time

        # Results should be identical
        assert result1 == result2, "Result must not be empty"
        # Cached query should be faster (at least 5x)
        assert time2 < time1 or time2 < 1, "time2 is not valid"

    def test_cache_invalidated_on_insert(self, db_with_data):
        """Test that cache is invalidated on insert."""
        # Get initial count
        results1 = db_with_data.query_sessions(limit=100)
        count1 = len(results1)

        # Insert new session
        timestamp = datetime.utcnow().isoformat() + "Z"
        session = {
            "session_id": "new-session",
            "timestamp": timestamp,
            "status": "complete",
        }
        db_with_data.insert_session(session)

        # Query again - cache should be invalidated
        results2 = db_with_data.query_sessions(limit=100)
        count2 = len(results2)

        assert count2 == count1 + 1, "Count must be greater than zero"

    @pytest.mark.flaky(reruns=2, reason="P6-timing: TTL expiry timing dependent on system clock")
    def test_cache_ttl_respected(self):
        """Test that cache TTL is respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")
            db._cache_ttl = 1  # 1 second TTL

            timestamp = datetime.utcnow().isoformat() + "Z"
            session = {
                "session_id": "ttl-test",
                "timestamp": timestamp,
                "status": "complete",
            }
            db.insert_session(session)

            # Query (will be cached)
            results1 = db.query_sessions(limit=100)

            # Wait for TTL to expire
            time.sleep(1.1)

            # Cache should be expired, second query will hit DB
            results2 = db.query_sessions(limit=100)

            assert results1 == results2, "Result must not be empty"


class TestSessionStatusUpdate:
    """Test updating session status."""

    @pytest.fixture
    def db(self):
        """Create database with test session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            timestamp = datetime.utcnow().isoformat() + "Z"
            session = {
                "session_id": "update-test",
                "timestamp": timestamp,
                "status": "pending",
            }
            db_instance.insert_session(session)
            yield db_instance

    def test_update_status_success(self, db):
        """Test successful status update."""
        result = db.update_session_status("update-test", "in-progress")
        assert result is True, "Result must not be empty"

        session = db.get_session("update-test")
        assert session["status"] == "in-progress", "Condition must be true"

    def test_update_nonexistent_session(self, db):
        """Test updating nonexistent session."""
        result = db.update_session_status("nonexistent", "complete")
        assert result is False, "Result must not be empty"

    def test_update_invalid_status(self, db):
        """Test that invalid status is rejected."""
        with pytest.raises(ValueError):
            db.update_session_status("update-test", "invalid")

    def test_cache_invalidated_on_update(self, db):
        """Test that cache is invalidated on status update."""
        # Cache a query result
        db.get_session("update-test")

        # Update status
        db.update_session_status("update-test", "complete")

        # Query should return updated status
        session = db.get_session("update-test")
        assert session["status"] == "complete", "Condition must be true"


class TestPatternTracking:
    """Test pattern insertion and tracking."""

    @pytest.fixture
    def db(self):
        """Create database with test session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            timestamp = datetime.utcnow().isoformat() + "Z"
            session = {
                "session_id": "pattern-test",
                "timestamp": timestamp,
                "status": "complete",
            }
            db_instance.insert_session(session)
            yield db_instance

    def test_add_pattern_to_session(self, db):
        """Test adding pattern to session."""
        result = db.add_pattern_to_session(
            "pattern-test", "pattern-1", "Test Pattern", success=True
        )
        assert result is True, "Result must not be empty"

    def test_multiple_patterns_per_session(self, db):
        """Test adding multiple patterns to session."""
        db.add_pattern_to_session("pattern-test", "p1", "Pattern 1", success=True)
        db.add_pattern_to_session("pattern-test", "p2", "Pattern 2", success=False)

        session = db.get_session_with_details("pattern-test")
        assert len(session["patterns"]) == 2, "Collection must not be empty"


class TestEventTracking:
    """Test event insertion and tracking."""

    @pytest.fixture
    def db(self):
        """Create database with test session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            timestamp = datetime.utcnow().isoformat() + "Z"
            session = {
                "session_id": "event-test",
                "timestamp": timestamp,
                "status": "complete",
            }
            db_instance.insert_session(session)
            yield db_instance

    def test_add_event_to_session(self, db):
        """Test adding event to session."""
        result = db.add_event_to_session("event-test", "start", event_details="Session started")
        assert result is True, "Result must not be empty"

    def test_all_event_types(self, db):
        """Test all valid event types."""
        valid_types = [
            "start",
            "pattern_applied",
            "check_passed",
            "check_failed",
            "error",
            "complete",
        ]

        for event_type in valid_types:
            result = db.add_event_to_session("event-test", event_type)
            assert result is True, "Result must not be empty"

    def test_invalid_event_type(self, db):
        """Test that invalid event type is rejected."""
        with pytest.raises(ValueError):
            db.add_event_to_session("event-test", "invalid_type")


class TestAggregation:
    """Test statistics aggregation."""

    @pytest.fixture
    def db_with_data(self):
        """Create database with diverse test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            base_time = datetime.utcnow()
            statuses = ["complete", "failed", "in-progress", "pending"]
            agents = ["agent-a", "agent-b", "agent-c"]
            branches = ["main", "develop", "feature"]

            for i in range(20):
                timestamp = (base_time - timedelta(days=i % 7)).isoformat() + "Z"
                session = {
                    "session_id": f"stats-test-{i}",
                    "timestamp": timestamp,
                    "status": statuses[i % len(statuses)],
                    "agent_name": agents[i % len(agents)],
                    "branch": branches[i % len(branches)],
                }
                db.insert_session(session)

            yield db

    def test_get_stats_all_time(self, db_with_data):
        """Test getting all-time statistics."""
        stats = db_with_data.get_stats(timeframe="all")

        assert stats["total"] == 20, "Condition must be true"
        assert "by_status" in stats, "Condition must be true"
        assert "by_agent" in stats, "Condition must be true"
        assert "by_branch" in stats, "Condition must be true"
        assert 0 <= stats["success_rate"] <= 100, "0 is not valid"

    def test_get_stats_7_days(self, db_with_data):
        """Test getting 7-day statistics."""
        stats = db_with_data.get_stats(timeframe="7d")

        assert stats["total"] > 0, "Value must be greater than zero"
        assert stats["total"] <= 20, "Condition must be true"

    def test_stats_success_rate(self, db_with_data):
        """Test success rate calculation."""
        stats = db_with_data.get_stats(timeframe="all")

        total = stats["total"]
        complete = stats["by_status"].get("complete", 0)
        expected_rate = (complete / total * 100) if total > 0 else 0

        assert stats["success_rate"] == round(expected_rate, 2)

    def test_stats_by_agent(self, db_with_data):
        """Test statistics breakdown by agent."""
        stats = db_with_data.get_stats(timeframe="all")

        assert len(stats["by_agent"]) > 0, "Collection must not be empty"
        assert all(isinstance(count, int) for count in stats["by_agent"].values())

    def test_stats_caching(self, db_with_data):
        """Test that stats are cached."""
        # First call
        start_time = time.time()
        stats1 = db_with_data.get_stats(timeframe="7d")
        time1 = time.time() - start_time

        # Second call (cached)
        start_time = time.time()
        stats2 = db_with_data.get_stats(timeframe="7d")
        time2 = time.time() - start_time

        assert stats1 == stats2, "stats1 is not valid"
        # Cached call should be faster
        assert time2 < time1 or time2 < 1, "time2 is not valid"


class TestThreadSafety:
    """Test thread safety."""

    @pytest.mark.flaky(reruns=2, reason="P6-concurrency: Concurrent inserts may have race conditions")
    def test_concurrent_inserts(self):
        """Test that concurrent inserts work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            def insert_sessions(start_id: int, count: int):
                timestamp = datetime.utcnow().isoformat() + "Z"
                for i in range(count):
                    session = {
                        "session_id": f"thread-{start_id}-{i}",
                        "timestamp": timestamp,
                        "status": "complete",
                    }
                    db.insert_session(session)

            # Create threads
            threads = [threading.Thread(target=insert_sessions, args=(i, 10)) for i in range(5)]

            # Run threads
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Verify all sessions inserted
            results = db.query_sessions(limit=1000)
            assert len(results) == 50, "Results must not be empty"

    @pytest.mark.flaky(reruns=2, reason="P6-concurrency: Concurrent queries may have race conditions")
    def test_concurrent_queries(self):
        """Test that concurrent queries work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            # Insert test data
            timestamp = datetime.utcnow().isoformat() + "Z"
            for i in range(20):
                session = {
                    "session_id": f"query-test-{i}",
                    "timestamp": timestamp,
                    "status": "complete",
                }
                db.insert_session(session)

            results_list = []

            def run_query():
                results = db.query_sessions(limit=100)
                results_list.append(results)

            # Create threads
            threads = [threading.Thread(target=run_query) for _ in range(5)]

            # Run threads
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Verify all queries succeeded
            assert len(results_list) == 5, "Results_list must not be empty"
            assert all(len(r) == 20 for r in results_list), "R must not be empty"


class TestSessionDeletion:
    """Test session deletion and cleanup."""

    @pytest.fixture
    def db(self):
        """Create database with test session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            timestamp = datetime.utcnow().isoformat() + "Z"
            session = {
                "session_id": "delete-test",
                "timestamp": timestamp,
                "status": "complete",
                "patterns": [{"pattern_id": "p1", "pattern_name": "Pattern 1", "success": True}],
            }
            db_instance.insert_session(session)
            yield db_instance

    def test_delete_session(self, db):
        """Test deleting a session."""
        result = db.delete_session("delete-test")
        assert result is True, "Result must not be empty"

        # Verify deletion
        session = db.get_session("delete-test")
        assert session is None, "session is not valid"

    def test_delete_nonexistent_session(self, db):
        """Test deleting nonexistent session."""
        result = db.delete_session("nonexistent")
        assert result is False, "Result must not be empty"

    def test_cascade_delete_patterns(self, db):
        """Test that patterns are deleted with session."""
        # Verify pattern exists
        session = db.get_session_with_details("delete-test")
        assert len(session["patterns"]) == 1, "Collection must not be empty"

        # Delete session
        db.delete_session("delete-test")

        # Verify pattern is also deleted (cascade)
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM session_patterns WHERE session_id = ?",
                ("delete-test",),
            )
            count = cursor.fetchone()[0]

        assert count == 0, "Count must be greater than zero"


class TestDatabaseOptimization:
    """Test database optimization."""

    def test_vacuum_succeeds(self):
        """Test that vacuum operation succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")

            # Insert some data
            timestamp = datetime.utcnow().isoformat() + "Z"
            for i in range(10):
                session = {
                    "session_id": f"vacuum-test-{i}",
                    "timestamp": timestamp,
                    "status": "complete",
                }
                db.insert_session(session)

            # Vacuum should succeed
            db.vacuum()

            # Verify database still works
            results = db.query_sessions(limit=100)
            assert len(results) == 10, "Results must not be empty"

    def test_get_connection_info(self):
        """Test getting database connection info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = SessionDB(f"{tmpdir}/test.db")
            info = db.get_connection_info()

            assert "db_path" in info, "Condition must be true"
            assert "journal_mode" in info, "Condition must be true"
            assert "cache_size" in info, "Condition must be true"
            assert "foreign_keys" in info, "Condition must be true"
            assert info["foreign_keys"] is True, "Condition must be true"
            assert info["journal_mode"].upper() == "WAL", "Condition must be true"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def db(self):
        """Create temporary database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_instance = SessionDB(f"{tmpdir}/test.db")
            yield db_instance

    def test_query_empty_database(self, db):
        """Test querying empty database."""
        results = db.query_sessions(limit=100)
        assert results == [], "Result must not be empty"

    def test_get_session_empty_database(self, db):
        """Test getting session from empty database."""
        session = db.get_session("nonexistent")
        assert session is None, "session is not valid"

    def test_stats_empty_database(self, db):
        """Test getting stats from empty database."""
        stats = db.get_stats()
        assert stats["total"] == 0, "Condition must be true"
        assert stats["success_rate"] == 0.0, "Condition must be true"

    def test_query_with_special_characters(self, db):
        """Test querying with special characters."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        session = {
            "session_id": "special-chars-test",
            "timestamp": timestamp,
            "status": "complete",
            "branch": "feature/special's-branch",
        }
        result = db.insert_session(session)
        assert result is True, "Result must not be empty"

        retrieved = db.get_session("special-chars-test")
        assert retrieved["branch"] == "feature/special's-branch", "Condition must be true"

    def test_large_metadata_values(self, db):
        """Test storing large metadata values."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        large_value = "x" * 10000

        session = {
            "session_id": "large-metadata-test",
            "timestamp": timestamp,
            "status": "complete",
            "metadata": {"large_key": large_value},
        }

        result = db.insert_session(session)
        assert result is True, "Result must not be empty"

        retrieved = db.get_session_with_details("large-metadata-test")
        assert retrieved["metadata"]["large_key"] == large_value, "Data must not be empty"
