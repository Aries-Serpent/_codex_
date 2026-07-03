"""
SessionDB: Facade for session database operations.

Composes specialized modules for:
- Database operations (SessionDatabase)
- Query building (SessionQueryBuilder)
- Analytics (SessionAnalytics)
- Pattern/event recording (PatternEventRecorder)

Maintains backward compatibility with existing public API.
"""

from typing import Any, Optional

from .pattern_event_recorder import PatternEventRecorder
from .session_analytics import SessionAnalytics

# Re-export CacheEntry for backward compatibility
from .session_database import (
    CacheEntry,  # noqa: F401
    SessionDatabase,
)
from .session_query_builder import SessionQueryBuilder


class SessionDB:
    """
    SQLite backend for session tracking with optimized query performance.

    Facade that composes specialized modules for:
    - Core database operations (SessionDatabase)
    - Session querying (SessionQueryBuilder)
    - Analytics and statistics (SessionAnalytics)
    - Pattern and event recording (PatternEventRecorder)

    Implements:
    - O(log n) queries through strategic indexing
    - Thread-safe connection pooling
    - Automatic result caching (5-minute TTL)
    - Transaction support (ACID compliance)
    - Foreign key constraint enforcement
    - Query result validation
    """

    def __init__(self, db_path: str = ".codex/sessions.db") -> None:
        """
        Initialize database facade and submodules.

        Args:
            db_path: Path to SQLite database file. Created if doesn't exist.

        Raises:
            sqlite3.Error: If schema initialization fails.
        """
        self.db_path = db_path

        # Initialize specialized modules
        self._database = SessionDatabase(db_path)
        self._query_builder = SessionQueryBuilder(self._database)
        self._analytics = SessionAnalytics(self._database)
        self._recorder = PatternEventRecorder(self._database)

        # Expose internal references for backward compatibility
        self._lock = self._database._lock
        self._cache = self._database._cache
        self._cache_ttl = self._database._cache_ttl

    def _get_connection(self):
        """Get database connection (for backward compatibility)."""
        return self._database._get_connection()

    def _ensure_schema(self) -> None:
        """Ensure database schema (for backward compatibility)."""
        self._database._ensure_schema()

    def _create_inline_schema(self) -> None:
        """Create inline schema (for backward compatibility)."""
        self._database._create_inline_schema()

    def _optimize_db(self) -> None:
        """Optimize database (for backward compatibility)."""
        self._database._optimize_db()

    def _invalidate_cache(self) -> None:
        """Clear all cached query results (for backward compatibility)."""
        self._database._invalidate_cache()

    def insert_session(self, session: dict[str, Any]) -> bool:
        """
        Insert new session into database.

        Args:
            session: Dictionary with keys: session_id, pr_number, branch,
                    timestamp, git_sha, status, agent_name, duration_minutes

        Returns:
            bool: True if insertion successful, False otherwise.

        Raises:
            ValueError: If required fields missing or invalid.
            sqlite3.IntegrityError: If session_id already exists.
        """
        return self._database.insert_session(session)

    def query_sessions(
        self, filters: Optional[dict[str, Any]] = None, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Query sessions with optional filters.

        Args:
            filters: Dictionary with optional filter keys:
                    - status: session status
                    - agent_name: filter by agent
                    - branch: filter by git branch
                    - pr_number: filter by PR number
                    - start_time: ISO 8601 timestamp
                    - end_time: ISO 8601 timestamp
            limit: Maximum results to return (default: 100)
            offset: Pagination offset (default: 0)

        Returns:
            List of session dictionaries matching filters.

        Performance:
            - O(log n) with proper indices on filter fields
            - Typical 7-day query: <100ms
        """
        return self._query_builder.query_sessions(filters, limit, offset)

    def query_by_date_range(
        self, start_dt: str, end_dt: str, limit: int = 1000
    ) -> list[dict[str, Any]]:
        """
        Query sessions within date range (ISO 8601 format).

        Args:
            start_dt: Start timestamp (ISO 8601, e.g., '2026-06-16T02:34:59Z')
            end_dt: End timestamp (ISO 8601)
            limit: Maximum results (default: 1000)

        Returns:
            List of sessions in date range ordered by timestamp DESC.

        Performance:
            - Uses index: idx_timestamp_status
            - 7-day query typically <100ms
        """
        return self._query_builder.query_by_date_range(start_dt, end_dt, limit)

    def query_by_agent(self, agent_name: str, days: int = 7) -> list[dict[str, Any]]:
        """
        Query sessions for specific agent in last N days.

        Args:
            agent_name: Name of the agent
            days: Number of days to look back (default: 7)

        Returns:
            List of sessions for the agent.

        Performance:
            - Uses index: idx_agent_name
            - Typical query <50ms
        """
        return self._query_builder.query_by_agent(agent_name, days)

    def query_by_status(self, status: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Query sessions by status.

        Args:
            status: Session status ('pending', 'in-progress', 'complete', 'failed')
            limit: Maximum results

        Returns:
            List of sessions with specified status.
        """
        return self._query_builder.query_by_status(status, limit)

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get single session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session dictionary or None if not found.

        Performance:
            - O(1) lookup via PRIMARY KEY
        """
        return self._database.get_session(session_id)

    def get_session_with_details(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get session with all related details (metadata, patterns, outcomes, events).

        Args:
            session_id: Unique session identifier

        Returns:
            Session dictionary with nested details or None if not found.
        """
        return self._database.get_session_with_details(session_id)

    def update_session_status(self, session_id: str, new_status: str) -> bool:
        """
        Update session status.

        Args:
            session_id: Session identifier
            new_status: New status value

        Returns:
            True if update successful, False if session not found.

        Raises:
            ValueError: If status invalid.
        """
        return self._database.update_session_status(session_id, new_status)

    def get_stats(self, timeframe: str = "7d") -> dict[str, Any]:
        """
        Get aggregated statistics for sessions.

        Args:
            timeframe: Time period ('24h', '7d', '30d', 'all')

        Returns:
            Dictionary with statistics:
            {
                'total': int,
                'by_status': {'pending': int, ...},
                'by_agent': {'agent_name': int, ...},
                'by_branch': {'branch': int, ...},
                'success_rate': float
            }
        """
        return self._analytics.get_stats(timeframe)

    def add_pattern_to_session(
        self, session_id: str, pattern_id: str, pattern_name: str, success: bool = True
    ) -> bool:
        """
        Add a pattern record to a session.

        Args:
            session_id: Session identifier
            pattern_id: Pattern identifier
            pattern_name: Human-readable pattern name
            success: Whether pattern was successfully applied

        Returns:
            True if added successfully.
        """
        return self._recorder.add_pattern_to_session(session_id, pattern_id, pattern_name, success)

    def add_event_to_session(
        self, session_id: str, event_type: str, event_details: Optional[str] = None
    ) -> bool:
        """
        Add an event record to a session.

        Args:
            session_id: Session identifier
            event_type: Type of event ('start', 'pattern_applied', 'check_passed', 'check_failed', 'error', 'complete')
            event_details: Optional detailed information about event

        Returns:
            True if added successfully.

        Raises:
            ValueError: If event_type invalid.
        """
        return self._recorder.add_event_to_session(session_id, event_type, event_details)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session and all related data.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully, False if not found.
        """
        return self._database.delete_session(session_id)

    def vacuum(self) -> None:
        """Optimize database size and performance."""
        self._database.vacuum()

    def get_connection_info(self) -> dict[str, Any]:
        """Get information about database connection and settings."""
        return self._database.get_connection_info()
