"""
SessionQueryBuilder: Session querying and filtering operations.

Provides:
- Flexible session querying with filters
- Date range queries
- Agent-specific queries
- Status-based queries
- Query caching and performance optimization
"""

import time
from datetime import datetime, timedelta
from typing import Any, Optional

from .session_database import CacheEntry, SessionDatabase


class SessionQueryBuilder:
    """
    Query builder for session database operations.

    Provides:
    - Flexible querying with optional filters
    - Performance-optimized queries using indices
    - Result caching with configurable TTL
    - Pagination support
    """

    def __init__(self, db: SessionDatabase) -> None:
        """
        Initialize query builder with database instance.

        Args:
            db: SessionDatabase instance for executing queries
        """
        self.db = db

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
        cache_key = f"query_{str(filters)}_{limit}_{offset}"

        # Check cache
        with self.db._lock:
            if cache_key in self.db._cache:
                entry = self.db._cache[cache_key]
                if not entry.is_expired(self.db._cache_ttl):
                    return entry.data

        filters = filters or {}
        where_clauses = []
        params = []

        # Build WHERE clause dynamically
        if "status" in filters:
            where_clauses.append("status = ?")
            params.append(filters["status"])

        if "agent_name" in filters:
            where_clauses.append("agent_name = ?")
            params.append(filters["agent_name"])

        if "branch" in filters:
            where_clauses.append("branch = ?")
            params.append(filters["branch"])

        if "pr_number" in filters:
            where_clauses.append("pr_number = ?")
            params.append(filters["pr_number"])

        if "start_time" in filters:
            where_clauses.append("timestamp >= ?")
            params.append(filters["start_time"])

        if "end_time" in filters:
            where_clauses.append("timestamp <= ?")
            params.append(filters["end_time"])

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
            SELECT * FROM sessions
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """  # nosec B608 - where_clause is built from safe values
        params.extend([limit, offset])

        with self.db._lock:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]

            # Cache result
            self.db._cache[cache_key] = CacheEntry(results, time.time())

        return results

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
        return self.query_sessions(
            filters={"start_time": start_dt, "end_time": end_dt}, limit=limit
        )

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
        start_dt = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        end_dt = datetime.utcnow().isoformat() + "Z"

        return self.query_sessions(
            filters={"agent_name": agent_name, "start_time": start_dt, "end_time": end_dt},
            limit=1000,
        )

    def query_by_status(self, status: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Query sessions by status.

        Args:
            status: Session status ('pending', 'in-progress', 'complete', 'failed')
            limit: Maximum results

        Returns:
            List of sessions with specified status.
        """
        valid_statuses = {"pending", "in-progress", "complete", "failed"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")

        return self.query_sessions(filters={"status": status}, limit=limit)
